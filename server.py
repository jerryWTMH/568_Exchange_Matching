import threading
import psycopg2
from configparser import ConfigParser
from create_tables import create_tables
import socket
import datetime
import xml_generator as res
from xml_parser import parse_xml
import handlers as handlers
import xml_parser as parser

import multiprocessing as mp
from multiprocessing import Process, Pool
import os

# connect to the PostgreSQL server
conn = psycopg2.connect(host="",database="MARKET",user="postgres",password="passw0rd")
        # create a cursor
cur = conn.cursor()
def drop_table(conn, cur):
    drops = "DROP TABLE IF EXISTS POSITION CASCADE; DROP TABLE IF EXISTS HISTORY CASCADE; DROP TABLE IF EXISTS TRANSACTION CASCADE; DROP TABLE IF EXISTS ACCOUNT CASCADE; "
    cur.execute(drops)


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

    def send_msg(self, msg):
        msg = str(len(msg)) + '\r\n' + msg
        msg = str.encode(msg, 'utf-8')
        print(msg)
        print("is sent to client")
        self.client.send(msg)


def server_handler(executions, conn, cur):
    # The problem that should be handled:
    # 1. Invalid order (ex: account doesn't exist; amount is higher than the balance;)
    # 2. Some parameters of Order and Cancel should be gotten by SQL first
    # 3. Transaction id should exist in every command.
    # If there is an error in current execution, it would generate the XML for <error>, and put the error message inside of the XML.
    # If there is no error in current execution, it would call the toSQL() of the Class, and then generate the XML for the response message.
    # This would return XML that is corresponding to the input from the client.
    msgs = []
    for execution in executions.executions:
        sql = ""
        error = ""
        className = execution.getClassName()
        if className == "Order":
            order_msg = handlers.order_handler(execution,conn)
            msgs.append(order_msg)

        elif className == "Account":
            account_msg = handlers.account_handler(execution,conn)
            msgs.append(account_msg)
            
        elif className == "Position":
            position_msg = handlers.position_handler(execution,conn)
            msgs.append(position_msg)

        elif className == "Query":
            query_msg = handlers.query_handler(execution,conn)
            msgs.append(query_msg)

        elif className == "Cancel":
            query_msg = handlers.query_handler(execution,conn)
            msgs.append(query_msg)
        # try to add some XML information to return_executions
        conn.commit()

    return msgs
    # return return_executions


class ClientThread(threading.Thread, Buffer):
    def __init__(self, buffer, thread_ID):
        threading.Thread.__init__(self)
        self.buffer = buffer
        self.thread_ID = thread_ID

    def run(self):
        print(self.thread_ID + " is running!")
        print("current process PID is : ", os.getpid())
        while True:
            #continuously read requests from buffer
            result = self.buffer.get_content()
            if result is None:
                continue
            if result == "This is the end!":
                break
            executions = parse_xml(result)
            print(executions)
            results = server_handler(executions, conn, cur)

def connect(commands):
    """ Connect to the PostgreSQL database server """
    if True:
        # drop the table
        drop_table(conn, cur)
        # create table one by one
        for command in commands:
            cur.execute(command)
        print("start socket")
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to a public host, and a well-known port
        serversocket.bind(("localhost", 12345))
        # become a server socket
        serversocket.listen(2)
        # accept connections from outside
        thread_count = 0
        # while True:
        #     client_socket, address = serversocket.accept()
        #     buffer = Buffer(client_socket,serversocket)
        #     ct = ClientThread(buffer, str(thread_count))
        #     thread_count += 1
        #     p = Process(target=ct.run(),)
        #     p.start()
        #     p.join()
        
        with Pool(processes = 4) as pool:
            while True:
                client_socket, address = serversocket.accept()
                buffer = Buffer(client_socket,serversocket)
                ct = ClientThread(buffer, str(thread_count))
                thread_count += 1
                pool.apply_async(ct.run())

        serversocket.close()
        print("close socket")

	    # close the communication with the PostgreSQL
        cur.close()
        conn.close()
        print('Database connection closed.')

if __name__ == '__main__':
    commands = create_tables()
    connect(commands)

