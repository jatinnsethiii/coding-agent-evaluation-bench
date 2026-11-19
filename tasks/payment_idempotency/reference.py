from threading import Lock


class PaymentProcessor:
    def __init__(self, charge):
        self.charge = charge
        self.processed = set()
        self._lock = Lock()

    def process(self, event_id, amount):
        with self._lock:
            if event_id in self.processed:
                return False
            self.charge(amount)
            self.processed.add(event_id)
            return True
