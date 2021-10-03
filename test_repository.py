# pylint: disable=protected-access
import model
import repository

# Repository가 batch 저장할 수 있는지?
def test_repository_can_save_a_batch(session):
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    # 아.. 보니까 session은 pytest에서 DI 해 주는 것 같다.
    repo = repository.SqlAlchemyRepository(session)
    #Repository에 저장하고
    repo.add(batch)
    session.commit()

    # 꺼내 오면
    rows = session.execute(
        'SELECT reference, sku, _purchased_quantity, eta FROM "batches"'
    )
    # 같은 batch이다.
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]


# OrderLine 넣는 함수
def insert_order_line(session):
    session.execute(
        "INSERT INTO order_lines (orderid, sku, qty)"
        ' VALUES ("order1", "GENERIC-SOFA", 12)'
    )


    # [1]
    # session.execute 결과는 sqlalchemy.engine.cursor.CursorResult 인 것 같다.
    # 아래와 같이 썼을 때, orderline_id의 값은 1이다.
    # 1은 row의 값인 것 같긴 한데, 확실치 않아 session.execute를 복사해서 하나 더 실행한 값을 봤더니 2가 나왔다.
    # 음.. orderline_id는 확실히 row 번호인 것 같다.

    # 근데 [[]]는 몰까??
    # https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.CursorResult 문서를 보니 .alL() 메소드가 있다.
    # 그래서 orderLine.all() 값을 봤더니 [(1,)]이다. 아마 [[orderline_id]] 는 저걸 변수로 추출해내는 문법인 것 같은데, Python Unpacking 같은 걸로 찾아봐도 안 나온다.
    # (a,b,c) = (1,2,3) 같은 예제를 찾긴 했는데, 그러면 구조만 똑같이 해 주면 되나? 싶어서 [[a,b]] = [(a,b)] 로 해보니까 추출이 잘 된다.
    # 음 ㅇㅋ 이해했다
    [[orderline_id]] = session.execute(
        # orderid = "order1", sku = GENERIC-SOFA 가 있는 dictionary 자료형으로 넘겨준다.
        # orderid가 key, "order1"이 값인 것 같다.
        "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
        dict(orderid="order1", sku="GENERIC-SOFA"),
    )
    return orderline_id

# 위의 [1] 타입이 궁금해서 만들어본 테스트
def test_insert_order_line_type(session):
    data = insert_order_line(session)
    # 주석 지우고, test 실패시킨 후 pytest가 찍어주는 값 봤다.
    # assert data == "aaaa"

# batch를 insert하는 함수
def insert_batch(session, batch_id):
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        ' VALUES (:batch_id, "GENERIC-SOFA", 100, null)',
        dict(batch_id=batch_id),
    )
    [[batch_id]] = session.execute(
        'SELECT id FROM batches WHERE reference=:batch_id AND sku="GENERIC-SOFA"',
        dict(batch_id=batch_id),
    )
    return batch_id

# allocation insert 하는 함수
def insert_allocation(session, orderline_id, batch_id):
    session.execute(
        "INSERT INTO allocations (orderline_id, batch_id)"
        " VALUES (:orderline_id, :batch_id)",
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )

# allocation이 있는 batch를 repository가 가져올 수 있는지?
def test_repository_can_retrieve_a_batch_with_allocations(session):
    # 이건 수동으로 order_line, batch, allocation 넣어준 것

    # orderLine = VALUES ("order1", "GENERIC-SOFA", 12)
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, "batch1")
    insert_batch(session, "batch2")
    insert_allocation(session, orderline_id, batch1_id)

    #Repository에서 batch1 가져온다.
    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get("batch1")

    expected = model.Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected  # Batch.__eq__ only compares reference
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {
        model.OrderLine("order1", "GENERIC-SOFA", 12),
    }
