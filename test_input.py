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


def create_account_testcase():
    account_requests =[]
    account_requests.append(AccountRequest("123", "1000"))
    create_request = CreateRequest(account_requests)
    return(etree.tostring(create_request.xml_element(), pretty_print=True).decode('UTF-8'))