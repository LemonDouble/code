from __future__ import annotations

import model
from model import OrderLine
from repository import AbstractRepository

# 전형적인 Service 계층의 함수들
# 1. 저장소에서 어떤 객체들을 가져온다.
# 2. 현재 (어플리케이션이 아는) 세계를 바탕으로, 요청을 검사하거나 Assertion으로 검증한다.
# 3. 도메인 서비스를 호출한다.
# 4. 모든 단계가 정상적으로 실행되었다면, 변경한 상태를 저장하거나 업데이트한다.

class InvalidSku(Exception):
    pass

# batches 안에 SKU가 있다면, valid하다.
def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    # batch를 가져온다 (1)
    batches = repo.list()
    # 요청을 검사한다. (2)
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    
    # 도메인 서비스를 호출한다 (3)
    batchref = model.allocate(line, batches)
    # 변경된 상태를 저장하거나 업데이트한다.
    session.commit()
    return batchref
