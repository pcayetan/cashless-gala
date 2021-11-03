#!/usr/bin/env python3
# -*- coding:utf-8 -*

from cashless_server import models, com_pb2

from . import PaymentProtocolTestCase, fake_db


class TestCounterList(PaymentProtocolTestCase):
    def setUp(self):
        super().setUp()
        self.base_counters = [
            {"id": 1, "name": "Central"},
            {"id": 2, "name": "Fosse"},
            {"id": 3, "name": "Assidu"},
            {"id": 4, "name": "Libanais"},
            {"id": 5, "name": "Pop-corn"},
            {"id": 6, "name": "Bulle"},
        ]

    def assert_counters(self, expected):
        req = self.request("CounterList", com_pb2.CounterListRequest())
        self.assertEqual(req.status, com_pb2.CounterListReply.Status.SUCCESS)
        self.assertEqual([{"id": c.id, "name": c.name} for c in req.counters], expected)

    def test_counter_list(self):
        self.assert_counters(self.base_counters)
        self.db.add(models.Counter(name="Foyer"))
        self.db.commit()
        self.assert_counters(self.base_counters + [{"id": 7, "name": "Foyer"}])
        for counter in self.db.query(models.Counter).all():
            self.db.delete(counter)
        self.db.commit()
        self.assert_counters([])
