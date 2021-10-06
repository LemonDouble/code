from __future__ import annotations
from typing import Optional
from datetime import date

from domain import model
from domain.model import OrderLine
from adapters.repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(
    ref: str, sku: str, qty: int, eta: Optional[date],
    repo: AbstractRepository, session,
) -> None:
    repo.add(model.Batch(ref, sku, qty, eta))
    session.commit()

# Domain으로부터 완전히 독립적으로 서비스 계층을 만들려면, API가 원시 타입만 사용하도록 해야 한다.
# 이전 코드 : def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
# OrderLine이라는 Domain에 의존적인 자료형을 orderid, sku, qty로 나눠 string 형으로 나누었다.
def allocate(orderid: str, sku: str, qty: int, repo: AbstractRepository, session) -> str:
    line = OrderLine(orderid, sku, qty)
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref
