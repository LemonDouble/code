from dataclasses import dataclass


class Event:
    pass
# Event는 단순한 값 객체
# @dataclass : 기본적으로 __init__, __repr__, __eq__ 메서드를 생성한다.
@dataclass
class OutOfStock(Event):
    sku: str
