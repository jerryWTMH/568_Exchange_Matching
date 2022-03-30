import psycopg2
from configparser import ConfigParser
from create_tables import create_tables
import socket

from xml_parser import parse_xml

def drop_table(conn, cur):
    drops = "DROP TABLE IF EXISTS POSITION CASCADE; DROP TABLE IF EXISTS HISTORY CASCADE; DROP TABLE IF EXISTS TRANSACTION CASCADE; DROP TABLE IF EXISTS ACCOUNT CASCADE; "
    #DROP TABLE ACCOUNT IF EXIST CASCADE
    cur.execute(drops)
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

        sql = "INSERT INTO ACCOUNT(account_id, balance) VALUES(12345, 11111);"
        cur.execute(sql)
        cur.execute("SELECT balance FROM ACCOUNT WHERE ACCOUNT.account_id = 12345")
        print("The number of parts: ", cur.rowcount)
        print("The content of parts: ", cur.fetchone())
        cur.close()
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