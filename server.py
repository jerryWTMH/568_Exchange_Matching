import psycopg2
from configparser import ConfigParser
import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
addr = (HOST, PORT)

def init_database():
    commands = (
        """
        CREATE TABLE ACCOUNT(
            account_id SERIAL PRIMARY KEY,
            balance DOUBLE PRECISION NOT NULL 
        )
        """,
        """
        CREATE TABLE POSITION(
            position_id SERIAL PRIMARY KEY,
            account_id INTEGER NOT NULL,
            symbol VARCHAR(128) NOT NULL,
            shares INTEGER NOT NULL,
            FOREIGN KEY (account_id) REFERENCES ACCOUNT (account_id) ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
        """ 
        CREATE TABLE TRANSACTION(
            transaction_id SERIAL PRIMARY KEY,
            account_id INTEGER NOT NULL,              
            create_time TIME NOT NULL,
            alive BOOL NOT NULL,
            amount INTEGER NOT NULL,
            limitation INTEGER NOT NULL,
            symbol VARCHAR(128) NOT NULL,
            FOREIGN KEY (account_id) REFERENCES ACCOUNT (account_id) ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE HISTORY(
            history_id SERIAL PRIMARY KEY,
            account_id INTEGER NOT NULL,
            transaction_id INTEGER NOT NULL,               
            status VARCHAR(128) NOT NULL,
            history_time TIME NOT NULL,
            history_shares INTEGER NOT NULL,
            price INTEGER,
            FOREIGN KEY (account_id) REFERENCES ACCOUNT (account_id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (transaction_id)  REFERENCES TRANSACTION (transaction_id) ON UPDATE CASCADE ON DELETE CASCADE
        )
        """
    )
    return commands

###
# FOREIGN KEY (account_id) REFERENCES ACCOUNT (account_id) ON UPDATE CASCADE ON DELETE CASCADE,
# FOREIGN KEY (order_id)  REFERENCES ORDER (order_id) ON UPDATE CASCADE ON DELETE CASCADE

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

        # create table one by one
        for command in commands:
            cur.execute(command)
       
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
    commands = init_database()
    connect(commands)

