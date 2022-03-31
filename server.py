import threading
import psycopg2
from configparser import ConfigParser
from create_tables import create_tables
import socket
import datetime
import xml_generator as res
from xml_parser import parse_xml

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
            sql = "SELECT * FROM ACCOUNT WHERE EXISTS(SELECT account_id FROM ACCOUNT WHERE ACCOUNT.account_id = " + execution.account_id + ");"
            cur.execute(sql)
            if cur.rowcount == 0:
                error = "The account_id doesn't exist!"
                print("error occurs in Order! ", error)
                msgs.append(res.ErrorResponse({"sym":execution.symbol,"amount":execution.amount,"limit":execution.limit},error))
                break
            else: 
                account_id = execution.account_id
                if(int(execution.amount) > 0):
                    ### Buying
                    sql = "SELECT balance FROM ACCOUNT WHERE ACCOUNT.account_id = " + account_id + ";"
                    cur.execute(sql)
                    result = cur.fetchone()
                    if(result[0] < int(execution.limit) * int(execution.amount)):
                        error = "The limitation of the order is higher than your balance!"
                        print("error occurs in Order! ", error)
                    sql = "UPDATE ACCOUNT SET balance = " + str(result[0] - (int(execution.limit) * int(execution.amount))) + " WHERE ACCOUNT.account_id = '" + execution.account_id + "' ;"
                    cur.execute(sql)
                    
                    ### add to TRANSACTION and HISTORY first
                    sql = "INSERT INTO TRANSACTION(account_id, create_time, alive, amount, limitation, symbol) VALUES(" +  execution.account_id + ", " + "now()" + ", " + "TRUE" + ", " + execution.amount + ", " + execution.limit + ", '" + execution.symbol + "');"
                    cur.execute(sql)
                    conn.commit()
                    sql = "SELECT currval(pg_get_serial_sequence('TRANSACTION','transaction_id'));"
                    cur.execute(sql)
                    result = cur.fetchone() ###### PROBLEM
                    new_transaction_id = result[0] ###### PROBLEM
                    sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + account_id + ", " + new_transaction_id + ", " + "open" + ", " + "now()" + ", " + execution.amount + ", " + execution.limit + ", '" + execution.symbol + "');"
                    cur.execute(sql)
                    conn.commit()

                    ### 
                    sql = "SELECT * FROM TRANSACTION WHERE TRANSACTION.symbol = '" + execution.symbol + "' TRANSACTION.limitation <= '" + execution.limit + "' + ORDER BY TRANSACTION.create_time ASC;"
                    cur.execute(sql)
                    sell_orders = cur.fetchall()
                    for sell_order in sell_orders:
                        if(execution.amount > sell_order['amount']):
                            old_transaction_id = sell_order['transaction_id']
                            old_account_id = sell_order['account_id']
                            old_amount = sell_order['amount']
                            old_price = sell_order['price']
                            symbol = sell_order['symbol']
                            ###(Old order) alive -> False
                            sql = "UPDATE TRANSACTION SET alive = FALSE WHERE TRANSACTION.transaction_id = '" + old_transaction_id + "';"
                            cur.execute(sql)
                            ###(Old order) delete transaction, and add executed in HISTORY
                            #sql = "DELETE FROM HISTORY WHERE HISTORY.transaction_id = " + old_transaction_id + ";"
                            cur.execute(sql)
                            sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + old_account_id + ", " + old_transaction_id + ", " + "executed" + ", " + datetime.datetime.now() + ", " + old_amount + ", " + old_price + ", " + symbol +");"  
                            cur.execute(sql)
                            ###(New order) alive -> True
                            #sql = "INSERT INTO TRANSACTION(account_id, create_time, alive, amount, limitation, symbol) VALUES(" +  execution.account_id + ", " + datetime.datetime.now() + ", " + "TRUE" + ", " + (execution.amount - amount) + ", " + execution.limit + ", " + execution.symbol + ");"
                            cur.execute(sql)
                            ###(New order) add to HISTORY
                            sql = "UPDATE HISTORY SET history_shares = " + (execution.amount - old_amount) + " WHERE HISTORY.account_id = " + execution.account_id + " AND HISTORY.status = open ;"  
                            cur.execute(sql)
                            sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + execution.account_id + ", " + new_transaction_id + ", " + "executed" + ", " + datetime.datetime.now() + ", " + old_amount + ", " + old_price + ", " + symbol +");"  
                            cur.execute(sql)
                            execution.amount -= old_amount
                else:
                    ### Selling
                    shares = execution.amount
                    sql = "SELECT shares FROM POSITION WHERE POSITION.account_id = " + account_id + " POSITION.symbol = '" + execution.symbol + "' ;"
                    cur.execute(sql)
                    result = cur.fetchone()
                    if(result[0] < int(execution.amount)):
                        error = "The amount of selling is higher than you own!"
                        print("error occurs in Order! ", error)

                ### if there is not errorin current execution: call toSQL()
                if(error == ""):
                    execution.toSQL(conn)                    
                ##else:
                    ##prepare xml error tag here

        elif className == "Account":
            sql = "SELECT account_id FROM ACCOUNT WHERE account_id = " + execution.account_id + ";"
            cur.execute(sql)
            if (cur.rowcount != 0):
                error = "The account_id Already Existed"
                print("error occurs in Account Init! ", error)
                msgs.append(res.ErrorResponse({"id":execution.account_id}, error))
                break
            msgs.append(execution.toSQL(conn))
            
        elif className == "Position":
            ### need to check whether valid or not
            sql = "SELECT account_id FROM ACCOUNT WHERE account_id = " + execution.account_id + ";"
            cur.execute(sql)
            if(cur.rowcount == 0):
                error = "The account_id doesn't exist!"
                print("error occurs in Position! ", error)
            ### if there is not errorin current execution: call toSQL()
            if(error == ""):
                execution.toSQL(conn)

        elif className == "Query":
            ### need to check whether valid or not
            sql = "SELECT transaction_id FROM TRANSACTION WHERE transaction_id = " + execution.transaction_id + ";"
            cur.execute(sql)
            if(cur.rowcount == 0):
                error = "The transaction_id doesn't exist!"
                print("error occurs in Query! ", error)
            ### if there is not errorin current execution: call toSQL()
            if(error == ""):
                execution.toSQL(conn)

        elif className == "Cancel":
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
        conn.commit()

    return msgs
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
        conn.close()
        print('Database connection closed.')

if __name__ == '__main__':
    commands = create_tables()
    connect(commands)

