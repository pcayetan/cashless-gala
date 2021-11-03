#!/usr/bin/env python3
# -*- coding:utf-8 -*

from decimal import Decimal
from cashless_server import models, com_pb2

from . import PaymentProtocolTestCase, fake_db

from cashless_server.pbutils import pb_money_to_decimal


class TestBalance(PaymentProtocolTestCase):
    def request_balance(self, customer: str):
        resp = self.request("Balance", com_pb2.BalanceRequest(customer_id=customer))
        self.assertEqual(resp.status, com_pb2.BalanceReply.Status.SUCCESS)
        return resp

    def test_bad_request(self):
        self.assertEqual(
            self.request("Balance", com_pb2.BalanceRequest()).status,
            com_pb2.BalanceReply.Status.MISSING_CUSTOMER,
        )

    def test_non_existing_customer(self):
        customer = "Alice"
        self.assertIsNone(self.db.query(models.Customer).get(customer))
        self.assertEqual(
            pb_money_to_decimal(self.request_balance(customer).balance), Decimal(0)
        )
        created_customer = self.db.query(models.Customer).get(customer)
        self.assertIsNotNone(created_customer)
        self.assertEqual(created_customer.balance, Decimal(0))

    def test_existing_user(self):
        customer = models.Customer(id="Bob", balance=Decimal("10.30"))
        self.db.add(customer)
        self.db.commit()
        self.assertEqual(
            pb_money_to_decimal(self.request_balance(customer.id).balance),
            customer.balance,
        )
