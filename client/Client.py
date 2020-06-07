
from __future__ import print_function

import grpc
from grpc import RpcError
import com_pb2
import com_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.json_format import MessageToDict
from Atoms import *
from Console import *

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
        # Mockup
        mockupProduct = Product()
        mockupProduct.price = 8
        mockupProduct.quantity = 2
        mockupProduct.name = "Bouteille"
        mockupProduct.id = 0
        mockupProduct.code = "BOUBOU"

        buying = Buying()
        buying.date = Timestamp().GetCurrentTime()
        buying.id = 1
        buying.label = "label"
        buying.price = 16
        buying.refounded = False
        buying.counterId = 0
        buying.basketItems = [mockupProduct]

        return mockupProduct


    def requestRefilling(self, **kwargs):
        """
        string customer_id
        int64 counter_id
        string device_uuid
        PaymentMethod payment_method
        double amount
        """

        # Mockup
        refilling = Refilling()
        refilling.amount = 42
        refilling.counterId = 0
        refilling.date = Timestamp().GetCurrentTime()
        refilling.id = 2
        refilling.label = "label"
        refilling.refounded = False

        return refilling


    def requestHistory(self, **kwargs):
        pass


    def requestRefund(self, **kwargs):
        pass


    def requestCounterProduct(self, **kwargs):
        """
        int64 counter_id
        """
        counterProduct = {}

        try:
            productsRequest = com_pb2.ProductsRequest(counter_id=kwargs['counter_id'])
            productsReply = self.stub.Products(productsRequest)

            self.now = productsReply.now
            return MessageToDict(productsReply)['items']
        except RpcError:
            printE("Unable to get product list")
            return None



        # Mockup
        mockupProduct1 = Product()
        mockupProduct1.name = "Coca"
        mockupProduct1.price = 1
        mockupProduct1.quantity = 1
        mockupProduct1.id = 0
        mockupProduct1.code = "COCA"

        mockupProduct2 = Product()
        mockupProduct2.name = "Bièrre"
        mockupProduct2.price = 2
        mockupProduct2.quantity = 1
        mockupProduct2.id = 1
        mockupProduct2.code = "BIBINE"

        products = {"Soft": mockupProduct1, "Alcool": mockupProduct2}

        return products


    def requestUserBalance(self, **kwargs):
        """
        string customer_id
        """
        # Mockup
        return 30


    def requestCounterList(self, **kwargs):
        """No parameters requiered"""
        counterList = []
        counterListRequest = com_pb2.CounterListRequest()
        try:
            counterListReply = self.stub.CounterList(counterListRequest)
            grpcCounterList = counterListReply.counters #get the payload
            self.now = counterListReply.now #update the time
            
            for i in grpcCounterList:
                newCounter = Counter()
                newCounter.setId(i.id)
                newCounter.setName(i.name)
                counterList.append(newCounter)
            return counterList
            
        except RpcError:
            printE("Unable to get counter list")
            return None
        

    def requestTransfert(self, **kwargs):
        pass
