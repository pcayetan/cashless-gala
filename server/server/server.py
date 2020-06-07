#!/usr/bin/env python3
# -*- coding:utf-8 -*

import grpc
import json
import decimal

from concurrent import futures
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.json_format import Parse

from server import db, models, com_pb2, com_pb2_grpc


def pb_now() -> Timestamp:
    timestamp = Timestamp()
    timestamp.GetCurrentTime()
    return timestamp


def decimal_to_pb_money(dec: decimal.Decimal) -> com_pb2.Money:
    tup = dec.as_tuple()
    return com_pb2.Money(sign=tup.sign, exponent=tup.exponent, digits=tup.digits)


def decimal_to_pb_money_dict(dec: decimal.Decimal):
    tup = dec.as_tuple()
    print(dec, tup)
    return {"sign": tup.sign, "exponent": tup.exponent, "digits": list(tup.digits)}


def pb_money_to_decimal(money: com_pb2.Money) -> decimal.Decimal:
    return decimal.Decimal(
        decimal.DecimalTuple(
            sign=money.sign, digits=money.digits, exponent=money.exponent
        )
    )


class PaymentServicer(com_pb2_grpc.PaymentProtocolServicer):
    """
        Communication protocol to communicate with the cashless client
    """

    def Buy(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Refill(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def RefoundBuying(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def CancelRefilling(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Transfert(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def Balance(self, request, context):
        """
            Return balance of a customer and create it if it doesn't exist
        """
        if not request.customer_id:
            return com_pb2.BalanceReply(
                status=com_pb2.BalanceReply.MISSING_CUSTOMER, now=pb_now()
            )
        customer = db.query(models.Customer).get(request.customer_id)
        if customer is None:
            customer = models.Customer(id=request.customer_id, balance=0)
            db.add(customer)
            db.commit()

        return com_pb2.BalanceReply(
            status=com_pb2.BalanceReply.SUCCESS,
            now=pb_now(),
            balance=decimal_to_pb_money(customer.balance),
        )

    def History(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def CounterList(self, request, context):
        """
            Return a list of every counter available
        """
        resp = []
        for counter in db.query(models.Counter).all():
            resp.append(
                com_pb2.CounterListReply.Counter(id=counter.id, name=counter.name)
            )
        return com_pb2.CounterListReply(
            status=com_pb2.CounterListReply.SUCCESS, counters=resp, now=pb_now()
        )

    def Products(self, request, context):
        """
            Return the list of products available on a given counter
        """
        if request.counter_id < 1:
            return com_pb2.ProductsReply(
                status=com_pb2.ProductsReply.MISSING_COUNTER, now=pb_now()
            )

        counter = db.query(models.Counter).get(request.counter_id)
        if counter is None:
            return com_pb2.ProductsReply(
                status=com_pb2.ProductsReply.COUNTER_NOT_FOUND, now=pb_now()
            )

        products = {}
        for availability in counter.products_available:
            product = availability.product

            # Navigate in tree to get to the deepest category
            # Create categories that doesn't exists in the process
            cat_list = product.category.split(".")
            main_cat = cat_list.pop(0)
            products[main_cat] = products.get(main_cat, {"sub": {}, "products": []})
            pos = products[main_cat]
            for cat in cat_list:
                pos["sub"][cat] = pos["sub"].get(cat, {"sub": {}, "products": []})
                pos = pos["sub"][cat]

            # Add the product at the end
            p = {
                "id": product.id,
                "name": product.name,
                "code": product.code,
                "default_price": decimal_to_pb_money_dict(product.default_price),
                "happy_hours": [],
            }

            # Add happy hours
            for happy_hour in product.happy_hours:
                start = Timestamp()
                start.FromDatetime(happy_hour.start)
                end = Timestamp()
                end.FromDatetime(happy_hour.end)
                p["happy_hours"].append(
                    {
                        "start": start.ToJsonString(),
                        "end": end.ToJsonString(),
                        "price": decimal_to_pb_money_dict(happy_hour.price),
                    }
                )
            pos["products"].append(p)

        # Here, we do a really ugly thing : we first encode everything to json
        # and then decode it to a protobuf message before it gets encoded again
        # THIS IS A TERRIBLE THING TO DO !
        # Why am I doing that ? The map implementation for python is shitty and left me no choice
        # This endpoint is realy slow and I don't care, it's not supposed to be called a lot
        resp = com_pb2.ProductsReply()
        Parse(
            json.dumps(
                {
                    "status": com_pb2.ProductsReply.SUCCESS,
                    "now": pb_now().ToJsonString(),
                    "items": products,
                }
            ),
            resp,
        )
        return resp


def serve(address: str, port: int, reflect: bool):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    com_pb2_grpc.add_PaymentProtocolServicer_to_server(PaymentServicer(), server)
    server.add_insecure_port("%s:%d" % (address, port))

    print("Listening from %s:%d" % (address, port))
    if reflect:
        from grpc_reflection.v1alpha import reflection

        SERVICE_NAMES = (
            com_pb2.DESCRIPTOR.services_by_name["PaymentProtocol"].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)
        print("Reflection enabled")

    server.start()
    server.wait_for_termination()
