import model
from datetime import date

# Orderline Mapper가 Orderline을 Load 할 수 있는지?
def test_orderline_mapper_can_load_lines(session):
    # DB에 order라인 세개 넣어놓고
    session.execute(
        "INSERT INTO order_lines (orderid, sku, qty) VALUES "
        '("order1", "RED-CHAIR", 12),'
        '("order1", "RED-TABLE", 13),'
        '("order2", "BLUE-LIPSTICK", 14)'
    )
    
    # expected : OrderLine 객체
    expected = [
        model.OrderLine("order1", "RED-CHAIR", 12),
        model.OrderLine("order1", "RED-TABLE", 13),
        model.OrderLine("order2", "BLUE-LIPSTICK", 14),
    ]
    # session.query(model.OrderLine).all() 하면 DB에 있는 모든 OrderLine을 가져오나?
    assert session.query(model.OrderLine).all() == expected

# Orderline Mapper가 line을 저장할 수 있는지?
def test_orderline_mapper_can_save_lines(session):
    new_line = model.OrderLine("order1", "DECORATIVE-WIDGET", 12)
    session.add(new_line)
    session.commit()

    rows = list(session.execute('SELECT orderid, sku, qty FROM "order_lines"'))
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]

# batch를 되찾아 올 수 있는지?
def test_retrieving_batches(session):
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        ' VALUES ("batch1", "sku1", 100, null)'
    )
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        ' VALUES ("batch2", "sku2", 200, "2011-04-11")'
    )
    expected = [
        model.Batch("batch1", "sku1", 100, eta=None),
        model.Batch("batch2", "sku2", 200, eta=date(2011, 4, 11)),
    ]

    assert session.query(model.Batch).all() == expected

# Batch를 저장할 수 있는지?
def test_saving_batches(session):
    batch = model.Batch("batch1", "sku1", 100, eta=None)
    session.add(batch)
    session.commit()
    rows = session.execute(
        'SELECT reference, sku, _purchased_quantity, eta FROM "batches"'
    )
    # ()는 Tuple이라는 자료구조이다. SELECT 쿼리 날리면 Tuple로 리턴하는 것 같다.
    # 아마 Tuple이 수정 불가하니 Tuple로 주는 것 같다.
    assert list(rows) == [("batch1", "sku1", 100, None)]

# allocation이 저장 되는지 확인해 본다. (중간 Table!)
def test_saving_allocations(session):
    batch = model.Batch("batch1", "sku1", 100, eta=None)
    line = model.OrderLine("order1", "sku1", 10)
    # Batch에 line을 allocate하고
    batch.allocate(line)
    # ORM 통해 DB에 넣으면?
    session.add(batch)
    session.commit()
    # batch1, order1를 FK로 가지는 중간 테이블이 생길 것이다.
    rows = list(session.execute('SELECT orderline_id, batch_id FROM "allocations"'))
    assert rows == [(batch.id, line.id)]

# allocation 찾아올 수 있는지?
def test_retrieving_allocations(session):
    # orderline에 하나 넣는다.
    session.execute(
        'INSERT INTO order_lines (orderid, sku, qty) VALUES ("order1", "sku1", 12)'
    )
    # ??
    # 
    [[olid]] = session.execute(
        "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
        dict(orderid="order1", sku="sku1"),
    )
    # 
    session.execute(
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        ' VALUES ("batch1", "sku1", 100, null)'
    )
    [[bid]] = session.execute(
        "SELECT id FROM batches WHERE reference=:ref AND sku=:sku",
        dict(ref="batch1", sku="sku1"),
    )
    session.execute(
        "INSERT INTO allocations (orderline_id, batch_id) VALUES (:olid, :bid)",
        dict(olid=olid, bid=bid),
    )

    batch = session.query(model.Batch).one()

    assert batch._allocations == {model.OrderLine("order1", "sku1", 12)}
