from io import BytesIO

from lxml import etree


class ErrorResponse:
    def __init__(self, attributes, message):
        # attributes should be a hashmap [attribute] -> [attribute value]
        # Possible attributes: sym,amount,limit,id|
        self.attributes = attributes
        self.message = message

    def xml_element(self):
        root = etree.Element('error')
        for attribute in self.attributes:
            root.set(attribute, str(self.attributes[attribute]))
        root.text = self.message
        return root


class CreateResponse:
    def __init__(self, account_id, sym=None):
        # sym might be null for account creation
        self.account_id = account_id
        self.sym = sym

    def xml_element(self):
        root = etree.Element('Created')
        root.set("id", str(self.account_id))
        if self.sym is not None:
            root.set("sym", str(self.sym))
        return root


class QueryResponse:
    def __init__(self, transaction_id, sub_transactions):
        # sub elements may include executed canceled and open
        self.transaction_id = transaction_id
        self.sub_transactions = sub_transactions

    def xml_element(self):
        root = etree.Element("status")
        root.set("id", str(self.transaction_id))
        for sub_transaction in self.sub_transactions:
            root.append(sub_transaction.xml_element())
        return root


class CancelResponse:
    def __init__(self, transaction_id, sub_transactions):
        self.transaction_id = transaction_id
        self.sub_transactions = sub_transactions

    def xml_element(self):
        root = etree.Element("canceled")
        root.set("id", str(self.transaction_id))
        for sub_transaction in self.sub_transactions:
            root.append(sub_transaction)
        return root


class SubTransaction:
    # type = {open, cancel, executed}
    def __init__(self, transaction_type, shares, price=None, time=None):
        self.transaction_type = transaction_type
        self.shares = shares
        self.price = price
        self.time = time

    def xml_element(self):
        root = etree.Element(self.transaction_type)
        root.set("shares", str(self.shares))
        if self.price is not None:
            root.set("price", str(self.price))
        if self.time is not None:
            root.set("time", str(self.time))
        return root


class ResultWrapper:
    def __init__(self, sub_elements):
        self.sub_elements = sub_elements

    def xml_element(self):
        root = etree.Element('results')
        # for result in self.results:
        for sub_element in self.sub_elements:
            root.append(sub_element.xml_element())
        return root
#
# Server:
#     parseXML(string:xml).handle().generateXML()
# server logic
# sql generator /filter
# testcases

if __name__ == '__main__':
    response = CreateResponse("account")
    print(etree.tostring(response.xml_element()))
    errorResponse = ErrorResponse({"attr1": 1, "attr2": "attr2"}, "Error Message");
    print(etree.tostring(errorResponse.xml_element()))
    print('\n')
    print('\n')

    open_transaction = SubTransaction("open", 10, 10, 10)
    cancel_transaction = SubTransaction("cancel", 10, 10, 10)
    execute_transaction = SubTransaction("executed", 10, 10, 10)
    Dict = {open_transaction, cancel_transaction, execute_transaction}
    query = QueryResponse("Query_id", Dict);
    print(etree.tostring(query.xml_element()))
    print('\n')
    print('\n')

    sub_elements = {query, response, errorResponse}
    result = ResultWrapper(sub_elements)
    print(etree.tostring(result.xml_element(), pretty_print=True).decode('UTF-8'))
    # parseXML:return a series of executables that are independent with each other
    # handle:return a wrapper, which contains a serious of objects
    # generateXML(): it's the method of wrapper, generate


