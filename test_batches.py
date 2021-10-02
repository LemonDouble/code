from datetime import date
from model import Batch, OrderLine


# 배치에 allocation 할당하면 사용 가능한 수량이 줄어드는지?
def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-123", sku, line_qty),
    )

# 현재 잔여수량이 요구수량보다 많다면, allocate 가능하다.
def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert large_batch.can_allocate(small_line)

# 현재 잔여수량이 요구수량보다 적다면, allocate 불가능하다.
# batch : 2개, line : 20개
def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)
    assert small_batch.can_allocate(large_line) is False

# 현재 잔여수량과 요구수량이 같다면, allocate 가능하다.
def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
    assert batch.can_allocate(line)

#만약 SKU가 매치되지 않는다면, allocate 불가능하다.
def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
    different_sku_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
    assert batch.can_allocate(different_sku_line) is False

# allocation은 멱등하다. 즉, f(x) == f(f(x))
# 여러번 진행해도 한 번만 allocate 된다.
# _allocation이 Set이기 때문에, Set 자료구조 특성상 중복 제거되므로 가능하다.
def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18

# deallocation. 만약 allocate 하고 deallocate 했다면, 수량 같아야 한다.
def test_deallocate():
    batch, line = make_batch_and_line("EXPENSIVE-FOOTSTOOL", 20, 2)
    batch.allocate(line)
    batch.deallocate(line)
    assert batch.available_quantity == 20

# allocation 된 라인만 deallocate 할 수 있다.
def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    assert batch.available_quantity == 20
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20
