from __future__ import annotations
from typing import Optional
from datetime import date

from allocation.domain import model
from allocation.domain.model import OrderLine
from allocation.service_layer import unit_of_work


class InvalidSku(Exception):
    pass


def add_batch(
    ref: str, sku: str, qty: int, eta: Optional[date],
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        # 해당 SKU에 맞는 Product Aggregate를 가져온다.
        product = uow.products.get(sku=sku)
        # 만약 Product 없다면 (즉, 이번 Batch가 첫 SKU라면)
        if product is None:
            # 새로운 Product 만든다.
            product = model.Product(sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(ref, sku, qty, eta))
        uow.commit()


def allocate(
    orderid: str, sku: str, qty: int,
    uow: unit_of_work.AbstractUnitOfWork,
) -> str:
    # 받은 Parameter로 새로운 OrderLine 만들고
    line = OrderLine(orderid, sku, qty)
    with uow:
        # 해당 SKU와 같은 Product 가져온 후
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        # product에 allocate 한다.
        batchref = product.allocate(line)
        uow.commit()
    return batchref
