#!/usr/bin/env python3
# -*- coding:utf-8 -*
from google.protobuf.timestamp_pb2 import Timestamp
import decimal

from . import models, com_pb2


def pb_now() -> Timestamp:
    timestamp = Timestamp()
    timestamp.GetCurrentTime()
    return timestamp


def date_to_pb(date) -> Timestamp:
    timestamp = Timestamp()
    timestamp.FromDatetime(date)
    return timestamp


def decimal_to_pb_money(dec: decimal.Decimal) -> com_pb2.Money:
    return com_pb2.Money(amount=str(dec))


def pb_money_to_decimal(money: com_pb2.Money) -> decimal.Decimal:
    try:
        return decimal.Decimal(money.amount)
    except:
        return decimal.Decimal(0)


def refilling_to_pb(refilling: models.Refilling) -> com_pb2.Refilling:
    return com_pb2.Refilling(
        id=refilling.id,
        customer_id=refilling.customer_id,
        counter_id=refilling.counter_id,
        device_uuid=refilling.machine_id,
        payment_method=refilling.payment_method.id,
        amount=decimal_to_pb_money(refilling.amount),
        cancelled=refilling.cancelled,
        date=date_to_pb(refilling.date),
    )
