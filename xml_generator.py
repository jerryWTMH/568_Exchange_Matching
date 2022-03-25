from io import BytesIO

from lxml import etree

class Error:
    def __init__(self,attributes,message):
        #attributes should be a hashmap [attribute] -> [attribute value]
        #Possible attributes: sym,amount,limit,id
        self.attributes = attributes
        self.message = message


class CreateResponse:
    def __init__(self, account_id, sym):
        #sym might be null for account creation
        self.account_id = id
        self.sym = sym


class QueryResponse:
    def __init__(self, transaction_id, shares, time, price):
        self.transaction_id = transaction_id
        self.shares = shares
        self.time = time
        self.price = price


class CancelResponse:
    def __init__(self, transaction_id, shares, time, price):
        self.transaction_id = transaction_id
        self.shares = shares
        self.time = time
        self.price = price



class TransactionResponse:
    def __init__(self, trans_id, type):
        self.trans_id = trans_id
        self.type = type


class ResultWrapper:

    def __init__(self):
        self.results = []
    #
    def generate_xml(self):
        root = etree.Element('results')
        # for result in self.results:


# Server:
#     parseXML(string:xml).handle().generateXML()
    #server logic
    #sql generator /filter
    #testcases

    #parseXML:return a series of executables that are independent with each other
    #handle:return a wrapper, which contains a serious of objects
    #generateXML(): it's the method of wrapper, generate
