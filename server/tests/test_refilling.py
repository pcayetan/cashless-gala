#!/usr/bin/env python3
# -*- coding:utf-8 -*

import typing
import pytz
import itertools
from decimal import Decimal
from cashless_server import models, com_pb2, pbutils
from cashless_server.settings import TIMEZONE

from . import PaymentProtocolTestCase, fake_db

from datetime import datetime, timedelta, tzinfo


class TestRefilling(PaymentProtocolTestCase):
    def setUp(self):
        super().setUp()
        self.customer = "bob"
        self.counter = (
            self.request("CounterList", com_pb2.CounterListRequest()).counters[0].id
        )
        self.device_uuid = "i'm unique"

    def get_balance(self, customer: typing.Optional[str] = None) -> Decimal:
        return pbutils.pb_money_to_decimal(
            self.request(
                "Balance",
                com_pb2.BalanceRequest(
                    customer_id=customer if customer is not None else self.customer
                ),
            ).balance
        )

    def test_bad_cancel_refilling_request(self):
        expected_balance = Decimal(42)
        refilling = self.request(
            "Refill",
            com_pb2.RefillingRequest(
                customer_id=self.customer,
                counter_id=self.counter,
                device_uuid=self.device_uuid,
                payment_method=com_pb2.PaymentMethod.AE,
                amount=pbutils.decimal_to_pb_money(expected_balance),
            ),
        )
        self.assertEqual(refilling.status, com_pb2.RefillingReply.SUCCESS)

        def assert_bad_request(request, expected):
            old_balance = self.get_balance()
            self.assertEqual(old_balance, expected_balance)
            self.assertEqual(self.request("CancelRefilling", request).status, expected)
            self.assertEqual(old_balance, self.get_balance())

        assert_bad_request(
            com_pb2.CancelRefillingRequest(),
            com_pb2.CancelRefillingReply.MISSING_TRANSACTION,
        )

        assert_bad_request(
            com_pb2.CancelRefillingRequest(refilling_id=42),
            com_pb2.CancelRefillingReply.TRANSACTION_NOT_FOUND,
        )

        self.assertEqual(
            self.request(
                "CancelRefilling",
                com_pb2.CancelRefillingRequest(refilling_id=refilling.refilling.id),
            ).status,
            com_pb2.CancelRefillingReply.SUCCESS,
        )
        expected_balance = Decimal(0)

        assert_bad_request(
            com_pb2.CancelRefillingRequest(refilling_id=refilling.refilling.id),
            com_pb2.CancelRefillingReply.ALREADY_CANCELLED,
        )

    def test_bad_refill_requests(self):
        def assert_bad_request(request, expected, test_func=self.assertEqual):
            old_balance = self.get_balance()
            self.assertEqual(old_balance, Decimal(0))
            test_func(self.request("Refill", request).status, expected)
            self.assertEqual(old_balance, self.get_balance())

        assert_bad_request(
            com_pb2.RefillingRequest(),
            com_pb2.RefillingReply.SUCCESS,
            self.assertNotEqual,
        )
        assert_bad_request(
            com_pb2.RefillingRequest(
                counter_id=self.counter,
                device_uuid=self.device_uuid,
                payment_method=com_pb2.PaymentMethod.CASH,
                amount=pbutils.decimal_to_pb_money(Decimal("10.89")),
            ),
            com_pb2.RefillingReply.MISSING_CUSTOMER,
        )
        assert_bad_request(
            com_pb2.RefillingRequest(
                customer_id=self.customer,
                device_uuid=self.device_uuid,
                payment_method=com_pb2.PaymentMethod.CASH,
                amount=pbutils.decimal_to_pb_money(Decimal("10.89")),
            ),
            com_pb2.RefillingReply.MISSING_COUNTER,
        )
        assert_bad_request(
            com_pb2.RefillingRequest(
                customer_id=self.customer,
                counter_id=self.counter,
                payment_method=com_pb2.PaymentMethod.CASH,
                amount=pbutils.decimal_to_pb_money(Decimal("10.89")),
            ),
            com_pb2.RefillingReply.MISSING_DEVICE_UUID,
        )
        assert_bad_request(
            com_pb2.RefillingRequest(
                customer_id=self.customer,
                counter_id=self.counter,
                device_uuid=self.device_uuid,
                amount=pbutils.decimal_to_pb_money(Decimal("10.89")),
            ),
            com_pb2.RefillingReply.MISSING_PAYMENT_METHOD,
        )
        assert_bad_request(
            com_pb2.RefillingRequest(
                customer_id=self.customer,
                counter_id=self.counter,
                device_uuid=self.device_uuid,
                payment_method=com_pb2.PaymentMethod.NOT_PROVIDED,
                amount=pbutils.decimal_to_pb_money(Decimal("10.89")),
            ),
            com_pb2.RefillingReply.MISSING_PAYMENT_METHOD,
        )
        assert_bad_request(
            com_pb2.RefillingRequest(
                customer_id=self.customer,
                counter_id=42,
                device_uuid=self.device_uuid,
                payment_method=com_pb2.PaymentMethod.CASH,
                amount=pbutils.decimal_to_pb_money(Decimal("10.89")),
            ),
            com_pb2.RefillingReply.COUNTER_NOT_FOUND,
        )

    def assert_cancel_refilling_request(
        self,
        refilling_id: str,
        customer: str,
    ):
        old_balance = self.get_balance(customer)
        self.assertFalse(self.db.query(models.Refilling).get(refilling_id).cancelled)
        resp = self.request(
            "CancelRefilling", com_pb2.CancelRefillingRequest(refilling_id=refilling_id)
        )
        # Request status
        self.assertEqual(resp.status, com_pb2.CancelRefillingReply.SUCCESS)

        # Check if cancelled
        self.db.commit()  # Refresh DB to get changes
        refilling = self.db.query(models.Refilling).get(refilling_id)
        self.assertTrue(refilling.cancelled)

        # Check returned customer
        self.assertEqual(resp.customer_id, customer)
        self.assertEqual(resp.customer_id, refilling.customer_id)

        # Check customer balance
        self.assertEqual(
            pbutils.pb_money_to_decimal(resp.customer_balance),
            self.get_balance(customer),
        )
        self.assertEqual(
            pbutils.pb_money_to_decimal(resp.customer_balance),
            old_balance - refilling.amount,
        )

    def assert_refilling_request(
        self,
        customer: str,
        counter: str,
        device_uuid: str,
        refill_amount: Decimal,
        new_balance: Decimal,
        payment_method: com_pb2.PaymentMethod,
        payment_method_name: str,
    ):
        resp = self.request(
            "Refill",
            com_pb2.RefillingRequest(
                customer_id=customer,
                counter_id=counter,
                device_uuid=device_uuid,
                payment_method=payment_method,
                amount=pbutils.decimal_to_pb_money(refill_amount),
            ),
        )
        # Request status
        self.assertEqual(resp.status, com_pb2.RefillingReply.SUCCESS)

        # Balance
        self.assertEqual(self.get_balance(customer), new_balance)
        self.assertEqual(
            self.get_balance(customer),
            pbutils.pb_money_to_decimal(resp.customer_balance),
        )

        # Corresponding object
        refilling = self.db.query(models.Refilling).get(resp.refilling.id)
        self.assertIsNotNone(refilling)

        # Customer
        self.assertEqual(resp.refilling.customer_id, customer)
        self.assertEqual(resp.refilling.customer_id, refilling.customer_id)

        # Payment method
        self.assertEqual(refilling.payment_method_id, payment_method)
        self.assertEqual(refilling.payment_method.name, payment_method_name)
        self.assertEqual(resp.refilling.payment_method, payment_method)

        # Counter id
        self.assertEqual(resp.refilling.counter_id, counter)
        self.assertEqual(resp.refilling.counter_id, refilling.counter_id)

        # Device uuid
        self.assertEqual(resp.refilling.device_uuid, device_uuid)
        self.assertEqual(resp.refilling.device_uuid, refilling.machine_id)

        # Amourt
        self.assertEqual(
            pbutils.pb_money_to_decimal(resp.refilling.amount), Decimal(refill_amount)
        )
        self.assertEqual(
            pbutils.pb_money_to_decimal(resp.refilling.amount), refilling.amount
        )

        # Cancellation status
        self.assertEqual(resp.refilling.cancelled, False)
        self.assertEqual(resp.refilling.cancelled, refilling.cancelled)

        # Creation date
        self.assertAlmostEqual(
            pytz.utc.localize(refilling.date),
            datetime.now(TIMEZONE),
            delta=timedelta(seconds=1),
        )
        self.assertEqual(resp.refilling.date, pbutils.date_to_pb(refilling.date))

    def test_refilling(self):
        ledger = {}
        refill_amount = Decimal("10.89")
        for payment_method in [
            (com_pb2.PaymentMethod.UNKNOWN, "inconnu"),
            (com_pb2.PaymentMethod.CASH, "espèces"),
            (com_pb2.PaymentMethod.CARD, "carte"),
            (com_pb2.PaymentMethod.CHECK, "chèque"),
            (com_pb2.PaymentMethod.AE, "AE"),
            (com_pb2.PaymentMethod.TRANSFER, "transfert"),
            (com_pb2.PaymentMethod.OTHER, "autre"),
        ]:
            ledger[self.customer] = (
                ledger.get(self.customer, Decimal("0")) + refill_amount
            )
            self.assert_refilling_request(
                self.customer,
                self.counter,
                self.device_uuid,
                refill_amount,
                ledger[self.customer],
                payment_method[0],
                payment_method[1],
            )

        # Test that nobody else got refilled
        all_customers = self.db.query(models.Customer).all()
        self.assertEqual(len(all_customers), 1)
        self.assertEqual(all_customers[0].id, self.customer)
        self.assertEqual(all_customers[0].balance, ledger[self.customer])

        # Test with different accounts
        for refill_amount, customer, counter, device_uuid in itertools.product(
            [Decimal("89.87"), Decimal("69.69"), Decimal("-8"), Decimal("5")],
            ["toto", "tata", "uta", "atu"],
            [counter.id for counter in self.db.query(models.Counter).all()],
            ["je", "suis", "un", "robot"],
        ):
            ledger[customer] = ledger.get(customer, Decimal("0")) + refill_amount
            self.assert_refilling_request(
                customer,
                counter,
                device_uuid,
                refill_amount,
                ledger[customer],
                com_pb2.PaymentMethod.AE,
                "AE",
            )

        # Test cancelling all refills
        for refilling in self.db.query(models.Refilling).all():
            self.assert_cancel_refilling_request(refilling.id, refilling.customer_id)
