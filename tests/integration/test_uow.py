import pytest
from allocation.domain import model
from allocation.service_layer import unit_of_work


def insert_batch(session, ref, sku, qty, eta):
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
    # Batch랑 allocations(중간 테이블) Join해서, Batch ref 가져온다.
    [[batchref]] = session.execute(
        "SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id"
        " WHERE orderline_id=:orderlineid",
        dict(orderlineid=orderlineid),
    )
    return batchref

# UoW가 batch를 가져오고, allocate 할 수 있는지?
def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch(session, "batch1", "HIPSTER-WORKBENCH", 100, None)
    session.commit()

    # 커스텀 세션 팩토리 (In-Memory DB)를 이용해 UoW를 통합, 블록 안에서 사용할 UoW 객체를 얻는다.
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        batch = uow.batches.get(reference="batch1") # uow.batches를 통해 배치 저장소에 대한 접근을 제공
        line = model.OrderLine("o1", "HIPSTER-WORKBENCH", 10)
        batch.allocate(line)
        uow.commit() # 작업이 끝났을 때, uow에 대한 commit을 호출


    batchref = get_allocated_batch_ref(session, "o1", "HIPSTER-WORKBENCH")
    assert batchref == "batch1"

# Commit 안 된 work에 대해 rollback 할 수 있는지?
def test_rolls_back_uncommitted_work_by_default(session_factory):
    # session-factory는 SQLite이다!
    # 실제로는, 실제 사용할 DB (여기서는 Postgres) 에 대해 테스트 할 필요 있다.
    # 7장에서 일부 테스트를 실제 DB로 바꿀 때, uow가 유용하다.
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_batch(uow.session, "batch1", "MEDIUM-PLINTH", 100, None)
        # commit이 없다!

    # 실제로 저장됐는지 확인하기 위해, 새로운 Session을 발급받는다..
    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    # Rollback되었으므로, rows에는 데이터가 없어야 한다.
    assert rows == []

# Exception 발생했을 때, Commit 되지 않고 Rollback 되어야 한다.
def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            insert_batch(uow.session, "batch1", "LARGE-FORK", 100, None)
            raise MyException()
            # Exception 발생했다!

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM "batches"'))
    assert rows == []
