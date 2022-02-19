import datetime

from agenda import now_events_message


def test_now_events_message_empty():
    dt = datetime.datetime(2022, 1, 1, 20, 30)
    msg = now_events_message(dt)
    print(msg)
    assert(False)


def test_now_events_message_full():
    dt = datetime.datetime(2022, 2, 18, 12, 30)
    msg = now_events_message(dt)
    print(msg)
    assert(False)
