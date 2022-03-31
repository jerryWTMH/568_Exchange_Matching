import socket
import time

from xml_parser import parse_xml
from test_input import create_account_testcase
from test_input import create_order_testcase
if __name__ == '__main__':
    try:
        # create an INET, STREAMing socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # now connect to the web server on port 80 - the normal http port
        s.connect(("localhost", 12345))
        msg = create_account_testcase()
        msg = str(len(msg)) + '\r\n' + msg
        msg = str.encode(msg, 'utf-8')
        s.send(msg)
        time.sleep(10)
        # sleep for ten seconds to wait for closing
        msg = "This is the end!"
        msg = str(len(msg)) + '\r\n' + msg
        msg = str.encode(msg, 'utf-8')
        s.send(msg)

        s.close()
        print(msg)
        print("done")
    except Exception as e: print(e)
