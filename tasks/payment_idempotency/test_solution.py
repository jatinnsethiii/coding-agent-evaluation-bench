from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock
from time import sleep
from solution import PaymentProcessor


def test_sequential_duplicate():
    charges = []
    p = PaymentProcessor(charges.append)
    assert p.process("evt-1", 100) is True
    assert p.process("evt-1", 100) is False
    assert charges == [100]


def test_distinct_events_are_processed():
    charges = []
    p = PaymentProcessor(charges.append)
    assert p.process("evt-1", 100) is True
    assert p.process("evt-2", 200) is True
    assert charges == [100, 200]


def test_failed_charge_can_be_retried():
    calls = []
    def charge(amount):
        calls.append(amount)
        if len(calls) == 1:
            raise RuntimeError("temporary gateway failure")
    p = PaymentProcessor(charge)
    try:
        p.process("evt-1", 100)
        assert False, "expected gateway exception"
    except RuntimeError:
        pass
    assert p.process("evt-1", 100) is True
    assert calls == [100, 100]


def test_concurrent_redelivery_never_double_charges():
    charges = []
    charge_lock = Lock()
    start = Barrier(10)
    def slow_charge(amount):
        sleep(0.03)  # widens read/modify/write race in incorrect implementation
        with charge_lock:
            charges.append(amount)
    p = PaymentProcessor(slow_charge)
    def worker(_):
        start.wait(timeout=5)
        return p.process("same-event", 99)
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(worker, range(10)))
    assert results.count(True) == 1
    assert charges == [99]
