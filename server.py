import psycopg2
from configparser import ConfigParser
from create_tables import create_tables
import socket

from xml_parser import parse_xml




def drop_table():
    drops = "DROP TABLE POSITION; DROP TABLE HISTORY; DROP TABLE TRANSACTION; DROP TABLE ACCOUNT; "
    return drops
    


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
        
        # sql = "INSERT INTO ACCOUNT(account_id, balance) VALUES(28, 1000000);"
        # cur.execute(sql)

        print("start socket")
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to a public host, and a well-known port
        serversocket.bind(("", 12345))
        # become a server socket
        serversocket.listen(2)
        # accept connections from outside
        while True:
            (clientsocket, address) = serversocket.accept()
            result = clientsocket.recv(1024).decode()
            if(result == ""):
                break

            executions = parse_xml(result)
            for execution in executions.executions:       
                print(execution.toSQL())
                cur.execute(execution.toSQL())
            

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

