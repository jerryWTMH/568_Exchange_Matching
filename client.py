import socket
import time

from xml_parser import parse_xml
import test_input

def send(s, msg):
    msg = str(len(msg)) + '\r\n' + msg
    msg = str.encode(msg, 'utf-8')
    print(msg)
    print("is sent")
    s.send(msg)


if __name__ == '__main__':
    try:
        # create an INET, STREAMing socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # now connect to the web server on port 80 - the normal http port
        s.connect(("localhost", 12345))
        msg = test_input.create_account_testcase()

        send(s,msg)
        s.recv()
        #__________________________________________________________________________________________________
        msg = test_input.buy_order_exceed_limit()
        send(s,msg)


        msg = "This is the end!"
        msg = str(len(msg)) + '\r\n' + msg
        msg = str.encode(msg, 'utf-8')
        print(msg)
        s.send(s,msg)

        s.close()
        print("done")
    except Exception as e: print(e)
