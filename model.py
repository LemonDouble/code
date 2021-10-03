from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set

# Model 정의

# 제품(Product) : SKU라는 식별자로 식별, 예시 : RED-CHAIR

# 주문 : 주문 참조 번호(Order Reference) 로 식별, 한 줄 이상의 주문 라인 (Order Line) 포함
# 주문 라인 : SKU와 수량이 있음. (eg > RED-CHAIR 10단위)

# 배치(Batch) : ID(Reference), SKU, 수량으로 이루어짐.

# 배치에는 주문을 할당 가능, 배치에 주문을 할당하면 배치의 잔여 수량이 줄어든다.
# 예를 들어 배치가 20개 가지고 있을 때, 2짜리 주문 할당하면 18이 된다.
# 1. 하지만 배치에 남은 재고보다 주문 수량이 많다면 할당이 불가능하다.
# 2. 또한, 한 배치에 같은 주문을 두 번 이상 할당해서는 안 된다.
# 예를 들어, 10단위 BLUE-BASE라는 배치에 같은 1번 배치를 두번 할당해도 배치의 가용 재고 수량은 계속 8개여야 한다.

# 배치가 현재 운송 중이면 ETA 정보가 배치에 들어 있다.
# ETA가 없는 배치는 창고 재고다.
# 창고 재고는 배송 중인 배치보다 더 먼저 할당해야 한다.
# 만약 배송 중인 배치를 할당하는 경우, ETA가 가장 빠른 배치를 먼저 할당해야 한다.

#재고 없음 Exception 
class OutOfStock(Exception):
    pass

def get_earliest_batch( line : OrderLine, batches : List[Batch] ):
    return next(b for b in sorted(batches) if b.can_allocate(line))

# line : OrderLine 같은 건 파라미터 타입 힌트,
# -> str은 리턴 타입 힌트

# OrderLine과 Batch List를 주면 가장 빠른 Batch에 Order를 할당하고, batch의 Reference (ID)를 리턴한다.
def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = get_earliest_batch(line, batches)
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")

# OrderLine은 ID, SKU, 수량으로 구성,
# @dataclass : __init__ , __repr__ , __eq__ 와 같은 메서드를 자동으로 생성해 줌
# __init__ : 초기화 메서드? 생성자
# __repr__ : 사용자가 객체를 이해할 수 있게 해 준다? 객체를 인간이 이해할 수 있는 평문으로 "표현"한다고 한다.
# print로 찍으면 __repr__ 이 return하는 String이 출력된다.
# __eq__ : 두 값을 비교할 때 쓰는 메서드
@dataclass(unsafe_hash=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations = set()  # type: Set[OrderLine]

    def __repr__(self):
        # 이건 또 뭐여
        # F-string formatting? 이거인 것 같다
        # 예시로 기억하자
        # month = 1
        # while month <= 12:
        # print(f'2020년 {month}월')
        # month = month + 1
        return f"<Batch {self.reference}>"

    def __eq__(self, other):
        # 만약 Batch Type이 아니면 False
        if not isinstance(other, Batch):
            return False
        # 만약 Batch Type이라면, Reference (ID) 비교한다.
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)
    
    # > 메소드 재정의
    # __gt__ 만 정의해도 괜찮나?
    def __gt__(self, other):
        # 만약 self가 None이라면, 창고에 있는 물건이니 더 작다
        if self.eta is None:
            return False
        # 만약 other가 None이라면, 창고에 있는 물건이니 더 작다.
        if other.eta is None:
            return True
        #그게 아니라면 eta 기준으로 정렬한다.
        return self.eta > other.eta
    
    # OrderLine 받아서, 만약 allocate 가능하면 _allocations Set에 추가한다.
    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    # OreerLine 받아서, 만약 allocations Set에 있다면 제거한다.
    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    # Property 데코레이터를 사용해 Field가 있는 것 처럼 사용이 가능하다.
    # 현재 주문된 수량이 얼마인지 확인하기 위해
    # allocation Set에 있는 모든 수량을 합쳐 리턴한다.
    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    # 현재 사용 가능한 재고를 나타낸다.
    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    # 만약 SKU가 같고, 남아있는 재고가 주문량보다 적다면 배치 가능하다.
    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty