# Payment webhook idempotency

## Task
A webhook processor receives an `event_id` and an `amount`. A payment gateway callback charges the amount. Delivery may be repeated, including concurrently. Implement `PaymentProcessor.process(event_id, amount)` so that, **within one process instance**, at most one gateway charge happens for each event ID. Return `True` only for the request that performs the charge; duplicates return `False`. Do not cache an event as processed if charging raises an exception, so a future retry can proceed. Assume a successful charge callback is synchronous.

## Evaluation
Tests check sequential duplicates, concurrent repeated delivery and retry after failed charge. This simplified exercise is not a solution for cross-process or crash-safe payment idempotency; production requires durable atomic state and careful recovery semantics.

Run `python -m evaluator.runner --task payment_idempotency --candidate reference` from repository root.
