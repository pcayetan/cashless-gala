#!/usr/bin/env python3
# -*- coding:utf-8 -*

from decimal import Decimal
from cashless_server import models, com_pb2

from . import PaymentProtocolTestCase, fake_db

from cashless_server.pbutils import pb_money_to_decimal, decimal_to_pb_money
import itertools


class TestHistory(PaymentProtocolTestCase):
    def setUp(self):
        super().setUp()
        self.customer = "bob"
        self.counter = (
            self.request("CounterList", com_pb2.CounterListRequest()).counters[0].id
        )
        self.device_uuid = "i'm unique"

    def request_history(self, type: int = None):
        resp = self.request("History", com_pb2.HistoryRequest(type=type))
        self.assertEqual(resp.status, com_pb2.HistoryReply.Status.SUCCESS)
        return resp

    def test_request_history(self):
        refillings = itertools.product(
            ["toto", "tata", "titi", "tutu"],
            [counter.id for counter in self.db.query(models.Counter).all()],
            ["uuid1", "uuid2", "uuid3", "uuid4"],
            [Decimal("42.42"), Decimal("69.69"), Decimal("15.15"), Decimal("14.0")],
        )
        counter_refillings = {}
        for customer, counter, uuid, amount in refillings:
            resp = self.request(
                "Refill",
                com_pb2.RefillingRequest(
                    customer_id=customer,
                    counter_id=counter,
                    device_uuid=uuid,
                    payment_method=com_pb2.PaymentMethod.AE,
                    amount=decimal_to_pb_money(amount),
                ),
            )
            # Request status
            self.assertEqual(resp.status, com_pb2.RefillingReply.SUCCESS)
            counter_refillings[counter] = counter_refillings.get(counter, 0) + 1


        for counter in self.db.query(models.Counter).all():
            history = self.request("History", com_pb2.HistoryRequest(
                type=com_pb2.HistoryRequest.REFILLINGS,
                counter_id=counter.id
                )
            )
            self.assertEqual(resp.status, com_pb2.HistoryReply.Status.SUCCESS)
            self.assertNotEqual(len(history.refillings), 0)
            self.assertEqual(len(history.refillings), counter_refillings[counter.id])

