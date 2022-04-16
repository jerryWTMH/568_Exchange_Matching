from io import BytesIO

from lxml import etree
import psycopg2
import xml_generator as xml_generator


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

    def toSQL(self, conn):
        sql = "INSERT INTO POSITION(account_id, symbol, shares) VALUES(" + self.account_id + " , '" + self.sym + "', " + self.shares + ");"
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()


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

    def toSQL(self, conn):
        sql = "INSERT INTO ACCOUNT(account_id, balance) VALUES(" + self.account_id + " , " + self.balance + ");"
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

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

    def toSQL(self, conn):
        sql = "INSERT INTO TRANSACTION(account_id, alive, amount, limitation, symbol) VALUES(" + self.account_id + " , " + "TRUE" + " , " + self.amount + " , " + self.limit + " , '" + self.symbol + "');"
        cur = conn.cursor()
        cur.execute(sql)

        sql = "SELECT currval(pg_get_serial_sequence('TRANSACTION','transaction_id'));"
        cur.execute(sql)
        result = cur.fetchone()
        ### At the mean time, we need to add new order into HISTORY!
        sql = "INSERT INTO HISTORY(transaction_id, account_id, status, history_shares, price, symbol) VALUES(" + str(result[0]) + " , " + self.account_id + " , " + "TRUE" + " , " + self.amount + " , " + self.limit + " , '" + self.symbol + "');"
        cur.execute(sql)
        conn.commit()

        
class QueryHelper:
    def __init__(self, transaction_id, conn):
        self.transaction_id = transaction_id
        self.conn = conn
        self.query_results = []

    def query(self):
        sql = "SELECT * FROM HISTORY WHERE transaction_id =" + self.transaction_id;
        cur = self.conn.cursor()
        cur.execute(sql)
        history_results = cur.fetchall()
        for history_result in history_results:
            status = history_result[3]
            share = history_result[5]
            time = history_result[4]
            price = history_result[6]
            if status == "open":
                open_sub_transaction = xml_generator.SubTransaction("Open",share,price,time)
                self.query_results.append(open_sub_transaction)
            elif status == "cancel":
                cancel_transaction = xml_generator.SubTransaction("Cancel",share,price,time)
                self.query_results.append(cancel_transaction)
            elif status == "executed":
                executed_transaction = xml_generator.SubTransaction("Executed",share,price,time)
                self.query_results.append(executed_transaction)
        return self.query_results
    # return list of subtransactions
    # eg:[open,cancel,executed]

class Query:
    def __init__(self, transaction_id):
        self.transaction_id = transaction_id

    def __str__(self):
        return 'Query(transaction_id = ' + self.transaction_id + ')\n'

    def getClassName(self):
        return "Query"

class Cancel:
    def __init__(self, transaction_id):
        self.transaction_id = transaction_id

    def __str__(self):
        return 'Cancel(transaction_id = ' + self.transaction_id + ')\n'
    
    def getClassName(self):
        return "Cancel"

    def toSQL(self, conn):
        cur = conn.cursor()
        cur.execute("SELECT account_id FROM TRANSACTION WHERE TRANSACTION.transaction_id = " + self.transaction_id + ";")
        result = cur.fetchone()
        account_id = result[0]
        cur.execute("SELECT amount FROM TRANSACTION WHERE TRANSACTION.transaction_id = " + self.transaction_id + ";")
        result = cur.fetchone()
        history_shares = result[0]
        cur.execute("SELECT limitation FROM TRANSACTION WHERE TRANSACTION.transaction_id = " + self.transaction_id + ";")
        result = cur.fetchone()
        price = result[0]
        cur.execute("SELECT symbol FROM TRANSACTION WHERE TRANSACTION.transaction_id = " + self.transaction_id + ";")
        result = cur.fetchone()
        symbol = result[0]
        sql = "UPDATE TRANSACTION SET alive = " + "FALSE" + " WHERE TRANSACTION.transaction_id = " + str(self.transaction_id) + ";"        
        cur.execute(sql)
        sql = "DELETE FROM HISTORY WHERE HISTORY.transaction_id = " + self.transaction_id + " AND HISTORY.status = 'open' AND HISTORY.symbol = '" + symbol + "' AND HISTORY.price = " + str(price) + "AND HISTORY.history_shares = " + str(history_shares) +  ";"
        cur.execute(sql)
        sql = "INSERT INTO HISTORY(transaction_id, account_id, status, history_shares, price, symbol) VALUES(" + str(self.transaction_id) + " , " + str(account_id) + " , '" + "cancel" + "' , " + str(history_shares) + " , " + str(price) + " , '" + symbol + "');"
        cur.execute(sql)
        conn.commit()



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
    parser = etree.XMLParser(encoding="UTF-8")
    root = etree.fromstring(recv_string.encode("UTF-8"),parser)
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

