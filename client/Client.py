from __future__ import print_function

import grpc
from grpc import RpcError
import com_pb2
import com_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from QAtoms import *
from Console import *

from convert import *



#def addProduct(product,categoryList):
#    try:
#        if isinstance(product,dict):
#            productDict={categoryList[-1]:product}
#        else:
#            productDict={categoryList[-1]:[product]}
#        return addProduct(productDict,categoryList[:-1])
#    except IndexError:
#        return product


#def parseProducts(productsReply):
#    pbProductList = productsReply.products # get protobuff products
#    for i in pbProductList:
#        happyHoursList = []
#        pbHappyHoursList = i.happy_hours
#        for j in pbHappyHoursList:
#            newHappyHour = HappyHours()
#            newHappyHour.setStart(j.start) #Still need to be converted in QTime 
#            newHappyHour.setEnd(j.end)
#            newHappyHour.setPrice(pb_money_to_eur(j.price)) # Since we choosed a securised money format we need to convert
#            happyHoursList.append(newHappyHour)
#        newProduct = Product()
#        newProduct.setId(i.id)
#        newProduct.setName(i.name)
#        newProduct.setCode(i.code)
#        newProduct.setPrice(pb_money_to_eur(i.default_price))
#        newProduct.setHappyHours(happyHoursList)
#        newProduct.setCategory(i.category)
#

class ClientSingleton(type):
    _instance = {}

    def __call__(cls):
        if cls not in cls._instance:
            cls._instance[cls] = super(ClientSingleton , cls).__call__()
        return cls._instance[cls]

class Client(metaclass=ClientSingleton):

    def __init__(self):
        self.serverAddress="127.0.0.1:50051"
        self.channel = grpc.insecure_channel(self.serverAddress)
        self.stub = com_pb2_grpc.PaymentProtocolStub(self.channel)
        self.now = None

    def requestBuy(self,**kwargs):
        """
    int64 counter_id
    string device_uuid
    repeated Payment payments
    repeated BasketItem basket
        """
        pass


    def requestRefilling(self, **kwargs):
        """
        string customer_id
        int64 counter_id
        string device_uuid
        PaymentMethod payment_method
        double amount
        """
        try:
            refillingRequest = com_pb2.RefillingRequest(**kwargs)
            refillingReply = self.stub.Refill(refillingRequest)
            self.now = refillingReply.now
            newBalance = unpackMoney(refillingReply.amount)
            refilling = unpackRefilling(refillingReply.refilling)
            refilling.setNewBalance(newBalance)
            return refilling
        except RpcError:
            printE("Unable to refill")
            return None

    def requestHistory(self, **kwargs):
        pass


    def requestRefund(self, **kwargs):
        pass


    def requestCounterProduct(self, **kwargs):
        """
        int64 counter_id
        """
        productList = []
        try:
            productsRequest = com_pb2.ProductsRequest(**kwargs)
            productsReply = self.stub.Products(productsRequest)
            self.now = productsReply.now

            # Fill product List 
            pbProductList = productsReply.products # get protobuff products
            for pb_product in pbProductList:
                newProduct = unpackProduct(pb_product)
                productList.append(newProduct)
            return productList

        except RpcError:
            printE("Unable to get product list")
            return None

        return None
        


    def requestUserBalance(self, **kwargs):
        """
        string customer_id
        """
        try:
            balanceRequest = com_pb2.BalanceRequest(customer_id = kwargs['customer_id'])
            balanceReply = self.stub.Balance(balanceRequest)
            self.now = balanceReply.now
            return unpackMoney(balanceReply.balance)
        except RpcError:
            printE("Unable to get customer balance")
            return None

        return None


    def requestCounterList(self, **kwargs):
        """No parameters requiered"""
        counterList = []
        try:
            counterListRequest = com_pb2.CounterListRequest()
            counterListReply = self.stub.CounterList(counterListRequest)
            pbCounterList = counterListReply.counters #get the payload
            self.now = counterListReply.now #update the time
            
            for pb_counter in pbCounterList:
                newCounter = unpackCounter(pb_counter)
                counterList.append(newCounter)
            return counterList
            
        except RpcError:
            printE("Unable to get counter list")
            return None

        return None
        

    def requestTransfert(self, **kwargs):
        pass

        
