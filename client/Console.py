from termcolor import colored
from babel.numbers import format_currency

# At the moment I assume we only print single strings
def printE(string): #Error
    print(colored("ERROR: " + str(string),'red'))

def printW(string): #Warning
    print(colored("WARNING: " + str(string),'yellow'))

def printWW(string): #Super Warning
    print(colored("WARNING: " + str(string),'yellow',attrs=['bold']))

def printN(string): #Nice
    print(colored(str(string),'green'))

def printD(string): #Debug
    print(colored("DEBUG: "+ str(string),''))

def printI(string): #Info
    print(colored(string, 'cyan'))

def printNFC(string): #NFC message
    print(colored(string,'magenta'))

def printM(eur): #Money
    print(colored(eur.format('fr_FR'),'yellow'))

#Suggestion: create printEE, printEEE, printWW, printWWW ... to create a hierarchy among the message
#            could be usefull to filter the message to print in the future ...

#Suggestion: create a singleton class to handle all of these...