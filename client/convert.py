
from __future__ import print_function
#GRPC modules
import grpc
from grpc import RpcError
import com_pb2
import com_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp

from Euro import *
#decimal helps here to convert protobuf money into Euro
import decimal

#Help to convert google timestamp into QTime ...
from datetime import datetime
from Atoms import *

#Cute print in the terminal
from Console import *
# 'packing' describes the fact of converting the UI atom
# into a grpc message

# 'unpacking' describes the fact of converting the grpc
# message into an atom that UI can use.

def packProduct(product: Product) -> com_pb2.BasketItem:
    pb_price = packMoney(product.getPrice())
    newPbProduct = com_pb2.BasketItem(product_id=product.getId(),quantity=product.getQuantity(),unit_price=pb_price)
    return newPbProduct


def unpackProduct(pb_product: com_pb2.Product) -> Product:

    happyHoursList = []
    pbHappyHoursList = pb_product.happy_hours
    for j in pbHappyHoursList:
        newHappyHour = HappyHours()
        newHappyHour.setStart(j.start) #Still need to be converted in QTime 
        newHappyHour.setEnd(j.end)
        newHappyHour.setPrice(unpackMoney(j.price)) # Since we choosed a securised money format we need to convert
        happyHoursList.append(newHappyHour)
    newProduct = Product()
    newProduct.setId(pb_product.id)
    newProduct.setName(pb_product.name)
    newProduct.setCode(pb_product.code)
    newProduct.setPrice(unpackMoney(pb_product.default_price))
    newProduct.setHappyHours(happyHoursList)
    newProduct.setCategory(pb_product.category)
    newProduct.setQuantity(1)
    return newProduct

def packMoney(euro: Eur) -> com_pb2.Money:

    def decimal_to_pb_money(dec: decimal.Decimal) -> com_pb2.Money:
        tup = dec.as_tuple()
        return com_pb2.Money(sign=tup.sign, exponent=tup.exponent, digits=tup.digits)
    return decimal_to_pb_money(euro._amount)

def unpackMoney(money: com_pb2.Money) -> Eur:
    def pb_money_to_decimal(money: com_pb2.Money) -> decimal.Decimal:
        return decimal.Decimal(
            decimal.DecimalTuple(
                sign=money.sign, digits=money.digits, exponent=money.exponent
            )
        )
    return Eur(pb_money_to_decimal(money))

def packCounter(counter: Counter) -> com_pb2.CounterListReply.Counter:
    pass #should not be usefull

def unpackCounter(pb_counter: com_pb2.CounterListReply.Counter) -> Counter:
    newCounter = Counter()
    newCounter.setId(pb_counter.id)
    newCounter.setName(pb_counter.name)
    return newCounter

def packDistribution(distrib: Distribution) -> [com_pb2.Payment]:
    paymentList = []
    for user in distrib.getUserList():
        amount = distrib.getUserAmount(user)
        newPayement = com_pb2.Payment(customer_id = user, amount=amount)
        paymentList.append(newPayement)
    return paymentList

def unpackRefilling(pb_refilling: com_pb2.Refilling) -> Refilling:
    newRefilling = Refilling()
    newRefilling.setId(pb_refilling.id)
    newRefilling.setCounterId(pb_refilling.counter_id)
    newRefilling.setAmount(unpackMoney(pb_refilling.amount))
    newRefilling.setRefounded(pb_refilling.cancelled)
    return newRefilling
