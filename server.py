import psycopg2
from configparser import ConfigParser
from create_tables import create_tables
import socket

from xml_parser import parse_xml


def drop_table():
    drops = "DROP TABLE IF EXISTS POSITION; DROP TABLE IF EXISTS HISTORY; DROP TABLE IF EXISTS TRANSACTION; DROP TABLE IF EXISTS ACCOUNT; "
    return drops


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


def server_handler(executions, cur):
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
        if(className == "Order"):
            ### need to check whether valid or not
            try:
                sql = "SELECT account_id FROM ACCOUNT WHERE account_id = " + execution.account_id + ";"
                cur.execute(sql)
                sql = "SELECT balance FROM ACCOUNT WHERE account_id = " + execution.account_id + ";"
                curr_balance = cur.execute(sql)
                if(curr_balance < execution.limit):
                    error = "The limitation of the order is higher than your balance!"

                ### if there is not errorin current execution: call toSQL()
                sql = sql + execution.toSQL()
                
            except (Exception, psycopg2.DatabaseError) as err:
                error = err     
                print(error)
        if(className == "Account"):
            ### need to check whether valid or not
            ### if there is not errorin current execution: call toSQL()
            sql = sql + execution.toSQL()
        if(className == "Position"):
            ### need to check whether valid or not
            ### if there is not errorin current execution: call toSQL()
            sql = sql + execution.toSQL()
        if(className == "Query"):
            ### need to check whether valid or not
            ### if there is not errorin current execution: call toSQL()
            sql = sql + execution.toSQL()
        if(className == "Cancel"):
            ### need to check whether valid or not
            ### if there is not errorin current execution: call toSQL()
            sql = sql + execution.toSQL()
        cur.execute(sql)
        # try to add some XML information to return_executions         
            
    return return_executions


def connect(drops, commands):
    """ Connect to the PostgreSQL database server """

    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(
        host="",
        database="MARKET",
        user="postgres",
        password="passw0rd")
		
        # create a cursor
        cur = conn.cursor()

        # drop the table
        cur.execute(drops)
    
        # create table one by one
        for command in commands:
            cur.execute(command)

        print("start socket")
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to a public host, and a well-known port
        serversocket.bind(("", 12345))
        # become a server socket
        serversocket.listen(2)
        # accept connections from outside
        client_socket, address = serversocket.accept()
        buffer = Buffer(client_socket)

        while True:
            result = buffer.get_content()
            if(result == ""):
                break

            executions = parse_xml(result)
            # Handler   
            executions_new = server_handler(executions, cur)

            # for execution in executions.executions:        
            #     print(execution.toSQL())
            #     cur.execute(execution.toSQL())
            
        serversocket.close()
        print("close socket")

	    # close the communication with the PostgreSQL
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

if __name__ == '__main__':
    drops = drop_table()
    commands = create_tables()

    connect(drops, commands)

