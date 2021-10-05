import uuid
import pytest
import requests

import config


def random_suffix():
    return uuid.uuid4().hex[:6]

def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"


# 아래 테스트는 End To End 테스트

# Happy Path : 정상 경로
@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_allocated_batch(add_stock):
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    # 아래와 같은 Batch를 DB에 넣는다.
    add_stock(
        [
            (laterbatch, sku, 100, "2011-01-02"),
            (earlybatch, sku, 100, "2011-01-01"),
            (otherbatch, othersku, 100, None),
        ]
    )
    
    # 요청 Data 만들어서
    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}
    url = config.get_api_url()

    # API 엔드포인트에 보낸다.
    r = requests.post(f"{url}/allocate", json=data)

    assert r.status_code == 201
    assert r.json()["batchref"] == earlybatch

# Unhappy Path : 비정상 경로
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {"orderid": orderid, "sku": unknown_sku, "qty": 20}
    url = config.get_api_url()
    r = requests.post(f"{url}/allocate", json=data)

    # 저장되지 않은 SKU이므로, 400 Error 떠야 한다!
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid sku {unknown_sku}"
