#!/usr/bin/env python3
# -*- coding:utf-8 -*

import grpc
import json
import decimal

from concurrent import futures
from google.protobuf.timestamp_pb2 import Timestamp

from server import db, models, com_pb2, com_pb2_grpc


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


def get_or_create_machine(_uuid: str) -> models.Machine:
    machine = db.query(models.Machine).get(_uuid)
    if machine is None:
        machine = models.Machine(uuid=_uuid)
        db.add(machine)
        db.commit()
    return machine


def get_or_create_customer(_id: str) -> models.Customer:
    customer = db.query(models.Customer).get(_id)
    if customer is None:
        customer = models.Customer(id=_id, balance=0)
        db.add(customer)
        db.commit()
    return customer


class PaymentServicer(com_pb2_grpc.PaymentProtocolServicer):
    """
        Communication protocol to communicate with the cashless client
    """

    def Buy(self, request, context):
        """
            Validate a given basket and roll payments for customer
            according to the money repartition given by the client
        """
        # Some basic checks
        if not request.counter_id:
            return com_pb2.BuyingReply(
                now=pb_now(), status=com_pb2.BuyingReply.MISSING_COUNTER
            )
        if not request.device_uuid:
            return com_pb2.BuyingReply(
                now=pb_now(), status=com_pb2.BuyingReply.MISSING_DEVICE_UUID
            )

        counter = db.query(models.Counter).get(request.counter_id)
        if counter is None:
            return com_pb2.BuyingReply(
                now=pb_now(), status=com_pb2.BuyingReply.COUNTER_NOT_FOUND
            )
        machine = get_or_create_machine(request.device_uuid)

        total_payment = decimal.Decimal("0")  # Total payment of customers
        real_price_sum = decimal.Decimal(
            "0"
        )  # Used to check if total_payment is correct
        payments = []  # Contains tuple (customer, amount_for_customer)
        for payment in request.payments:
            customer = get_or_create_customer(payment.customer_id)
            amount = pb_money_to_decimal(payment.amount)
            if amount > customer.balance:
                return com_pb2.BuyingReply(
                    now=pb_now(), status=com_pb2.BuyingReply.NOT_ENOUGH_MONEY
                )
            total_payment += amount
            payments.append((customer, amount))

        basket = []  # Contains tuple (product, quantity, real_unit_price)
        # When here, we know that every one have enough money
        # Time to check if the total price matchs items in basket
        for item in request.basket:
            product = db.query(models.Product).get(item.product_id)
            if product is None:
                return com_pb2.BuyingReply(
                    now=pb_now(), status=com_pb2.BuyingReply.ITEM_NOT_FOUND
                )
            real_unit_price = product.real_unit_price
            quantity = item.quantity
            basket.append((product, quantity, real_unit_price))
            real_price_sum += real_unit_price * quantity

        # If the two sums differs, it means the client either forgot someone in the payment list
        # Or surely did not take happy hours into account
        if total_payment != real_price_sum:
            return com_pb2.BuyingReply(
                now=pb_now(), status=com_pb2.BuyingReply.MISSING_AMOUNT_IN_PAYMENT
            )

        # Here, we know that every product exists and that prices matches
        # We roll payments
        reply_customer_ids = []  # Used for response
        reply_customer_balances = []  # Used for response
        reply_payments = []  # Used for response
        reply_items = []  # Used for response
        buying = models.Buying(
            counter_id=counter.id, machine_id=machine.uuid, refounded=False,
        )
        db.add(buying)
        db.commit()
        for item in basket:
            db.add(
                models.BasketItem(
                    buying_id=buying.id,
                    product_id=item[0].id,
                    quantity=item[1],
                    unit_price=item[2],
                )
            )
            reply_items.append(
                com_pb2.BasketItem(
                    product_id=item[0].id,
                    quantity=item[1],
                    unit_price=decimal_to_pb_money(item[2]),
                )
            )
        for payment in payments:
            customer = payment[0]
            customer.balance -= payment[1]
            db.add(customer)
            db.add(
                models.Payment(
                    customer_id=customer.id, buying_id=buying.id, amount=payment[1]
                )
            )
            reply_customer_ids.append(customer.id)
            reply_customer_balances.append(decimal_to_pb_money(customer.balance))
            reply_payments.append(
                com_pb2.Payment(
                    customer_id=customer.id, amount=decimal_to_pb_money(payment[1])
                )
            )
        db.commit()
        buying.generate_label()
        db.add(buying)
        db.commit()

        return com_pb2.BuyingReply(
            now=pb_now(),
            status=com_pb2.BuyingReply.SUCCESS,
            customer_ids=reply_customer_ids,
            customer_balances=reply_customer_balances,
            transaction=com_pb2.Buying(
                id=buying.id,
                label=buying.label,
                price=decimal_to_pb_money(total_payment),
                date=date_to_pb(buying.date),
                items=reply_items,
                payments=reply_payments,
            ),
        )

    def Refill(self, request, context):
        """
            Refill a customer account with money
        """
        if not request.customer_id:
            return com_pb2.RefillingReply(
                now=pb_now(), status=com_pb2.RefillingReply.MISSING_CUSTOMER
            )
        if not request.counter_id:
            return com_pb2.RefillingReply(
                now=pb_now(), status=com_pb2.RefillingReply.MISSING_COUNTER
            )
        if not request.device_uuid:
            return com_pb2.RefillingReply(
                now=pb_now(), status=com_pb2.RefillingReply.MISSING_DEVICE_UUID
            )

        counter = db.query(models.Counter).get(request.counter_id)
        if counter is None:
            return com_pb2.RefillingReply(
                now=pb_now(), status=com_pb2.RefillingReply.COUNTER_NOT_FOUND
            )

        customer = get_or_create_customer(request.customer_id)
        machine = get_or_create_machine(request.device_uuid)
        amount = pb_money_to_decimal(request.amount)

        customer.balance += amount
        db.add(customer)
        refilling = models.Refilling(
            customer_id=customer.id,
            payment_method_id=request.payment_method,
            counter_id=counter.id,
            machine_id=machine.uuid,
            amount=amount,
            cancelled=False,
        )
        db.add(refilling)
        db.commit()
        return com_pb2.RefillingReply(
            now=pb_now(),
            status=com_pb2.RefillingReply.SUCCESS,
            customer_balance=decimal_to_pb_money(customer.balance),
            refilling=refilling_to_pb(refilling),
        )

    def RefoundBuying(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def CancelRefilling(self, request, context):
        """
            Cancel a refilling
        """
        if not request.refilling_id:
            return com_pb2.CancelRefillingReply(
                now=pb_now(), status=com_pb2.CancelRefillingReply.MISSING_TRANSACTION
            )
        if not request.device_uuid:
            return com_pb2.CancelRefillingReply(
                now=pb_now(), status=com_pb2.CancelRefillingReply.MISSING_DEVICE_UUID
            )

        refilling = db.query(models.Refilling).get(request.refilling_id)
        if refilling is None:
            return com_pb2.CancelRefillingReply(
                now=pb_now(), status=com_pb2.CancelRefillingReply.TRANSACTION_NOT_FOUND
            )

        refilling.cancelled = True
        customer = refilling.customer
        customer.balance -= refilling.amount
        db.add(refilling)
        db.commit()

        return com_pb2.CancelRefillingReply(
            now=pb_now(),
            status=com_pb2.CancelRefillingReply.SUCCESS,
            customer_id=customer.id,
            customer_balance=decimal_to_pb_money(customer.balance),
        )

    def Transfert(self, request, context):
        """
            Transfert money from a customer to another
        """
        if not request.origin_id:
            return com_pb2.TransfertReply(
                now=pb_now(), status=com_pb2.TransfertReply.MISSING_ORIGN
            )

        if not request.destination_id:
            return com_pb2.TransfertReply(
                now=pb_now(), status=com_pb2.TransfertReply.MISSING_DESTINATION
            )

        if not request.counter_id:
            return com_pb2.TransfertReply(
                now=pb_now(), status=com_pb2.TransfertReply.MISSING_COUNTER
            )

        if not request.device_uuid:
            return com_pb2.TransfertReply(
                now=pb_now(), status=com_pb2.TransfertReply.MISSING_DEVICE_UUID,
            )

        counter = db.query(models.Counter).get(request.counter_id)
        if counter is None:
            return com_pb2.TransfertReply(
                now=pb_now(), status=com_pb2.TransfertReply.COUNTER_NOT_FOUND,
            )

        amount = pb_money_to_decimal(request.amount)

        # Check origin balance
        origin_customer = get_or_create_customer(request.origin_id)
        if origin_customer.balance < amount:
            return com_pb2.TransfertReply(
                now=pb_now(), status=com_pb2.TransfertReply.NOT_ENOUGH_MONEY,
            )
        destination_customer = get_or_create_customer(request.destination_id)
        machine = get_or_create_machine(request.device_uuid)

        # Remove money from origin
        origin_customer.balance -= amount
        db.add(origin_customer)
        origin_refilling = models.Refilling(
            customer_id=origin_customer.id,
            payment_method_id=com_pb2.TRANSFER,
            counter_id=counter.id,
            machine_id=machine.uuid,
            amount=-amount,
            cancelled=False,
        )
        db.add(origin_refilling)

        # Adding money to destination
        destination_customer.balance += amount
        db.add(destination_customer)
        destination_refilling = models.Refilling(
            customer_id=destination_customer.id,
            payment_method_id=com_pb2.TRANSFER,
            counter_id=counter.id,
            machine_id=machine.uuid,
            amount=amount,
            cancelled=False,
        )
        db.add(destination_refilling)

        db.commit()

        return com_pb2.TransfertReply(
            now=pb_now(),
            status=com_pb2.TransfertReply.SUCCESS,
            origin_balance=decimal_to_pb_money(origin_customer.balance),
            destination_balance=decimal_to_pb_money(destination_customer.balance),
            origin_refilling=refilling_to_pb(origin_refilling),
            destination_refilling=refilling_to_pb(destination_refilling),
        )

    def Balance(self, request, context):
        """
            Return balance of a customer and create it if it doesn't exist
        """
        if not request.customer_id:
            return com_pb2.BalanceReply(
                status=com_pb2.BalanceReply.MISSING_CUSTOMER, now=pb_now()
            )

        return com_pb2.BalanceReply(
            status=com_pb2.BalanceReply.SUCCESS,
            now=pb_now(),
            balance=decimal_to_pb_money(
                get_or_create_customer(request.customer_id).balance
            ),
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
        if not request.counter_id:
            return com_pb2.ProductsReply(
                status=com_pb2.ProductsReply.MISSING_COUNTER, now=pb_now()
            )

        counter = db.query(models.Counter).get(request.counter_id)
        if counter is None:
            return com_pb2.ProductsReply(
                status=com_pb2.ProductsReply.COUNTER_NOT_FOUND, now=pb_now()
            )

        products = []
        for availability in counter.products_available:
            product = availability.product

            p = com_pb2.Product(
                id=product.id,
                name=product.name,
                code=product.code,
                default_price=decimal_to_pb_money(product.default_price),
                category=product.category,
            )

            # Add happy hours
            for happy_hour in product.happy_hours:
                p.happy_hours.append(
                    com_pb2.Product.HappyHour(
                        start=date_to_pb(happy_hour.start),
                        end=date_to_pb(happy_hour.end),
                        price=decimal_to_pb_money(happy_hour.price),
                    )
                )
            products.append(p)

        return com_pb2.ProductsReply(
            status=com_pb2.ProductsReply.SUCCESS, now=pb_now(), products=products
        )


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
