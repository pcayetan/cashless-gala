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


class User(Atom):
    def __init__(self):
        super().__init__()
        self.id = None  # UID of the nfc card
        self.balance = None
        self.canDrink = None

    def setId(self, id):
        self.id = id

    def setBalance(self, balance):
        self.balance = balance

    def setCanDrink(self, canDrink):
        self.canDrink = canDrink

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

    def setId(self, id):
        self.id = id

    def setName(self, name):
        self.name = name

    def setCode(self, code):
        self.code = code

    def setPrice(self, price):
        self.price = price

    def setQuantity(self, quantity):
        self.quantity = quantity

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

    def setLabel(self, label):
        self.label = label

    def setRefounded(self, refounded):
        self.refounded = refounded

    def setCounterId(self, counterId):
        self.counterId = counterId

    def setDate(self, date):
        self.date = date

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
        self.price = print

    def setPayment(self, payments):
        self.payments = payments

    def setBasketItems(self, basketItems):
        self.basketItems = basketItems

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

    def setAmount(self, amount):
        self.amount = amount

    def getAmount(self):
        return self.amount


class Counter(Atom):
    def __init__(self):
        super().__init__()
        self.id = None
        self.name = None

    def setId(self, id):
        self.id = id

    def setName(self, name):
        self.name = name

    def getId(self):
        return self.id

    def getName(self):
        return self.name
