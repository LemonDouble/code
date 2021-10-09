import abc
from typing import Set
from allocation.domain import model


class AbstractRepository(abc.ABC):
    def __init__(self):
        # seen : 자신에게 전달된 애그리게이트를 추적한다.
        self.seen = set()  # type: Set[model.Product]

    def add(self, product: model.Product):
        # _add : 상속받은 하위 객체에서 구현한다.
        self._add(product)
        # 그리고, seen에 객체를 추가한다.
        self.seen.add(product)

    def get(self, sku) -> model.Product:
        # 마찬가지로, _get : 상속받은 하위 객체에서 구현한다.
        product = self._get(sku)
        # 그리고, seen에 객체를 추가한다.
        if product:
            self.seen.add(product)
        return product

    @abc.abstractmethod
    def _add(self, product: model.Product):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, sku) -> model.Product:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, product):
        self.session.add(product)

    def _get(self, sku):
        return self.session.query(model.Product).filter_by(sku=sku).first()
