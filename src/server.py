import threading
import time

import psycopg2
from configparser import ConfigParser
from create_tables import create_tables
import socket
import datetime
import xml_generator as res
from xml_parser import parse_xml
import handlers as handlers
import xml_parser as parser
import random

import multiprocessing as mp
from multiprocessing import Process, Pool,Lock
import os
from lxml import etree




request_count = 0
start_time = datetime.datetime.now()

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
        self.sock.send(msg)


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
            query_msg = handlers.cancel_handler(execution,conn)
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
        global request_count
        global start_time
        # print(self.thread_ID + " is running!")
        # print("current process PID is : ", os.getpid())
        response_bytes_array = []
        while True:
            #continuously read requests from buffer
            result = self.buffer.get_content()
            if result is None:
                continue
            if result == "This is the end!":
                for sub_response in response_bytes_array:
                    self.buffer.send_msg(sub_response)
                    response_bytes_array = []
                break
            else:
                executions = parse_xml(result)
                server_response = server_handler(executions, conn, cur)
                response_xml = res.ResultWrapper(server_response)
                response_bytes = etree.tostring(response_xml.xml_element(), pretty_print=True).decode('UTF-8')
                response_bytes_array.append(response_bytes)
                #This is for performance test
                request_count = request_count+1
                time_difference_seconds = (datetime.datetime.now() - start_time).seconds
                if time_difference_seconds >= 1:
                    start_time = datetime.datetime.now()
                    print(request_count)


def connect(commands, conn):
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
        serversocket.listen(10)
        
        # accept connections from outside
        thread_count = 0
        with Pool(processes = 4) as pool:
            print("################")
            while True:                
                client_socket, address = serversocket.accept()
                buffer = Buffer(client_socket,serversocket)
                ct = ClientThread(buffer, str(thread_count))
                thread_count += 1
                pool.apply_async(ct.run())
        serversocket.close()
        print("close socket")

        cur.close()
        conn.close()
        print('Database connection closed.')

if __name__ == '__main__':
    conn = psycopg2.connect(host="db",port=5432, user="postgres",password="passw0rd")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DROP DATABASE MARKET;")
    cur.execute("CREATE DATABASE " + "MARKET" + ";")
    conn = psycopg2.connect(host="db", port=5432, database="market",user="postgres",password="passw0rd")
    commands = create_tables()
    connect(commands, conn)



