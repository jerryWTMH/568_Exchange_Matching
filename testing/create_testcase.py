import socket

import test_input


def send(s, msg):
    msg = str(len(msg)) + '\r\n' + msg
    msg = str.encode(msg, 'utf-8')
    s.send(msg)


class Buffer:
    def __init__(self, sock, client):
        self.sock = sock
        self.buffer = b''
        self.client = client

    def get_content(self):
        while b'\r\n' not in self.buffer:
            data = self.sock.recv(1)
            if not data:
                return None
            self.buffer += data
        line, _, self.buffer = self.buffer.partition(b'\n')
        byte_count = line.decode('utf-8')
        data = self.sock.recv(int(byte_count))
        return data.decode('utf-8')

def demonstrate_valid_create_account_testcase():
    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # now connect to the web server on port 80 - the normal http port
    s.connect(("localhost", 12345))
    msg = test_input.create_account_testcase()
    buffer = Buffer(s, None)
    print("This is the message sent\n", msg)
    send(s, msg)
    msg = "This is the end!"
    send(s, msg)
    server_msg = buffer.get_content()
    print("This is the response from server\n", server_msg)

def demonstrate_invalid_create_account_testcase():
    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # now connect to the web server on port 80 - the normal http port
    s.connect(("localhost", 12345))
    msg = test_input.create_account_error()
    buffer = Buffer(s, None)
    print("This is the message sent\n", msg)
    send(s, msg)
    msg = "This is the end!"
    send(s, msg)
    server_msg = buffer.get_content()
    print("This is the response from server\n", server_msg)


if __name__ == '__main__':
    try:
        demonstrate_valid_create_account_testcase()
        demonstrate_invalid_create_account_testcase()


    except Exception as e: print(e)
