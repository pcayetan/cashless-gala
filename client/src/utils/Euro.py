from money import Money
from babel.numbers import format_currency
import logging

# money is based on Decimal, this class handle perfect float representation
# every single amount of money should be generated through this library to avoid float virgule problem
# e.g with regular float 1.1 + 1.2 = 2.30000000000000003
#     with money/Decimal class 1.1 + 1.2 = 2.30


# money could theoricaly handle multi device program, here we just need euro so we create a specialized class


class Eur(Money):
    def __init__(
        self, amount="0", currency="EUR"
    ):  # the currency parameter is here just to make this class compatible with money __add__ __sub__...
        super().__init__(amount=amount, currency="EUR")
        if isinstance(amount, float) is True:
            log.warning(
                "Eur should not be instancied with a float number, approximation may occure"
            )
            if self.as_tuple().exponent < -2:
                log.warning(
                    "Money with more than two decimals. Unforseen behavior may occure"
                )

    # Overloaded function ... allow me to use XX.YY€ instead of EUR XX.YY
    def __str__(self):
        try:
            return self.format("fr_FR")
        except Exception:
            return self.__unicode__()

    def __unicode__(self):
        return u"{} {:,.2f}".format(self._currency, self._amount)

    def __mul__(self, other):
        if isinstance(other, Eur):
            raise TypeError("multiplication is unsupported between two money objects")
        amount = self._amount * other
        return self.__class__(amount)

    def as_tuple(self):
        return self._amount.as_tuple()

    def getExponent(self):
        return self.as_tuple().exponent
