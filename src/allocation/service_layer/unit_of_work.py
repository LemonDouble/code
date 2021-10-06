# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
import abc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from allocation import config
from allocation.adapters import repository

# UoW : 어떤 객체가 메모리에 적재되었고, 어떤 객체가 최종 상태인지를 기억한다.

# 작업에 대한 DB의 스냅샷 제공, 연산을 진행하는 도중 변경하지 않은 객체에 대한 스냅샷도 제공
# 변경 내용을 한번에 영속화할 방법 제공, 어딘가 잘못되더라도 일관성이 없는 상태로 끝나지 않는다. 
# 영속성 처리를 위한 간단한 API, 저장소를 쉽게 얻을 방법을 제공한다.

class AbstractUnitOfWork(abc.ABC):
    batches: repository.AbstractRepository

    # Context Manager, with 블록에 들어갈때는 Enter 함수가
    def __enter__(self) -> AbstractUnitOfWork:
        return self

    # 나올때는 Exit 함수가 자동으로 호출된다.
    def __exit__(self, *args):
        self.rollback()

    # 준비가 다 되었다면 Commit을 호출해 작업을 커밋
    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    # 커밋을 하지 않거나 예외가 발생되어 Context 관리자를 빠져나가면 Rollback을 수행. 
    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.get_postgres_uri(),
    )
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    # Default : PostgreSQL과 연결한다. 하지만 통합 테스트에서는 Session Factory 값을 넣어줌으로써
    # 즉, 오버로이드 함으로써 SQLite를 사용할 수 있도록 한다.
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    # Enter : DB 세션을 시작하고, 세션을 사용할 실제 저장소를 인스턴스화한다.
    def __enter__(self):
        self.session = self.session_factory()  # type: Session
        self.batches = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()
    
    # Exit : super.exit 통해 rollback 호출하고, 세션을 닫는다.
    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()
    
    
    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
