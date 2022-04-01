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

def init_database():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 12345))
    msg = test_input.create_account_testcase()
    buffer = Buffer(s, None)
    send(s, msg)
    msg = "This is the end!"
    send(s, msg)
    server_msg = buffer.get_content()


def demonstrate_valid_orders():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 12345))
    buffer = Buffer(s, None)
    msg = test_input.one_order("1", "TESLA", "-500", "2")
    send(s,msg)
    print("This is the order sent",msg)
    msg = test_input.one_order("1", "TESLA", "-500", "4")
    send(s, msg)
    print("This is the order sent", msg)
    msg = test_input.one_order("2", "TESLA", "200", "4")
    send(s, msg)
    print("This is the order sent", msg)
    msg = test_input.one_order("2", "TESLA", "400", "4")
    send(s, msg)
    print("This is the order sent", msg)
    msg = test_input.one_order("2", "TESLA", "400", "3")
    send(s, msg)
    print("This is the order sent", msg)
    msg = test_input.one_query("1")
    send(s, msg)
    print("This is the order sent", msg)
    msg = "This is the end!"
    send(s, msg)
    server_msg = buffer.get_content()
    print("This is the message got\n", server_msg)
    server_msg = buffer.get_content()
    print("This is the message got\n", server_msg)
    server_msg = buffer.get_content()
    print("This is the message got\n", server_msg)
    server_msg = buffer.get_content()
    print("This is the message got\n", server_msg)
    server_msg = buffer.get_content()
    print("This is the message got\n", server_msg)
    server_msg = buffer.get_content()
    print("This is the message got\n", server_msg)


def demonstrate_invalid_orders():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 12345))
    buffer = Buffer(s, None)
    msg = test_input.one_order("1", "TESLA", "-50000", "12")
    send(s, msg)
    print("This is the order sent", msg)
    msg = test_input.one_order("3", "TESLA", "-500", "14")
    send(s, msg)
    print("This is the order sent", msg)
    msg = test_input.one_order("1", "NONEEXIST", "-200", "14")
    send(s, msg)
    print("This is the order sent", msg)
    msg = test_input.one_order("2", "TESLA", "40000", "14")
    send(s, msg)
    print("This is the order sent", msg)

    msg = "This is the end!"
    send(s, msg)
    server_msg = buffer.get_content()
    print("This is the message got\n", server_msg)
    server_msg = buffer.get_content()
    print("This is the message got\n", server_msg)
    server_msg = buffer.get_content()
    print("This is the message got\n", server_msg)
    server_msg = buffer.get_content()
    print("This is the message got\n", server_msg)


if __name__ == '__main__':
    try:
        init_database()
        print("-----------------------------------------------")
        print("Valid cases demonstration")
        demonstrate_valid_orders()
        print("-----------------------------------------------")
        print("inValid cases demonstration")
        demonstrate_invalid_orders()

    except Exception as e: print(e)
