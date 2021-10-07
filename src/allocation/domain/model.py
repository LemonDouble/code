from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set


class OutOfStock(Exception):
    pass


# 같은 SKU(BLACK-CHAIR 같은 거)를 가지는 Batch를 Product 라는 개념으로 묶는다.
class Product:
    def __init__(self, sku: str, batches: List[Batch], version_number: int = 0):
        # Product의 식별자는 SKU다!
        self.sku = sku
        self.batches = batches
        # version은, 동시성을 제어할 수 있게 해 준다.
        # 예를 들어, DB에 ver = 2 인 Product를 A , B 쓰레드가 가져온다고 가정해 보자.
        # A,B 쓰레드는 각자 자신의 변경을 수행하고, ver=3인 데이터를 만든다.
        # 그리고 DB에 푸쉬하는데, A와 B 중 먼저 도착한 ver=3의 수정사항을 DB에 저장하고,
        # 늦게 도착한 ver=3의 수정사항은 Reject 한다. 이를 통해, 동시성을 지킬 수 있다.
        self.version_number = version_number

    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
            self.version_number += 1
            return batch.reference
        except StopIteration:
            raise OutOfStock(f"Out of stock for sku {line.sku}")


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
        return f"<Batch {self.reference}>"

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
