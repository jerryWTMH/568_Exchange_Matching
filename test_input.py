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
    account_requests =[]
    account_requests.append(AccountRequest("123", "1000"))
    create_request = CreateRequest(account_requests)
    return etree.tostring(create_request.xml_element(), pretty_print=True).decode('UTF-8')


def create_order_testcase():
    transactions = []
    transactions.append(OrderRequest("100", "100", "SYM"))
    transaction_request = TransactionRequest("123", transactions)
    return etree.tostring(transaction_request.xml_element(), pretty_print=True).decode('UTF-8')
