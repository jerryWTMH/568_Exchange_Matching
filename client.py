import socket
from xml_parser import parse_xml
from test_input import create_account_testcase
from test_input import create_order_testcase
if __name__ == '__main__':
    try:
        # create an INET, STREAMing socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # now connect to the web server on port 80 - the normal http port
        s.connect(("localhost", 12345))
        # msg = "INSERT INTO ACCOUNT(account_id, balance) VALUES(888, 10000);"
        msg = create_account_testcase()
        # msg = "INSERT INTO POSITION(account_id, symbol, shares) VALUES(123456, 'symbol', 100000)"
        msg = str(len(msg)) + '\r\n' + msg
        # "Hello world"
        # "len(Hello world) + \r\n + "Hello world" "
        msg = str.encode(msg, 'utf-8')
        s.send(msg)

        msg = create_order_testcase()
        msg = str(len(msg)) + '\r\n' + msg
        msg = str.encode(msg, 'utf-8')
        s.send(msg)

        s.close()
        print(msg)
        print("done")
    except:
        print("Error from client's socket")
