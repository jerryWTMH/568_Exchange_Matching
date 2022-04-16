import socket

import test_input

def init_database():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 12345))
    msg = test_input.create_account_testcase()
    buffer = Buffer(s, None)
    send(s, msg)
    msg = "This is the end!"
    send(s, msg)
    server_msg = buffer.get_content()

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

if __name__ == '__main__':
    try:
        init_database()
        f = open("test_in.xml", "r")
        test_input = f.read()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 12345))
        buffer = Buffer(s, None)

        send(s, test_input)
        result = buffer.get_content()
        output_file = open("test_out_test","w")
        output_file.write(result)


    except:
        print("ERROR")


