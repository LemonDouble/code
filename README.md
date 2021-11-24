<img src = "https://github.com/LemonDouble/python_architecture/blob/master/img/XL.jpg" width="50%" height="50%">

## 파이썬으로 살펴보는 아키텍쳐 패턴

파이썬으로 살펴보는 아키텍쳐 패턴 책을 읽고, 예제 코드를 살펴보며 주석을 다는 리포지토리입니다.

단순히 책만 보는 것으로는 이해에 한계가 있어, 예제 코드에 직접 주석을 달며 이해력을 높였습니다.

현재 도메인 모델링을 지원하는 아키텍쳐 구축 (Chap 07) 까지 읽었으며, 작성한 주석은 해당 리포지토리의 브랜치를 통해 확인할 수 있습니다.

---

## Chapters

Each chapter has its own branch which contains all the commits for that chapter,
so it has the state that corresponds to the _end_ of that chapter.
If you want to try and code along with a chapter,
you'll want to check out the branch for the previous chapter.

https://github.com/cosmicpython/code/branches/all


## Exercises

Branches for the exercises follow the convention `{chapter_name}_exercise`,
eg https://github.com/cosmicpython/code/tree/chapter_04_service_layer_exercise


## Requirements

* docker with docker-compose
* for chapters 1 and 2, and optionally for the rest: a local python3.8 virtualenv


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
pip install -r requirements.txt

# for chapter 6+
pip install -r requirements.txt
pip install -e src/
```

<!-- TODO: use a make pipinstall command -->


## Running the tests

```sh
make test
# or, to run individual test types
make unit-tests
make integration-tests
make e2e-tests
# or, if you have a local virtualenv
make up
pytest tests/unit
pytest tests/integration
pytest tests/e2e
```

## Makefile

There are more useful commands in the makefile, have a look and try them out.

