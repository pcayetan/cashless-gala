from money import Money
from babel.numbers import format_currency
# money is based on Decimal, this class handle perfect float representation
# every single amount of money should be generated through this library to avoid float virgule problem
# e.g with regular float 1.1 + 1.2 = 2.30000000000000003 
#     with money/Decimal class 1.1 + 1.2 = 2.30

#money could theoricaly handle multi device program, here we just need euro so we create a specialized class

class Eur(Money):

    def __init__(self,amount="0"):
        super().__init__(amount=amount,currency='EUR')
        if isinstance(amount,float) is True:
            printW("Eur should not be instancied with a float number, approximation may occure")
