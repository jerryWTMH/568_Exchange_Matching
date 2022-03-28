from io import BytesIO

from lxml import etree


class Position:
    def __init__(self, sym, account_id, shares):
        self.sym = sym
        self.account_id = account_id
        self.shares = shares

    def __str__(self):
        return 'Position(account_id = ' + self.account_id + ',' + \
               'sym = ' + self.sym + ',' + \
               'shares = ' + self.shares + \
               ')\n'
               
    def getClassName(self):
        return "Position"

    def toSQL(self):
        return "INSERT INTO POSITION(account_id, symbol, shares) VALUES(" + self.account_id + " , '" + self.sym + "', " + self.shares + ")"


class Account:
    def __init__(self, account_id, balance):
        self.balance = balance
        self.account_id = account_id

    def __str__(self):
        return 'Account(account_id = ' + self.account_id + ',' +\
                    'balance = ' + self.balance + \
                    ')\n'     

    def getClassName(self):
        return "Account"

    def toSQL(self):
        return "INSERT INTO ACCOUNT(account_id, balance) VALUES(" + self.account_id + " , " + self.balance + ")"

class Order:
    def __init__(self, account_id, amount, limit, symbol):
        self.account_id = account_id
        self.amount = amount
        self.limit = limit
        self.symbol = symbol

    def __str__(self):
        return 'Order(account_id = ' + self.account_id + ',' +\
                    'amount = ' + self.amount + ',' +\
                    'limit = ' + self.limit + ',' +\
                    'symbol = ' + self.symbol + \
                    ')\n'

    def getClassName(self):
        return "Order"

    def toSQL(self):
        sql = "INSERT INTO TRANSACTION(account_id, alives, amount, limitation, symbol) VALUES(" + self.account_id + " , " + "TRUE" + " , " + self.amount + " , " + self.limit + " , '" + self.sym + "');" 
                      ### PROBLEM ### "INSERT INTO HISTORY()"


class Query:
    def __init__(self, transaction_id):
        self.transaction_id = transaction_id

    def __str__(self):
        return 'Query(transaction_id = ' + self.transaction_id + ')\n'
    def getClassName(self):
        return "Query"
    def toSQL(self):
        return "SELECT * FROM TRANSACTION WHERE TRANSACTION.transaction_id = " + self.transaction_id


class Cancel:
    def __init__(self, transaction_id):
        self.transaction_id = transaction_id

    def __str__(self):
        return 'Cancel(transaction_id = ' + self.transaction_id + ')\n'
    
    def getClassName(self):
        return "Cancel"

    def toSQL(self):
        var_a = "SELECT price FROM wheee........."
        sql = "DELETE * FROM TRANSACTION WHERE TRANSACTION.transaction_id = " + self.transaction_id + ";" +
            ### PROBLEM ### "INSERT INTO HISTORY(transaction_id, status, history_shares, price) VALUES(" +  transaction_id + " , '" + "cancel" + "' , " + var_a +  


class Execution:
    def __init__(self):
        self.executions = []

    def __str__(self):
        # str = "Display Excecution!\n"
        str = ""
        for element in self.executions:
            str += element.__str__()
        return str

    def getClassName(self):
        return "Execution"

    def toSQL(self):
        return "Execution"


def parse_xml(recv_string):
    # recv_string is the string received;
    root = etree.fromstring(recv_string)
    # execution is the execution to be handled(create, transaction)
    execution = Execution()
    # classify by the root element
    # if the root element is create
    if root.tag == 'create':
        for child in root:
            if child.tag == 'account':
                account_id = child.attrib.get('id')
                balance = child.attrib.get('balance')
                account = Account(account_id,balance)
                execution.executions.append(account)
            if child.tag == 'symbol':
                sym = child.attrib.get('sym')
                # parse the position nested in child
                for grandchild in child:
                    account_id = grandchild.attrib.get('id')
                    share = grandchild.text
                    position = Position(sym, account_id, share)
                    execution.executions.append(position)

    # if the root element is transactions
    if root.tag == 'transactions':
        # this is the account for transaction
        account_id = root.attrib.get('id')
        for child in root:
            if child.tag == 'order':
                symbol = child.attrib.get('sym')
                amount = child.attrib.get('amount')
                limit = child.attrib.get('limit')
                order = Order(account_id, amount, limit, symbol)
                execution.executions.append(order)
            if child.tag == 'query':
                id = child.attrib.get('id')
                query = Query(id)
                execution.executions.append(query)
            if child.tag == 'cancel':
                id = child.attrib.get('id')
                cancel = Cancel(id)
                execution.executions.append(cancel)
    return execution


# this is used for test
if __name__ == '__main__':
    create_string = "<create> " \
                  "<account id=\"123456\" balance=\"1000\"/>" \
                      "<symbol sym=\"SPY\">" \
                      "<account id=\"123456\">100000</account>" \
                      "</symbol>" \
                      "<symbol sym=\"NASDAQ\">" \
                      "<account id=\"654321\">50</account>" \
                      "</symbol>" \
                  "<account id=\"13579\" balance=\"10000\"/>" \
                    "</create>"
    create_execution = parse_xml(create_string)
    print(create_execution)
    transaction_string = "<transactions id=\"123456\">" \
                            "<order sym=\"SPY\" amount=\"123\" limit=\"321\"/>" \
                            "<query id=\"1\"/>" \
                            "<cancel id=\"1\"/>" \
                          "</transactions> "
    transaction_execution = parse_xml(transaction_string)
    print(transaction_execution)


