from lxml import etree


class CreateRequest:
    def __init__(self, accounts, positions=None):
        self.accounts = accounts
        self.positions = positions

    def xml_element(self):
        root = etree.Element('create')
        for account in self.accounts:
            root.append(account.xml_element())
        if self.positions is not None:
            for position in self.positions:
                root.append(position.xml_element())
        return root


class AccountRequest:
    def __init__(self, account_id, balance):
        self.account_id = account_id
        self.balance = balance

    def xml_element(self):
        root = etree.Element('account')
        root.set('id', self.account_id)
        root.set('balance', self.balance)
        return root


class PositionRequest:
    def __init__(self, sym, savings):
        self.sym = sym
        self.savings = savings

    def xml_element(self):
        root = etree.Element('symbol')
        root.set('sym', self.sym)
        for saving in self.savings:
            root.append(saving.xml_element())
        return root


class Saving:
    def __init__(self, account_id, share):
        self.account_id = account_id
        self.share = share

    def xml_element(self):
        root = etree.Element('account')
        root.set('id', self.account_id)
        root.text = self.share
        return root

class TransactionRequest:
    def __init__(self, account_id, transactions):
        self.account_id = account_id
        self.transactions = transactions

    def xml_element(self):
        root = etree.Element('transactions')
        root.set('id', self.account_id)
        for transaction in self.transactions:
            root.append(transaction.xml_element())
        return root

class OrderRequest:
    def __init__(self, amount, limit, symbol):
        self.amount = amount
        self.limit = limit
        self.symbol = symbol

    def xml_element(self):
        root = etree.Element('order')
        root.set('sym',self.symbol)
        root.set('amount',self.amount)
        root.set('limit',self.limit);
        return root

class QueryRequest:
    def __init__(self,transaction_id):
        self.transaction_id = transaction_id

    def xml_element(self):
        root = etree.Element('query')
        root.set('id',self.transaction_id)
        return root

class CancelRequest:
    def __init__(self,transaction_id):
        self.transaction_id = transaction_id

    def xml_element(self):
        root = etree.Element('cancel')
        root.set('cancel',self.transaction_id)
        return root


def create_account_testcase():
    # msg = "INSERT INTO ACCOUNT(account_id, balance) VALUES(888, 10000);"
    account_requests =[]
    #acccount 1 has 10000 balance and 1000 shares of tesla and 2000 shares of apple
    account_requests.append(AccountRequest("1", "10000"))
    saving_1_1 = [Saving("1", "1000")]
    saving_1_2 = [Saving("1", "2000")]
    account_requests.append(PositionRequest("TESLA", saving_1_1))
    account_requests.append(PositionRequest("APPLE", saving_1_2))
    #account 2 has 5000 balance and 5000 shares of META and 5000 shares of AMAZON
    account_requests.append(AccountRequest("2", "5000"))
    saving_2_1 = [Saving("2", "5000")]
    saving_2_2 = [Saving("2", "5000")]
    account_requests.append(PositionRequest("META", saving_2_1))
    account_requests.append(PositionRequest("AMAZ", saving_2_2))
    create_request = CreateRequest(account_requests)
    return etree.tostring(create_request.xml_element(), pretty_print=True).decode('UTF-8')

def order_account_non_exist_testcase():
    transactions = []
    transactions.append(OrderRequest("100", "100", "SYM"))
    transaction_request = TransactionRequest("10", transactions)
    return etree.tostring(transaction_request.xml_element(), pretty_print=True).decode('UTF-8')

def simple_buy_order():
    transactions = []
    transactions.append(OrderRequest("100", "100", "SYM"))
    transaction_request = TransactionRequest("1", transactions)
    return etree.tostring(transaction_request.xml_element(), pretty_print=True).decode('UTF-8')

def buy_order_exceed_limit():
    transactions = []
    transactions.append(OrderRequest("100", "1000", "SYM"))
    transaction_request = TransactionRequest("1", transactions)
    return etree.tostring(transaction_request.xml_element(), pretty_print=True).decode('UTF-8')
#
# def create_order_testcase():
#     transactions = []
#     transactions.append(OrderRequest("100", "100", "SYM"))
#     transaction_request = TransactionRequest("1", transactions)
#     return etree.tostring(transaction_request.xml_element(), pretty_print=True).decode('UTF-8')
