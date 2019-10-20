from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

import json

# For handle request MaxRetry exception
from urllib3.exceptions import *

import uuid


class MachineConfigSingleton(type(swagger_client.Configuration)):
    _instance = {}

    def __call__(cls):
        if cls not in cls._instance:
            cls._instance[cls] = super(MachineConfigSingleton, cls).__call__()
        return cls._instance[cls]


class MachineConfig(swagger_client.Configuration, metaclass=MachineConfigSingleton):
    def __init__(self):
        super().__init__()
        self.counterID = 1
        self.host = "http://127.0.0.1:5000"
        self.defaultItemFileName = "ItemModel.json"

    def setHost(host):
        self.host = host

    def setCounterID(counterID):
        self.counterID = counterID


configuration = MachineConfig()

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))


def requestBuy(userUID, counterID, computerMAC, basket):
    # basket format conversion

    if isinstance(basket, dict) is True:
        fBasket = []
        for i in basket:
            tempDict = {}
            tempDict["product_code"] = i
            tempDict["quantity"] = basket[i]
            fBasket.append(tempDict)
    else:
        fBasket = basket

    try:
        body = swagger_client.Body(counterID, computerMAC, fBasket)
        return api_instance.buy_user_uid_post(body, userUID)
    except ApiException as e:
        if e.status == 401:
            print("User {}: Insufficient balance".format(userUID))
        elif e.status == 404:
            print("User {}: Not found".format(userUID))
        return None
    except MaxRetryError as e:
        return None


def requestRefilling(userUID, counterID, computerMAC, amount):
    try:
        body = swagger_client.Body1(counterID, computerMAC, amount)
        return api_instance.refilling_user_uid_post(body, userUID)
    except MaxRetryError:
        return None


def requestGeneralHistory(historySize):
    raise NotImplementedError


def requestUserHistory(userUID, historySize):
    try:
        return api_instance.get_user_history_user_uid_history_size_post(historySize, userUID)
    except ApiException as e:
        return None
    except MaxRetryError as e:
        print("Unable to establish connexion with the server")
        return None


def requestCounterHistory(counterID, historySize):
    try:
        return api_instance.get_counter_history_counter_id_history_size_post(historySize, counterID)
    except ApiException as e:
        return None
    except MaxRetryError as e:
        print("Unable to establish connexion with the server")
        return None


def requestComputerHistory(computerMAC, historySize):
    try:
        return api_instance.get_computer_history_computer_mac_history_size_post(historySize, computerMAC)
    except ApiException as e:
        return None
    except MaxRetryError:
        return None


def requestRefund(transactionID, counterID, computerMAC):
    try:
        body = swagger_client.Body2(counterID, computerMAC)
        return api_instance.refund_transaction_id_post(body, transactionID)
    except ApiException as e:
        if e.status == 404:
            print("Refund failed: Transaction not found")
        return None
    except MaxRetryError:
        return None


def requestCounterProduct(counterID):
    try:
        return api_instance.get_counter_products_counter_id_post(counterID)
    except ApiException as e:
        print("Counter product request failed: Counter not found")
    except MaxRetryError:
        return None


def requestUserBalance(uid):
    try:
        return api_instance.get_user_balance_user_uid_post(uid)
    except ApiException as e:
        if e.status == 404:
            print("User {} not found".format(uid))
        return None
    except MaxRetryError as e:
        return None
