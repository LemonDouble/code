# pylint: disable=broad-except
import threading
import time
import traceback
from typing import List
import pytest
from allocation.domain import model
from allocation.service_layer import unit_of_work
from ..random_refs import random_sku, random_batchref, random_orderid


def insert_batch(session, ref, sku, qty, eta, product_version=1):
    session.execute(
        "INSERT INTO products (sku, version_number) VALUES (:sku, :version)",
        dict(sku=sku, version=product_version),
    )
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        " VALUES (:ref, :sku, :qty, :eta)",
        dict(ref=ref, sku=sku, qty=qty, eta=eta),
    )


def get_allocated_batch_ref(session, orderid, sku):
    [[orderlineid]] = session.execute(
        "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
        dict(orderid=orderid, sku=sku),
    )
    [[batchref]] = session.execute(
        "SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id"
        " WHERE orderline_id=:orderlineid",
        dict(orderlineid=orderlineid),
    )
    return batchref


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch(session, "batch1", "HIPSTER-WORKBENCH", 100, None)
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        product = uow.products.get(sku="HIPSTER-WORKBENCH")
        line = model.OrderLine("o1", "HIPSTER-WORKBENCH", 10)
        product.allocate(line)
        uow.commit()

    batchref = get_allocated_batch_ref(session, "o1", "HIPSTER-WORKBENCH")
    assert batchref == "batch1"


def test_rolls_back_uncommitted_work_by_default(session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_batch(uow.session, "batch1", "MEDIUM-PLINTH", 100, None)

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            insert_batch(uow.session, "batch1", "LARGE-FORK", 100, None)
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []

# 할당한 다음 의도적으로 Sleep하는 함수, 느린 Transaction을 시뮬레이션한다.
def try_to_allocate(orderid, sku, exceptions):
    line = model.OrderLine(orderid, sku, 10)
    try:
        with unit_of_work.SqlAlchemyUnitOfWork() as uow:
            product = uow.products.get(sku=sku)
            product.allocate(line)
            time.sleep(0.2)
            uow.commit()
    except Exception as e:
        # Exception이 발생하면, exceptions 리스트에 넣는다.
        print(traceback.format_exc())
        exceptions.append(e)

# 궁금한 점 : 버전을 사용하는 코드가 없는 것 같은데?
def test_concurrent_updates_to_version_are_not_allowed(postgres_session_factory):
    sku, batch = random_sku(), random_batchref()
    session = postgres_session_factory()
    # Batch를 미리 넣는다.
    insert_batch(session, batch, sku, 100, eta=None, product_version=1)
    session.commit()

    # 랜덤한 ORDER ID 두개 생성한 후
    order1, order2 = random_orderid(1), random_orderid(2)
    exceptions = []  # type: List[Exception]

    # 위에서 생성한 느린 Transaction을 통해 Race Condition 구현한다.
    try_to_allocate_order1 = lambda: try_to_allocate(order1, sku, exceptions)
    try_to_allocate_order2 = lambda: try_to_allocate(order2, sku, exceptions)
    thread1 = threading.Thread(target=try_to_allocate_order1)
    thread2 = threading.Thread(target=try_to_allocate_order2)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # 이후에 Product에서 버전 가져온다.
    [[version]] = session.execute(
        "SELECT version_number FROM products WHERE sku=:sku",
        dict(sku=sku),
    )

    # 최초 버전이 1이었으니, 버전이 2일 것이라고 예상한다.
    assert version == 2
    
    # 이 Exception은 postgreSQL의 Exception이다.
    # isolation Level이 REPEATABLE READ일때 발생, READ COMMITTED라면 발생되지 않는다.
    # 만약, Allocation Table만 업데이트 했다면 이 Exception이 발생하지 않았을 것이다.
    # 하지만 강제로 Product의 version을 업데이트하도록 하였으므로, 한 트랜잭션은 업데이트에 실패하게 된다.
    [exception] = exceptions
    assert "could not serialize access due to concurrent update" in str(exception)


    orders = session.execute(
        "SELECT orderid FROM allocations"
        " JOIN batches ON allocations.batch_id = batches.id"
        " JOIN order_lines ON allocations.orderline_id = order_lines.id"
        " WHERE order_lines.sku=:sku",
        dict(sku=sku),
    )
    # 할당 중 하나만 제대로 되었음을 확인
    assert orders.rowcount == 1
    with unit_of_work.SqlAlchemyUnitOfWork() as uow:
        uow.session.execute("select 1")
