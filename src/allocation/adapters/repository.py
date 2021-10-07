import abc
from allocation.domain import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, product: model.Product):
        raise NotImplementedError

    # 이제 Repository는 Aggregate를 반환한다!
    @abc.abstractmethod
    def get(self, sku) -> model.Product:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, product):
        self.session.add(product)

    def get(self, sku):
        return self.session.query(model.Product).filter_by(sku=sku).first()
