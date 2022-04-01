from multiprocessing import Lock, Pool, Pipe
import time
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


def create_accounts():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 12345))
    msg = test_input.create_account_testcase()
    send(s,msg)
    msg = "This is the end!"
    send(s, msg)
    s.recv(1024)


def add_one_order():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 12345))
    msg = test_input.one_order("1", "TESLA", "-500", "12")
    send(s, msg)
    msg = "This is the end!"
    send(s, msg)
    s.recv(1024)


def query_once():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 12345))
    msg = test_input.one_query("1")
    send(s, msg)
    msg = "This is the end!"
    send(s, msg)
    s.recv(1024)

def multi_orders():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 12345))
    buffer = Buffer(s,None)
    msg = test_input.one_order("1", "TESLA", "-50", "12")
    send(s, msg)
    msg = test_input.one_order("1", "TESLA", "50", "12")
    send(s,msg)
    msg = test_input.one_order("1", "APPLE", "50", "12")
    send(s, msg)
    msg = test_input.one_order("1", "APPLE", "-50", "12")
    send(s, msg)
    msg = "This is the end!"
    send(s, msg)
    server_msg = buffer.get_content()
    print(server_msg)
    server_msg = buffer.get_content()
    print(server_msg)
    server_msg = buffer.get_content()
    print(server_msg)
    server_msg = buffer.get_content()
    print(server_msg)

if __name__ == '__main__':
    pool = Pool(processes=4)
    count = 0
    pool.apply_async(create_accounts())
    # pool.apply_async(add_one_order())
    while count < 10000:
        pool.apply_async(multi_orders())
        count = count + 1