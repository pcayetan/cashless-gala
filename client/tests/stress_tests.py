#!/usr/bin/env python
import sys
from pathlib import Path
import uuid
import logging

sys.path.insert(1, "../src/managers")
sys.path.insert(1, "../src/managers/com")
sys.path.insert(1, "..")

from src.managers.Client import Client
from src.utils.Euro import Eur
from src.utils.logs import init_logging

log = logging.getLogger()

if __name__ == "__main__":
    init_logging()
    client = Client()

    # REFILLING TEST
    customer = str(uuid.uuid4())
    for i in range(10):
        expected = i + 1
        client.requestRefilling(
            customer_id=customer,
            counter_id=1,
            device_uuid="TEST_UID_1",
            payment_method=3,
            amount=Eur(1),
        )
    balance = client.requestUserBalance(customer_id=customer)
    log.debug("{} {}".format(int(balance), expected))
    assert int(balance) == expected, "Refilling failed"
