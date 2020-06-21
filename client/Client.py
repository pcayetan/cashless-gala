from __future__ import print_function

import grpc
from grpc import RpcError
import com_pb2
import com_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from Console import *

from convert import *

# OPTINAL FOR PINGING THE SERVER AND ENSURE IT'S AVAILABLE
import platform    # For getting the operating system name
import subprocess  # For executing a shell command

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0

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
    
    def setServerAddress(self, address):
        self.serverAddress = address
        #TODO: add ping test here
        #TODO: Test address format
        self.channel = grpc.insecure_channel(self.serverAddress)
        self.stub = com_pb2_grpc.PaymentProtocolStub(self.channel)

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

        
