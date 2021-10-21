# -*- coding:utf-8 -*
from datetime import datetime
import decimal

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship, backref
import sqlalchemy.types as types

from . import Model


class Money(types.TypeDecorator):
    """
        Store fixed decimal values as strings
    """

    impl = types.String

    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value, dialect):
        return decimal.Decimal(value)


class Customer(Model):
    """
        Customer class
        A customer is associated to a NFC card and informs about its balance
    """

    __tablename__ = "customers"
    id = Column(String, primary_key=True, unique=True, autoincrement=False)
    balance = Column(Money)


class Machine(Model):
    """
        Individual machine creating operations
        Used for logging operations
    """

    __tablename__ = "machines"
    uuid = Column(String, primary_key=True, unique=True, autoincrement=False)


class Counter(Model):
    """
        Physical counter during the event
        This refers to the physical location the machine are placed
        This restricts what you can buy on a given machine
    """

    __tablename__ = "counters"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String)


class Product(Model):
    """
        Product available for customers to buy
    """

    __tablename__ = "products"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String)  # Real fancy name
    code = Column(String)  # Slugified name
    category = Column(String)  # Dot separated string for the category main.sub.category
    default_price = Column(Money)

    @property
    def real_unit_price(self) -> decimal.Decimal:
        """
            Return real unit price at the moment it's invoked
            Takes happy hours into account
            If multiple happy hours matches, it gets the first found one
        """
        now = datetime.now()
        for hap in self.happy_hours:
            if now >= hap.start and now <= hap.end:
                return hap.price
        return self.default_price


class HappyHour(Model):
    """
        Reduced price for a given period of time for a specified product
    """

    __tablename__ = "happy_hours"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship(
        "Product", backref=backref("happy_hours", lazy=True), lazy=True
    )
    price = Column(Money)
    start = Column(DateTime(timezone=True))
    end = Column(DateTime(timezone=True))


class ProductAvailableInCounter(Model):
    """
        Link a product with a counter
        Allow to have the same product in multiple counters
    """

    __tablename__ = "products_available_in_counters"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    counter_id = Column(Integer, ForeignKey("counters.id"))
    counter = relationship(
        "Counter", backref=backref("products_available", lazy=True), lazy=True
    )
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship(
        "Product", backref=backref("counters_available", lazy=True), lazy=True
    )


class PaymentMethod(Model):
    """
        Contains payment methods, it's mapped against the ENUM in protobuf files
        Generated at the setup step
    """

    __tablename__ = "payment_methods"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=False)
    name = Column(String)


class Refilling(Model):
    """
        Refill a customer account
    """

    __tablename__ = "refillings"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    customer_id = Column(String, ForeignKey("customers.id"))
    customer = relationship(
        "Customer", backref=backref("refillings", lazy=True), lazy=True
    )

    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"))
    payment_method = relationship(
        "PaymentMethod", backref=backref("refillings", lazy=True), lazy=True
    )

    counter_id = Column(Integer, ForeignKey("counters.id"))
    counter = relationship(
        "Counter", backref=backref("refillings", lazy=True), lazy=True
    )

    machine_id = Column(Integer, ForeignKey("machines.uuid"))
    machine = relationship(
        "Machine", backref=backref("refillings", lazy=True), lazy=True
    )

    amount = Column(Money)
    date = Column(DateTime(timezone=True), default=datetime.utcnow)
    cancelled = Column(Boolean, default=False)

    def __str__(self):
        return (
            "id: %d, cancelled: %d, customer: %s, payment_method: %s, counter: %s, machine: %s, amount: %s, date: %s"
            % (
                self.id,
                self.cancelled,
                self.customer_id,
                self.payment_method,
                self.counter.name,
                self.machine_id,
                self.amount,
                self.date,
            )
        )


class Buying(Model):
    """
        Buying from one or multiple customers at once
        This is a final transaction fixed in time
    """

    __tablename__ = "buyings"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    counter_id = Column(Integer, ForeignKey("counters.id"))
    counter = relationship("Counter", backref=backref("buyings", lazy=True), lazy=True)

    machine_id = Column(Integer, ForeignKey("machines.uuid"))
    machine = relationship("Machine", backref=backref("buyings", lazy=True), lazy=True)

    label = Column(String)
    date = Column(DateTime(timezone=True), default=datetime.utcnow)
    refounded = Column(Boolean, default=False)

    def generate_label(self):
        self.label = ",".join(
            [
                "%s x %d" % (item.product.name, item.quantity)
                for item in self.basket_items
            ]
        )

    def __str__(self):
        return (
            "id: %d, refounded: %d, counter: %s, machine: %s, label: %s, payments: %s, date: %s"
            % (
                self.id,
                self.refounded,
                self.counter.name,
                self.machine_id,
                self.label,
                [str(payment) for payment in self.payments],
                self.date,
            )
        )


class BasketItem(Model):
    """
        One element of a basket associated to a Buying
    """

    __tablename__ = "basket_items"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    buying_id = Column(Integer, ForeignKey("buyings.id"))
    buying = relationship(
        "Buying", backref=backref("basket_items", lazy=True), lazy=True
    )

    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship(
        "Product", backref=backref("basket_items", lazy=True), lazy=True
    )

    quantity = Column(Integer)
    unit_price = Column(Money)  # Unit price of the product at the time of purchase


class Payment(Model):
    """
        Amount spent par each customer involved in a buying
    """

    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    customer_id = Column(String, ForeignKey("customers.id"))
    customer = relationship(
        "Customer", backref=backref("payments", lazy=True), lazy=True
    )

    buying_id = Column(Integer, ForeignKey("buyings.id"))
    buying = relationship("Buying", backref=backref("payments", lazy=True), lazy=True)

    amount = Column(Money)  # Amount spent by this user in the Buying

    def __str__(self):
        return "id: %d, customer: %s, amount: %s" % (
            self.id,
            self.customer_id,
            self.amount,
        )
