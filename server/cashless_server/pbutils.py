#!/usr/bin/env python3
# -*- coding:utf-8 -*
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime
import decimal
import pytz

from . import models, com_pb2
from .settings import TIMEZONE


def pb_now() -> com_pb2.Time:
    timestamp = Timestamp()
    timestamp.FromDatetime(datetime.utcnow())
    return com_pb2.Time(time=timestamp, timezone=TIMEZONE.zone)


def date_to_pb(date: datetime) -> com_pb2.Time:
    """
    Only works if the date comes from the database
    """
    timestamp = Timestamp()
    timestamp.FromDatetime(date)
    return com_pb2.Time(time=timestamp, timezone=TIMEZONE.zone)


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
