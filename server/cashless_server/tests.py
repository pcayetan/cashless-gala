#!/usr/bin/env python3
# -*- coding:utf-8 -*

import unittest

import grpc

from google.protobuf.timestamp_pb2 import Timestamp
from grpc_testing import server_from_dictionary, strict_real_time

from . import db, models, com_pb2, com_pb2_grpc

from .pbutils import (
    pb_now,
    date_to_pb,
    decimal_to_pb_money,
    pb_money_to_decimal,
    refilling_to_pb,
)


class PaymentProtocolTestCase(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        servicers = {
            com_pb2.DESCRIPTOR.services_by_name[
                "PaymentProtocol"
            ]: com_pb2_grpc.PaymentProtocolServicer()
        }
        self.test_server = server_from_dictionary(servicers, strict_real_time())

    def setUp(self):
        # Create database
        pass


class TestBalance(PaymentProtocolTestCase):
    def test_non_existing_user(self):
        print("HELLO")
        self.assertEqual("hello", "hello")

    def test_existing_user(self):
        print("HELLO2")
        self.assertEqual("hello", "hello")
