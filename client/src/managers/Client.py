from __future__ import print_function
import grpc
from grpc import RpcError
import com_pb2
import com_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp

# OPTINAL FOR PINGING THE SERVER AND ENSURE IT'S AVAILABLE
import platform  # For getting the operating system name
import subprocess  # For executing a shell command

# Project specific imports
from convert import *
from Console import *


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = "-n" if platform.system().lower() == "windows" else "-c"

    # Building the command. Ex: "ping -c 1 google.com"
    command = ["ping", param, "1", host]

    return subprocess.call(command) == 0


class ClientSingleton(type):
    _instance = {}

    def __call__(cls):
        if cls not in cls._instance:
            cls._instance[cls] = super(ClientSingleton, cls).__call__()
        return cls._instance[cls]


class Client(metaclass=ClientSingleton):
    def __init__(self):
        self.serverAddress = "127.0.0.1:50051"
        self.channel = grpc.insecure_channel(self.serverAddress)
        self.stub = com_pb2_grpc.PaymentProtocolStub(self.channel)
        self.now = None  # datetime

    def setServerAddress(self, address):
        self.serverAddress = address
        # TODO: add ping test here
        # TODO: Test address format
        self.channel = grpc.insecure_channel(self.serverAddress)
        self.stub = com_pb2_grpc.PaymentProtocolStub(self.channel)

    def requestBuy(self, **kwargs) -> Buying:
        """
    int64 counter_id
    string device_uuid
    repeated Payment payments
    repeated BasketItem basket
        """
        try:
            payments = kwargs["payments"]
            basket = kwargs["basket"]
            newPayments = []
            newBasket = []

            for qProduct in basket:
                product = qProduct.getAtom()
                newBasket.append(packProduct(product))

            kwargs["basket"] = newBasket
            kwargs["payments"] = packDistribution(kwargs["payments"])

            buyingRequest = com_pb2.BuyingRequest(**kwargs)
            buyingReply = self.stub.Buy(buyingRequest)
            self.now = unpackTime(buyingReply.now)
            if buyingReply.status == com_pb2.BuyingReply.SUCCESS:
                transaction = buyingReply.transaction
                buying = unpackBuying(transaction)
            elif buyingReply.status == com_pb2.BuyingReply.NOT_ENOUGH_MONEY:
                printW("Not enough money")
                return None

            return buying

        except RpcError:
            pass

    def requestRefilling(self, **kwargs) -> Refilling:
        """
        string customer_id
        int64 counter_id
        string device_uuid
        int payment_method
        Eur amount
        """
        try:
            paymentMethodList = [
                com_pb2.UNKNOWN,
                com_pb2.CASH,
                com_pb2.CARD,
                com_pb2.CHECK,
                com_pb2.AE,
                com_pb2.TRANSFER,
                com_pb2.OTHER,
            ]
            kwargs["payment_method"] = paymentMethodList[kwargs["payment_method"]]
            kwargs["amount"] = packMoney(kwargs["amount"])
            refillingRequest = com_pb2.RefillingRequest(**kwargs)
            refillingReply = self.stub.Refill(refillingRequest)
            if refillingReply.status == com_pb2.RefillingReply.SUCCESS:
                self.now = unpackTime(refillingReply.now)
                newBalance = unpackMoney(refillingReply.customer_balance)
                refilling = unpackRefilling(refillingReply.refilling)
                refilling.setNewBalance(newBalance)
                return refilling
            else:
                printE("Unable to refill")
                return None
        except RpcError:
            printE("RPC: Unable to refill")
            return None

    def requestHistory(self, **kwargs):
        """
        HistoryType type (enum)
        RefoundStatus refounded (enum)
        # Optional fields
        uint64 counter_id
        string customer_id
        string device_uuid
        uint64 max_history_size (0: no limit)
        """
        buyings = []
        refillings = []

        requestType = [com_pb2.HistoryRequest.BUYINGS, com_pb2.HistoryRequest.REFILLINGS]
        refoundStatus = [
            com_pb2.HistoryRequest.NOT_SPECIFIED,
            com_pb2.HistoryRequest.NOT_REFOUNDED,
            com_pb2.HistoryRequest.REFOUNDED,
        ]
        try:
            historyRequest = com_pb2.HistoryRequest(**kwargs)
            historyReply = self.stub.History(historyRequest)
            if historyReply.status == com_pb2.HistoryReply.SUCCESS:
                for buying in historyReply.buyings:
                    buyings.append(unpackBuying(buying))
                for refilling in historyReply.refillings:
                    refillings.append(unpackRefilling(refilling))
                return buyings, refillings
            else:
                return None
        except RpcError:
            pass

    def requestRefund(self, **kwargs):
        """
        int64 buying_id
        """

        try:
            refoundBuyingRequest = com_pb2.RefoundBuyingRequest(**kwargs)
            refoundBuyingReply = self.stub.RefoundBuying(refoundBuyingRequest)
            if refoundBuyingReply.status == com_pb2.RefoundBuyingReply.SUCCESS:
                self.now = unpackTime(refoundBuyingReply.now)
                return True
            else:
                printE("Unable to refound: {}".format(refoundBuyingReply.status))
                return None

        except RpcError:
            printE("RPC: Unable to refound")
            return None

    def requestCounterProduct(self, **kwargs) -> [Product]:
        """
        int64 counter_id
        """
        productList = []
        try:
            productsRequest = com_pb2.ProductsRequest(**kwargs)
            productsReply = self.stub.Products(productsRequest)
            if productsReply.status == com_pb2.ProductsReply.SUCCESS:
                self.now = unpackTime(productsReply.now)
                # Fill product List
                pbProductList = productsReply.products  # get protobuff products
                for pb_product in pbProductList:
                    newProduct = unpackProduct(pb_product)
                    productList.append(newProduct)
                return productList
            else:
                printE("Unable to get product list")
                return None

        except RpcError:
            printE("RPC: Unable to get product list")
            return None

        return None

    def requestUserBalance(self, **kwargs) -> Eur:
        """
        string customer_id
        """
        try:
            balanceRequest = com_pb2.BalanceRequest(customer_id=kwargs["customer_id"])
            balanceReply = self.stub.Balance(balanceRequest)
            self.now = unpackTime(balanceReply.now)
            return unpackMoney(balanceReply.balance)
        except RpcError:
            printE("Unable to get customer balance")
            return None

        return None

    def requestCounterList(self, **kwargs) -> [Counter]:
        """No parameters requiered"""
        counterList = []
        try:
            counterListRequest = com_pb2.CounterListRequest()
            counterListReply = self.stub.CounterList(counterListRequest)
            pbCounterList = counterListReply.counters  # get the payload
            self.now = unpackTime(counterListReply.now)  # update the time

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

    def requestCancelRefilling(self, **kwargs):
        """
        uint64 refilling_id
        """

        try:
            cancelRefillingRequest = com_pb2.CancelRefillingRequest(**kwargs)
            cancelRefillingReply = self.stub.CancelRefilling(cancelRefillingRequest)
            if cancelRefillingReply.status == com_pb2.CancelRefillingReply.SUCCESS:
                self.now = unpackTime(cancelRefillingReply.now)
                return True
            else:
                printE("Unable to refound: {}".format(cancelRefillingReply.status))
                return None
        except RpcError:
            printE("RPC: Unable to cancel refilling")
            return None