from multiprocessing import Lock, Pool, Pipe
import time
import socket
import test_input


def send(s, msg):
    msg = str(len(msg)) + '\r\n' + msg
    msg = str.encode(msg, 'utf-8')
    s.send(msg)


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


if __name__ == '__main__':
    pool = Pool(processes=4)
    count = 0
    pool.apply_async(create_accounts())
    pool.apply_async(add_one_order())
    while count < 10000:
        pool.apply_async(query_once())
        count = count + 1