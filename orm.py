from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import mapper, relationship

# ORM이 Model을 Import하니, ORM이 Model에 의존한다!
import model

# 잘 모르겠지만 Metadata 관련된 내용 같다.
metadata = MetaData()

# Order_lines는 orderID, SKU, Quantity로 구성된다.
order_lines = Table(
    # 이게 Table 명
    "order_lines",
    # MetaData, 근데 항상 같은 Parameter 들어갈거면 지워도 되지 않나?
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    # SKU도 Nullable하면 안 될 것 같은데, Quantity만 Nullable하다. 왤까?
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
)


# Batches는 Ref(ID), SKU, ETA(도착시간), Quantity, _allocations(Set) 으로 구성되어 있다. 
batches = Table(
    "batches",
    metadata,
    #Reference와 별도로 ID를 저장하는군.. 
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    # _purchased_quantity 를 Object에서는 함수로 구현했는데, 여기서는 값으로 집어넣는구나.
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

# Allocation은 객체에서는 Batches 내의 Set이었는데, 여기서는 중간 테이블 이용해 구현한 것 같다.
allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    # FK를 얘가 가지고 있네.. JPA 할때 연관관계의 주인? 같은 개념이 있었던 것 같은데 얘도 그런게 있으려나?
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)

# Mapping 하는 함수인 것 같다.
def start_mappers():
    # OrderLine은 값 객체니까 그냥 Mapping하는 것 같다.
    lines_mapper = mapper(model.OrderLine, order_lines)
    
    # 그리고 Batchs는 
    mapper(
        model.Batch,
        batches,
        # properties 중 _allocation Set을
        properties={
            # 잘 모르겠지만 relationShip이라는 함수 호출해서, lines_mapper 통해 lines 저장하고,
            # 이걸 allocations라는 중간 테이블 통해 매핑하는 것 같다.
            "_allocations": relationship(
                lines_mapper, secondary=allocations, collection_class=set,
            )
        },
    )
