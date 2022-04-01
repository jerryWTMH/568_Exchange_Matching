
def create_tables():
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
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
            history_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            history_shares INTEGER NOT NULL,
            price INTEGER,
            symbol VARCHAR(128) NOT NULL,
            FOREIGN KEY (account_id) REFERENCES ACCOUNT (account_id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (transaction_id)  REFERENCES TRANSACTION (transaction_id) ON UPDATE CASCADE ON DELETE CASCADE
        )
        """
    )
    return commands
