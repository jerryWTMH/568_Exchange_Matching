import threading

import psycopg2
from configparser import ConfigParser
from create_tables import create_tables
import socket

from xml_parser import parse_xml

# connect to the PostgreSQL server
conn = psycopg2.connect(host="",database="MARKET",user="postgres",password="passw0rd")
        # create a cursor
cur = conn.cursor()

def drop_table(conn, cur):
    drops = "DROP TABLE IF EXISTS POSITION CASCADE; DROP TABLE IF EXISTS HISTORY CASCADE; DROP TABLE IF EXISTS TRANSACTION CASCADE; DROP TABLE IF EXISTS ACCOUNT CASCADE; "
    cur.execute(drops)


class Buffer:
    def __init__(self, sock):
        self.sock = sock
        self.buffer = b''

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


def server_handler(executions, conn, cur):
    # The problem that should be handled:
    # 1. Invalid order (ex: account doesn't exist; amount is higher than the balance;)
    # 2. Some parameters of Order and Cancel should be gotten by SQL first
    # 3. Transaction id should exist in every command.
    # If there is an error in current execution, it would generate the XML for <error>, and put the error message inside of the XML.
    # If there is no error in current execution, it would call the toSQL() of the Class, and then generate the XML for the response message.
    # This would return XML that is corresponding to the input from the client. 
    return_executions = ""
    for execution in executions.executions:
        sql = ""
        error = ""
        className = execution.getClassName()
        if className == "Order":
            ### need to check whether valid or not
            sql = "SELECT * FROM ACCOUNT WHERE EXISTS(SELECT account_id FROM ACCOUNT WHERE ACCOUNT.account_id = " + execution.account_id + ");"
            cur.execute(sql)
            if(cur.rowcount == 0):               
                error = "The account_id doesn't exist!"
                print("error occurs in Order! ", error)
            else: 
                account_id = execution.account_id
                sql = "SELECT balance FROM ACCOUNT WHERE ACCOUNT.account_id = " + account_id + ";"
                cur.execute(sql)
                result = cur.fetchone()

                if result[0] < int(execution.limit * execution):
                    error = "The limitation of the order is higher than your balance!"
                    print("error occurs in Order! ", error)

                ### if there is not errorin current execution: call toSQL()
                if(error == ""):
                    execution.toSQL(conn)                    
                ##else:
                    ##prepare xml error tag here

        if(className == "Account"):
            execution.toSQL(conn)
            
        if(className == "Position"):
            ### need to check whether valid or not
            sql = "SELECT account_id FROM ACCOUNT WHERE account_id = " + execution.account_id + ";"
            cur.execute(sql)
            if(cur.rowcount == 0):
                error = "The account_id doesn't exist!"
                print("error occurs in Position! ", error)
            ### if there is not errorin current execution: call toSQL()
            if(error == ""):
                execution.toSQL(conn)

        if(className == "Query"):
            ### need to check whether valid or not
            sql = "SELECT transaction_id FROM TRANSACTION WHERE transaction_id = " + execution.transaction_id + ";"
            cur.execute(sql)
            if(cur.rowcount == 0):
                error = "The transaction_id doesn't exist!"
                print("error occurs in Query! ", error)
            ### if there is not errorin current execution: call toSQL()
            if(error == ""):
                execution.toSQL(conn)

        if(className == "Cancel"):
            ### need to check whether valid or not
            sql = "SELECT transaction_id FROM TRANSACTION WHERE transaction_id = " + execution.transaction_id + ";"
            cur.execute(sql)
            if(cur.rowcount == 0):
                error = "The transaction_id doesn't exist!"
                print("error occurs in Cancel! ", error)
            ### if there is not errorin current execution: call toSQL()
            if(error == ""):
                execution.toSQL(conn)                    
            ##else:
                ##prepare xml error tag here
        # try to add some XML information to return_executions        
    
    # return return_executions


class ClientThread(threading.Thread, Buffer):
    def __init__(self, buffer, thread_ID):
        threading.Thread.__init__(self)
        self.buffer = buffer
        self.thread_ID = thread_ID

    def run(self):
        print(self.thread_ID + "is running!")
        while True:
            #continuously read requests from buffer
            result = self.buffer.get_content()
            if result is None:
                continue
            if result == "This is the end!":
                break
            executions = parse_xml(result)
            print(executions)
            server_handler(executions, conn, cur)

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
        while True:
            client_socket, address = serversocket.accept()
            buffer = Buffer(client_socket)
            ct = ClientThread(buffer, str(thread_count))
            thread_count += 1
            ct.run()
        serversocket.close()
        print("close socket")

	    # close the communication with the PostgreSQL
        cur.close()
        # commit the changes
        conn.commit()
    # except (Exception, psycopg2.DatabaseError) as error:
    #     print(error)
    #
    # finally:
    #     if conn is not None:
    #         conn.close()
    #         print('Database connection closed.')

if __name__ == '__main__':
    commands = create_tables()
    connect(commands)

