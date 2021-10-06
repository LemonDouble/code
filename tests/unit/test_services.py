import pytest
from adapters import repository
from service_layer import services


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True

# 주요 변경점 : Service Layer Test가 Service Layer만 테스트하도록 변경했다.


# Service Layer에 추가된 새로운 add_batch 메소드
# 이 테스트는 Service Layer에 대한 테스트만 수행한다.
def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.committed

# Domain으로부터 완전히 독립적으로 서비스 계층을 만들려면, API가 원시 타입만 사용하도록 해야 한다.
# 이전 코드 : def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
# OrderLine이라는 Domain에 의존적인 자료형을 orderid, sku, qty로 나눠 string 형으로 나누었다.
# 현재 코드 : def allocate(orderid: str, sku: str, qty: int, repo: AbstractRepository, session) -> str:
# 이에 따라, allocate 테스트를 재작성한다.
def test_allocate_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, repo, session)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, session)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "AREALSKU", 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())


def test_commits():
    repo, session = FakeRepository([]), FakeSession()
    session = FakeSession()
    services.add_batch("b1", "OMINOUS-MIRROR", 100, None, repo, session)
    services.allocate("o1", "OMINOUS-MIRROR", 10, repo, session)
    assert session.committed is True
