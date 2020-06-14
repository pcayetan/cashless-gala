
from Console import *

    

class UIProperties:
    def __init__(self):
        self.text = (
            []
        )  # A list because there is several things we may want to show from an Atom (name,price,...)
        self.foreground = None
        self.background = None
        self.icon = None
        self.toolTip = None

    def setTexts(self, text):
        self.text = text
        return self

    def setText(self, text, index):
        self.text[index] = text
        return self

    def setForeground(self, foreground):
        self.foreground = foreground
        return self

    def setBackground(self, background):
        self.background = background
        return self

    def setIcon(self, icon):
        self.icon = icon
        return self

    def setToolTip(self, toolTip):
        self.toolTip = toolTip
        return self

    def getTexts(self):
        return self.text

    def getText(self, index):
        return self.text[index]

    def getForeground(self):
        return self.foreground

    def getBackground(self):
        return self.background

    def getIcon(self):
        return self.icon

    def getToolTip(self):
        return self.toolTip

class Atom:
    def __init__(self):
        self.ui = UIProperties()

    def setTexts(self, text):
        self.ui.setTexts(text)
        return self

    def setText(self, text, index):
        self.ui.setText(text,index)
        return self

    def setForeground(self, foreground):
        self.ui.setForeground(foreground)
        return self

    def setBackground(self, background):
        self.ui.setBackground(background)
        return self

    def setIcon(self, icon):
        self.ui.setIcon(icon)
        return self

    def setToolTip(self, toolTip):
        self.ui.setToolTip(toolTip)
        return self

    def getTexts(self):
        return self.ui.getTexts()

    def getText(self, index):
        return self.ui.getText(index)

    def getForeground(self):
        return self.ui.getForeground()

    def getBackground(self):
        return self.ui.getBackground()

    def getIcon(self):
        return self.ui.getIcon()

    def getToolTip(self):
        return self.ui.getToolTip()

    def getUI(self):
        return self.ui

class HappyHours(Atom):
    
    def __init__(self):
        super().__init__()
        self.start = None # QTime
        self.end = None   # QTime
        self.price = None # Eur
    
    def setStart(self,start):
        self.start = start
        return self

    def setEnd(self, end):
        self.end = end
        return self

    def setPrice(self, price):
        self.price = price
        return self

    def getStart(self):
        return self.start

    def getEnd(self):
        return self.end

    def getPrice(self):
        return self.price

class User(Atom):
    def __init__(self):
        super().__init__()
        self.id = None  # UID of the nfc card
        self.balance = None
        self.canDrink = None

    def setId(self, id):
        self.id = id
        return self

    def setBalance(self, balance):
        self.balance = balance
        return self

    def setCanDrink(self, canDrink):
        self.canDrink = canDrink
        return self

    def getId(self):
        return self.id

    def getBalance(self):
        return self.balance

    def getCanDrink(self):
        return self.canDrink


class Product(Atom):
    def __init__(self):
        super().__init__()
        self.id = None  # int64, used in db
        self.name = None  # pretty print
        self.code = None  # short name
        self.price = None  # The price is either updated when it's in a the selctor, either retreived from database when it's in history
        self.quantity = None  # When product is used as selector, quantity is 1 and when used in a basket, it may vary
        self.happyHours = None # List of happy hours
        self.category = None # string e.g "Drinks.Alcool.Wine"

    def setId(self, id):
        self.id = id
        return self

    def setName(self, name):
        self.name = name
        return self

    def setCode(self, code):
        self.code = code
        return self

    def setPrice(self, price): # price is never a float but something inherited from Decimal (Money.Eur)
        self.price = price
        return self

    def setQuantity(self, quantity):
        self.quantity = quantity
        return self

    def setHappyHours(self,happyHours):
        self.happyHours = happyHours
        return self

    def setCategory(self, category):
        self.category = category
        return self

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def getCode(self):
        return self.code

    def getPrice(self):
        return self.price

    def getQuantity(self):
        return self.quantity

    def getHappyHours(self):
        return self.happyHours

    def getCategory(self):
        return self.category

    def __repr__(self):
        return "Product({0}, {1})".format(self.id,self.name)

    def __str__(self):
        return "{0}: {1}".format(self.id,self.name)


class Operation(Atom):
    def __init__(self):
        super().__init__()
        self.id = None
        self.label = None  # human readable description gave by the server
        self.refounded = None
        # Could be usefull to show where the product has been bought
        self.counterId = None
        self.date = None

    def setId(self, id):
        self.id = id
        return self

    def setLabel(self, label):
        self.label = label
        return self

    def setRefounded(self, refounded):
        self.refounded = refounded
        return self

    def setCounterId(self, counterId):
        self.counterId = counterId
        return self

    def setDate(self, date):
        self.date = date
        return self

    def getId(self):
        return self.id

    def getLabel(self):
        return self.label

    def getRefounded(self, refounded):
        return self.refounded

    def getCounterId(self):
        return self.counterId

    def getDate(self):
        return self.date


class Buying(Operation):
    def __init__(self):
        super().__init__()
        self.price = None  # price the customer(s) actually paid
        self.payments = None  # List of all payment for this order since several users maybe concerned
        self.basketItems = None  # List of "Product", their unit price should be download from the history

    def setPrice(self, price):
        self.price = price
        return self

    def setPayment(self, payments):
        self.payments = payments
        return self

    def setBasketItems(self, basketItems):
        self.basketItems = basketItems
        return self

    def getPrice(self):
        return self.price

    def getPayments(self):
        return self.payments

    def getBasketItems(self):
        return self.basketItems


class Refilling(Operation):
    def __init__(self):
        super().__init__()
        self.amount = None
        self.newBalance = None

    def setAmount(self, amount):
        self.amount = amount
        return self

    def getAmount(self):
        return self.amount

    def setNewBalance(self, balance):
        self.newBalance = balance
        return self
    
    def getNewBalance(self):
        return self.newBalance


class Counter(Atom):
    def __init__(self):
        super().__init__()
        self.id = None
        self.name = None

    def setId(self, id):
        self.id = id
        return self

    def setName(self, name):
        self.name = name
        return self

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def __repr__(self):
        return "Counter({0}, {1})".format(self.id,self.name)

    def __str__(self):
        return "{0}: {1}".format(self.id,self.name)

class Distribution(Atom):
    def __init__(self):
        super().__init__()
        self.userList = [] # list of user uid
        self.userBalance = [] # the current balance of each user before transaction
        self.amount = [] # the amount paid by each user
        self.totalPrice = None # The total price to pay
    
    def setUserList(self,uidList):
        self.userList = uidList
        return self

    def getUserList(self):
        return self.userList

    def addUser(self,uid):
        self.userList.append(uid)
        return self

    def removeUser(self,uid):
        try:
            indexUser = self.userList.index(uid)
            del(self.userList[indexUser])
            return self
        except ValueError:
            printE("User {} not found".format(uid))
            return None

    def setUserBalanceList(self, balanceList):
        self.userBalance = balanceList
        return self

    def getUserBalanceList(self):
        return self.userBalance

    def setUserBalance(self, uid, balance):
        try:
            indexUser = self.userList.index(uid)
            self.userBalance[indexUser] = balance
        except ValueError:
            printE("User {} not found".format(uid))
            return None

    def getUserBalance(self, uid):
        try:
            indexUser = self.userList.index(uid)
            return self.userBalance[indexUser] 
        except ValueError:
            printE("User {} not found".format(uid))
            return None

    def setAmountList(self, amountList):
        self.amount

    def setUserAmount(self, uid, amount):
        try:
            userIndex = self.userList.index(uid)
            if amount <= self.userBalance[userIndex]:
                self.amount[userIndex] = amount
            else:
                printWW("Insufficient balance for user {}".format(uid))
                self.amount[userIndex]  = self.userBalance[userIndex]
        except ValueError:
            printE("user {} not found".format(uid))

    def getAmountList(self):
        return self.amount

    def getUserAmount(self, uid):
        try:
            userIndex = self.userList.index(uid)
            return self.amount[userIndex]
        except ValueError:
            printE("user {} not found".format(uid))


    def setFairDistribution(self):
        pass