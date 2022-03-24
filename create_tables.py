import psycopg2
from config import config


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE ACCOUNTS(
            account_id SERIAL PRIMARY KEY,
            balance DOUBLE PRECISION NOT NULL 
        )
        """,
        """ 
        CREATE TABLE ORDERS(
            order_id SERIAL PRIMARY KEY,
            account_id INTEGER NOT NULL
            FOREIGN KEY(account_id)
                REFERENCES ACCOUNTS(account_id)
                ON UPDATE CASCADE ON DELETE CASCADE,
            sym VARCHAR(128) NOT NULL,
            amount INTEGER NOT NULL,
            limit INTEGER NOT NULL
        )
        """,
    )
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()