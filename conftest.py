import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from orm import metadata, start_mappers


@pytest.fixture
def in_memory_db():
    # Sqlite : H2 database같은 간단한 DB인것 같다.
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    # start_mappers는 직접 만든 ORM에서 가져온다.
    start_mappers()
    # Yield? Generator 문법인 것 같은데 왜 쓰는진 잘 모르겠다.
    # 책 Page 67페이지에 fixture라는 개념이 나오는데, 이거랑 관련 있을까?
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()
