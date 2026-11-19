class PaymentProcessor:
    def __init__(self, charge):
        self.charge = charge
        self.processed = set()

    def process(self, event_id, amount):
        if event_id in self.processed:
            return False
        self.charge(amount)
        self.processed.add(event_id)
        return True
