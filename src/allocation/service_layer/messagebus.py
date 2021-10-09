from typing import List, Dict, Callable, Type
from allocation.adapters import email
from allocation.domain import events

# Message Bus : 어떤 이벤트가 발생했을 때, 어떤 핸들러 함수가 호출되는 방식

# 어떤 이벤트에 대해서, 해당 이벤트를 처리할 수 있는 핸들러 함수를 순차적으로 호출한다.
def handle(event: events.Event):
    for handler in HANDLERS[type(event)]:
        handler(event)

# OutOfStock 이벤트가 발생하면, email send 함수를 호출한다.
def send_out_of_stock_notification(event: events.OutOfStock):
    email.send_mail(
        "stock@made.com",
        f"Out of stock for {event.sku}",
    )

# HANDLERS는 Dictionary, Key는 event고, value는 핸들러 함수다.
# 예를 들어, OutOfStock 이벤트에 대해서는 send_out_of_stock_notification (구매부에 이메일 발송) 이벤트가 호출된다.
HANDLERS = {
    events.OutOfStock: [send_out_of_stock_notification],
}  # type: Dict[Type[events.Event], List[Callable]]
