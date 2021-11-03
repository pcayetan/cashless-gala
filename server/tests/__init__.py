#!/usr/bin/env python3
# -*- coding:utf-8 -*
from datetime import timedelta
from grpc import StatusCode

import os
import unittest
import pytest
import pathlib
import importlib
import cashless_server
import cashless_server.server
import cashless_server.com_pb2
import cashless_server.com_pb2_grpc
import cashless_server.settings
import cashless_server.pbutils

from grpc_testing import server_from_dictionary, strict_real_time


@pytest.fixture(scope="function")
def fake_db(tmpdir):
    db_file = pathlib.Path(tmpdir) / "database.sqlite"
    settings = pathlib.Path(tmpdir) / "settings.py"
    with open(settings, "w+") as f:
        f.write(f"DB_PATH='{db_file.absolute()!s}'")
    os.environ["CFG"] = str(settings.absolute())

    importlib.reload(cashless_server.settings)
    importlib.reload(cashless_server)

    from cashless_server.manage import setup

    with open("2019.json", "r") as f:
        setup(f)

    yield

    os.remove(settings)
    os.remove(db_file)


@pytest.mark.usefixtures("fake_db")
class PaymentProtocolTestCase(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        servicers = {
            cashless_server.com_pb2.DESCRIPTOR.services_by_name[
                "PaymentProtocol"
            ]: cashless_server.server.PaymentServicer()
        }
        self.test_server = server_from_dictionary(servicers, strict_real_time())

    @cashless_server.db_session
    def setUp(self, db):
        self.db = db

    def request(self, endpoint: str, request, invocation_metadata={}, timeout=1):
        start_time = cashless_server.pbutils.pb_now()
        response, _, code, _ = self.test_server.invoke_unary_unary(
            cashless_server.com_pb2.DESCRIPTOR.services_by_name[
                "PaymentProtocol"
            ].methods_by_name[endpoint],
            invocation_metadata=invocation_metadata,
            request=request,
            timeout=timeout,
        ).termination()
        self.assertEqual(code, StatusCode.OK, msg="Internal server error")
        self.assertAlmostEqual(
            response.now.ToDatetime(),
            start_time.ToDatetime(),
            delta=timedelta(seconds=timeout),
        )
        return response
