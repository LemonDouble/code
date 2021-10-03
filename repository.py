import abc
import model

# abc : Abstact Base Class
# Java의 interface 비슷한 기능인가?

class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        # 만약 AbstractRepository 상속받은 Class가 add 함수 구현 안 했다면,
        # AbstractRepository 의 add 함수 실행될 것이다.
        # 그런데 만약 여기가 비어있으면 에러 없이 실행될 것이므로 문제가 될 수 있다.
        # 따라서, 구현 안 됨 Exception을 띄운다.
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    # session은 SQLAlchemy의 몬가몬가인데 SQLAlchemy는 import 안 했는데?
    # conftest.py에서 session 설정 했었으니, 뭔가 DI같은거 해 주는건가?
    # Test 코드 보면 될 것 같다.
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference):
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(model.Batch).all()
