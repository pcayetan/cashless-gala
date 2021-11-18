from __future__ import print_function
from typing import Optional
import grpc
from grpc import RpcError
from google.protobuf.timestamp_pb2 import Timestamp
import logging

import src.managers.com.com_pb2
import src.managers.com.com_pb2_grpc

# OPTINAL FOR PINGING THE SERVER AND ENSURE IT'S AVAILABLE
import platform  # For getting the operating system name
import subprocess  # For executing a shell command

import time
import pytz
from datetime import datetime, timedelta

# Project specific imports
from src.managers.com.convert import *

# Temporary solution to let 'user' change server address
import sys
from pathlib import Path


log = logging.getLogger()


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

        # TEMPORARY
        # I don't want QDataManager here so I get the root path myself here
        if getattr(sys, "frozen", False):
            # If the program has been frozen by cx_freeze
            self.rootDir = Path(sys.executable).absolute().parents[0]
        else:
            self.rootDir = Path(__file__).absolute().parents[2]
        # END TEMPORARY

        self.connectToServer(loadFromSettings=True)

        # Time management
        # Default timezone, this will be override from requests
        self.timezone = pytz.utc
        # This will be updated from requests
        self.timestamp = datetime(
            1970, 1, 1, tzinfo=self.timezone
        )  # Works because pytz.utc is compatible
        self.t0 = pytz.utc.localize(datetime.utcnow()).astimezone(self.timezone)

    def connectToServer(self, loadFromSettings=False):
        def _establishConnection(ip, timeout=1) -> Optional[grpc.Channel]:
            from src.gui.widgets.QForms import QIpInputDialog

            if not QIpInputDialog.isIPValid(ip):
                return None

            channel = grpc.insecure_channel(ip)
            try:
                grpc.channel_ready_future(channel).result(timeout=timeout)
            except grpc.FutureTimeoutError as e:
                logging.error(f"Could not connect to server with address {ip}: {e}")
                return None
            return channel

        # Read server address
        from src.gui.widgets.QForms import QIpInputDialog

        inputDialog = QIpInputDialog()

        serverSettings = self.rootDir / Path("data/server")
        if loadFromSettings and serverSettings.exists():
            # Pre-load from settings
            with open(serverSettings, "r") as file:
                address = file.readline().strip()
        else:
            # Ask user
            if inputDialog.exec() != 1:
                # NOTE: This exit produces undesired behavior when used from the menu
                exit(0)
            address = inputDialog.textValue()

        # Check connection and ask user if address is unreachable
        channel = _establishConnection(address)
        while channel is None:
            if inputDialog.exec() != 1:
                exit(0)
            address = inputDialog.textValue()
            channel = _establishConnection(address)

        # Save settings
        with open(serverSettings, "w+") as file:
            file.write(address)

        self.serverAddress = address
        self.channel = channel
        self.stub = com_pb2_grpc.PaymentProtocolStub(self.channel)

    def getTime(self) -> datetime:
        return self.timestamp + (
            pytz.utc.localize(datetime.utcnow()).astimezone(self.timezone) - self.t0
        )

    def updateTime(self, protoTime: com_pb2.Time):
        self.timezone = pytz.timezone(protoTime.timezone)
        self.t0 = pytz.utc.localize(datetime.utcnow()).astimezone(self.timezone)
        self.timestamp = unpackTime(protoTime)

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
            self.updateTime(buyingReply.now)
            if buyingReply.status == com_pb2.BuyingReply.SUCCESS:
                transaction = buyingReply.transaction
                buying = unpackBuying(transaction)
            elif buyingReply.status == com_pb2.BuyingReply.NOT_ENOUGH_MONEY:
                log.warning("Not enough money")
                return None
            elif buyingReply.status == com_pb2.BuyingReply.MISSING_AMOUNT_IN_PAYMENT:
                log.error("Incorrect item price")
                return None
            else:
                log.error("Bad buying request")
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
                com_pb2.NOT_PROVIDED,
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
                self.updateTime(refillingReply.now)
                newBalance = unpackMoney(refillingReply.customer_balance)
                refilling = unpackRefilling(refillingReply.refilling)
                refilling.setNewBalance(newBalance)
                return refilling
            else:
                log.error("Unable to refill")
                return None
        except RpcError:
            log.error("RPC: Unable to refill")
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

        requestType = [
            com_pb2.HistoryRequest.BUYINGS,
            com_pb2.HistoryRequest.REFILLINGS,
        ]
        refoundStatus = [
            com_pb2.HistoryRequest.NOT_SPECIFIED,
            com_pb2.HistoryRequest.NOT_REFOUNDED,
            com_pb2.HistoryRequest.REFOUNDED,
        ]
        try:
            historyRequest = com_pb2.HistoryRequest(**kwargs)
            historyReply = self.stub.History(historyRequest)
            if historyReply.status == com_pb2.HistoryReply.SUCCESS:
                self.updateTime(historyReply.now)
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
                self.updateTime(refoundBuyingReply.now)
                return True
            else:
                log.error("Unable to refound: {}".format(refoundBuyingReply.status))
                return None

        except RpcError:
            log.error("RPC: Unable to refound")
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
                self.updateTime(productsReply.now)
                # Fill product List
                pbProductList = productsReply.products  # get protobuff products
                for pb_product in pbProductList:
                    newProduct = unpackProduct(pb_product)
                    productList.append(newProduct)
                return productList
            else:
                log.error("Unable to get product list")
                return None

        except RpcError:
            log.error("RPC: Unable to get product list")
            return None

        return None

    def requestUserBalance(self, **kwargs) -> Eur:
        """
        string customer_id
        """
        try:
            balanceRequest = com_pb2.BalanceRequest(customer_id=kwargs["customer_id"])
            balanceReply = self.stub.Balance(balanceRequest)
            self.updateTime(balanceReply.now)
            return unpackMoney(balanceReply.balance)
        except RpcError:
            log.error("Unable to get customer balance")
            return None

        return None

    def requestCounterList(self, **kwargs) -> [Counter]:
        """No parameters requiered"""
        counterList = []
        try:
            counterListRequest = com_pb2.CounterListRequest()
            counterListReply = self.stub.CounterList(counterListRequest)
            pbCounterList = counterListReply.counters  # get the payload
            self.updateTime(counterListReply.now)  # update the time

            for pb_counter in pbCounterList:
                newCounter = unpackCounter(pb_counter)
                counterList.append(newCounter)
            return counterList

        except RpcError:
            log.error("Unable to get counter list")
            return None

        return None

    def requestTransfert(self, **kwargs):
        """
        string origin_id = 1;
        string destination_id = 2;
        Eur amount = 3;
        uint64 counter_id = 4;
        string device_uuid = 5;
        """
        try:
            kwargs["amount"] = packMoney(kwargs["amount"])
            transfertRequest = com_pb2.TransfertRequest(**kwargs)
            transfertReply = self.stub.Transfert(transfertRequest)

            if transfertReply.status == com_pb2.TransfertReply.SUCCESS:
                self.updateTime(transfertReply.now)
                return True
            else:
                log.error("Unable to transfer: {}".format(transfertReply.status))
                return None
        except RpcError:
            log.error("RPC: Unable to transfer")
            return None

    def requestCancelRefilling(self, **kwargs):
        """
        uint64 refilling_id
        """

        try:
            cancelRefillingRequest = com_pb2.CancelRefillingRequest(**kwargs)
            cancelRefillingReply = self.stub.CancelRefilling(cancelRefillingRequest)
            if cancelRefillingReply.status == com_pb2.CancelRefillingReply.SUCCESS:
                self.updateTime(cancelRefillingReply.now)
                return True
            else:
                log.error("Unable to refound: {}".format(cancelRefillingReply.status))
                return None
        except RpcError:
            log.error("RPC: Unable to cancel refilling")
            return None
