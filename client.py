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
        # msg = test_input.create_account_error()
        send(s,msg)
        # s.recv()
        #__________________________________________________________________________________________________
        msg = test_input.one_order("1", "TESLA", "-500", "12")
        send(s, msg)
        msg = test_input.one_order("2", "TESLA", "300", "13")
        send(s, msg)
        msg = test_input.one_cancel(transaction_id="1",account_id="1")
        send(s, msg)

        msg = "This is the end!"
        send(s,msg)

        server_msg = s.recv(2048)
        print(server_msg.decode('UTF-8'))

        server_msg = s.recv(2048)
        print(server_msg.decode('UTF-8'))

        server_msg = s.recv(2048)
        print(server_msg.decode('UTF-8'))

        server_msg = s.recv(2048)
        print(server_msg.decode('UTF-8'))

    except Exception as e: print(e)
