import psycopg2
from configparser import ConfigParser
from create_tables import create_tables
import socket

from xml_parser import parse_xml




def drop_table(conn, cur):
    # sql = "SELECT COUNT(*) FROM ACCOUNT"
    # if cur.execute(sql) != 0:
    #     cur.execute("DROP TABLE ACCOUNT")
    #     conn.commit()  
    # sql = "SELECT COUNT(*) FROM POSITION"
    # if cur.execute(sql) != 0:
    #     cur.execute("DROP TABLE POSITION")
    #     conn.commit()  
    # sql = "SELECT COUNT(*) FROM TRANSACTION"
    # if cur.execute(sql) != 0:
    #     cur.execute("DROP TABLE TRANSACTION")
    #     conn.commit()  
    # sql = "SELECT COUNT(*) FROM HISTORY"
    # if cur.execute(sql) != 0:
    #     cur.execute("DROP TABLE HISTORY")
    #     conn.commit()  
    drops = "DROP TABLE POSITION; DROP TABLE HISTORY; DROP TABLE TRANSACTION; DROP TABLE ACCOUNT; "
    cur.execute(drops)
    conn.commit()
    
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
        if(className == "Order"):
            ### need to check whether valid or not
            sql = "SELECT * FROM ACCOUNT WHERE EXISTS(SELECT account_id FROM ACCOUNT WHERE ACCOUNT.account_id = " + execution.account_id + ");"
            bool_result = cur.execute(sql)
            if(not bool_result):
                error = "The account_id doesn't exist!"
            account_id = execution.account_id
            print(error)
            sql = "SELECT balance FROM ACCOUNT WHERE ACCOUNT.account_id = " + account_id + ";"
            curr_balance = cur.execute(sql)
            # print("curr_balance: " + curr_balance)
            # print("execution.limit: " + execution.limit)
            if(curr_balance < execution.limit):
                error = "The limitation of the order is higher than your balance!"

            ### if there is not errorin current execution: call toSQL()
            if(error == ""):
                execution.toSQL(conn)                    
            ##else:
                ##prepare xml error tag here

        if(className == "Account"):
            execution.toSQL(conn)

        if(className == "Position"):
            ### need to check whether valid or not
            sql = "SELECT * FROM ACCOUNT WHERE EXISTS(SELECT account_id FROM ACCOUNT WHERE account_id = " + execution.account_id + ");"
            bool_result = cur.execute(sql)
            ### if there is not errorin current execution: call toSQL()
            if(error == ""):
                execution.toSQL(conn)

        if(className == "Query"):
            ### need to check whether valid or not
            sql = "SELECT * FROM ACCOUNT WHERE EXISTS(SELECT account_id FROM ACCOUNT WHERE account_id = " + execution.account_id + ");"
            bool_result = cur.execute(sql)
            if(not bool_result):
                error = "The account_id doesn't exist!"
            ### if there is not errorin current execution: call toSQL()
            if(error == ""):
                execution.toSQL(conn)

        if(className == "Cancel"):
            ### need to check whether valid or not
            sql = "SELECT * FROM ACCOUNT WHERE EXISTS(SELECT account_id FROM ACCOUNT WHERE account_id = " + execution.account_id + ");"
            bool_result = cur.execute(sql)
            if(not bool_result):
                error = "The account_id doesn't exist!"
            ### if there is not errorin current execution: call toSQL()
            if(error == ""):
                execution.toSQL(conn)                    
            ##else:
                ##prepare xml error tag here
        # try to add some XML information to return_executions        
            
    # return return_executions


def connect(commands):
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
        drop_table(conn, cur)
    
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
        while True:
            (clientsocket, address) = serversocket.accept()
            result = clientsocket.recv(1024).decode()
            if(result == ""):
                break
            executions = parse_xml(result)
            # Handler   
            # executions_new = server_handler(executions, conn, cur)
            server_handler(executions, conn, cur)

            for execution in executions.executions:   
                print(execution)     
                # print(execution.toSQL())
                # cur.execute(execution.toSQL())
            
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
    commands = create_tables()
    connect(commands)

