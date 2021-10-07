# Example application code for the python architecture book

## Chapters

Each chapter has its own branch which contains all the commits for that chapter,
so it has the state that corresponds to the _end_ of that chapter. If you want
to try and code along with a chapter, you'll want to check out the branch for the
previous chapter.

https://github.com/python-leap/code/branches/all

## Exercises

Branches for the exercises follow the convention `{chatper_name}_exercise`, eg
https://github.com/python-leap/code/tree/chapter_04_service_layer_exercise

## Requirements

- docker with docker-compose
- for chapters 1 and 2, and optionally for the rest: a local python3.7 virtualenv

## Building the containers

_(this is only required from chapter 3 onwards)_

```sh
make build
make up
# or
make all # builds, brings containers up, runs tests
```

## Creating a local virtualenv (optional)

```sh
python3.8 -m venv .venv && source .venv/bin/activate # or however you like to create virtualenvs

# for chapter 1
pip install pytest

# for chapter 2
pip install pytest sqlalchemy

# for chapter 4+5
pip install requirements.txt

# for chapter 6+
pip install requirements.txt
pip install -e src/
```

<!-- TODO: use a make pipinstall command -->

## Running the tests

```sh
make test
# or, to run individual test types
make unit
make integration
make e2e
# or, if you have a local virtualenv
make up
pytest tests/unit
pytest tests/integration
pytest tests/e2e
```

## Makefile

There are more useful commands in the makefile, have a look and try them out.

## 7장 메모

- 불변 조건(invariant) : 어떤 연산을 끝낼 때마다 항상 참이어야 하는 요소
- 제약(constraint) : 모델이 취할 수 있는 상태의 수를 제한
- 제약은 불변 조건을 만들 수 있다.
  - 중복 예약을 허용하지 않는 제약은, 한 객실엔 예약 하나만 있을 수 있다는 불변조건을 만든다.

### 애그리게이트란?

- 만약 A상품을 두 사람이 동시에 할당한다면, Race Condition에 의해서 문제 발생할 수 있다.
- 하지만 '가' 유저는 A상품을, '나' 유저는 B 상품을 할당하는건 아무 문제가 없다.

- Aggregate 패턴은, 다른 도메인 객체들을 포함하며 객체 컬렉션 전체를 다루게 해 주는 도메인 객체
- 애그리게이트 안에 있는 객체를 변경하려면, 애그리게이트를 불러와 애그리게이트 자체에 대한 메서드를 호출하는 것.

- Repository는 Aggregate만 반환해야 한다. 즉, Aggregate 도메인 모델에 접근할 수 있는 유일한 통로여야 한다.
  - 이렇게 함으로써, 애그리게이트가 단일 진입점이 되고, 시스템이 개념적으로 더 간단해지고 시스템 문제에 대해 추론하기 쉬워진다.
