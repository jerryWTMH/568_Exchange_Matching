import psycopg2

import xml_parser as parser
import xml_generator as res

def order_handler(execution:parser.Order,conn):
    cur = conn.cursor()
    sql = "SELECT * FROM ACCOUNT WHERE EXISTS(SELECT account_id FROM ACCOUNT WHERE ACCOUNT.account_id = " + execution.account_id + ");"
    cur.execute(sql)
    if cur.rowcount == 0:
        error = "The account_id doesn't exist!"
        print("error occurs in Order! ", error)
        return res.ErrorResponse({"sym": execution.symbol, "amount": execution.amount, "limit": execution.limit}, error)
    else:
        account_id = execution.account_id
        if (int(execution.amount) > 0):
            ### Buying
            sql = "SELECT balance FROM ACCOUNT WHERE ACCOUNT.account_id = " + account_id + ";"
            cur.execute(sql)
            result = cur.fetchone()
            if (result[0] < int(execution.limit) * int(execution.amount)):
                error = "The limitation of the order is higher than your balance!"
                print("error occurs in Order! ", error)
            sql = "UPDATE ACCOUNT SET balance = " + str(result[0] - (int(execution.limit) * int(
                execution.amount))) + " WHERE ACCOUNT.account_id = '" + execution.account_id + "' ;"
            cur.execute(sql)

            sql = "INSERT INTO TRANSACTION(account_id, create_time, alive, amount, limitation, symbol) VALUES(" + execution.account_id + ", " + "now()" + ", " + "TRUE" + ", " + execution.amount + ", " + execution.limit + ", '" + execution.symbol + "');"
            cur.execute(sql)
            conn.commit()
            sql = "SELECT currval(pg_get_serial_sequence('TRANSACTION','transaction_id'));"
            cur.execute(sql)
            result = cur.fetchone()  ###### PROBLEM
            new_transaction_id = result[0]  ###### PROBLEM
            sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + account_id + ", " + new_transaction_id + ", " + "open" + ", " + "now()" + ", " + execution.amount + ", " + execution.limit + ", '" + execution.symbol + "');"

            cur.execute(sql)
            conn.commit()

            ###
            sql = "SELECT * FROM TRANSACTION WHERE TRANSACTION.symbol = '" + execution.symbol + "' TRANSACTION.limitation <= '" + execution.limit + "' + ORDER BY TRANSACTION.create_time ASC;"
            cur.execute(sql)
            sell_orders = cur.fetchall()
            for sell_order in sell_orders:
                old_transaction_id = sell_order['transaction_id']
                old_account_id = sell_order['account_id']
                old_amount = sell_order['amount']
                old_price = sell_order['price']
                symbol = sell_order['symbol']
                if execution.amount != 0:
                    if (execution.amount > -1 * old_amount):
                        ###(Old order) alive -> False
                        sql = "UPDATE TRANSACTION SET alive = FALSE WHERE TRANSACTION.transaction_id = '" + old_transaction_id + "';"
                        cur.execute(sql)
                        ###(Old order) delete open, and add executed in HISTORY
                        sql = "DELETE FROM HISTORY WHERE HISTORY.transaction_id = " + old_transaction_id + " AND HISTORY.status = open;"
                        cur.execute(sql)
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + old_account_id + ", " + old_transaction_id + ", " + "executed" + ", " + "now()" + ", " + old_amount + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        ###(New order) alive -> True
                        sql = "UPDATE TRANSACTION SET alive = TRUE WHERE TRANSACTION.transaction_id = " + new_transaction_id + ";"
                        cur.execute(sql)
                        ###(New order) add to HISTORY
                        sql = "UPDATE HISTORY SET history_shares = " + (
                                    execution.amount - old_amount) + " WHERE HISTORY.account_id = " + int(
                            execution.account_id) + " AND HISTORY.status = open ;"
                        cur.execute(sql)
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + int(
                            execution.account_id) + ", " + new_transaction_id + ", " + "executed" + ", " + "now()" + ", " + old_amount + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        execution.amount -= old_amount
                    elif (execution.amount == -1 * old_amount):
                        ###(Old order) alive -> False
                        sql = "UPDATE TRANSACTION SET alive = FALSE WHERE TRANSACTION.transaction_id = '" + old_transaction_id + "';"
                        cur.execute(sql)
                        ###(Old order) delete open, and add executed in HISTORY
                        sql = "DELETE FROM HISTORY WHERE HISTORY.transaction_id = " + old_transaction_id + " AND HISTORY.status = open;"
                        cur.execute(sql)
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + old_account_id + ", " + old_transaction_id + ", " + "executed" + ", " + "now()" + ", " + old_amount + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        ###(New order) alive -> False
                        sql = "UPDATE TRANSACTION SET alive = FALSE WHERE TRANSACTION.transaction_id = " + new_transaction_id + ";"
                        cur.execute(sql)
                        ###(New order) add to HISTORY
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + int(
                            execution.account_id) + ", " + new_transaction_id + ", " + "executed" + ", " + "now()" + ", " + old_amount + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        execution.amount -= old_amount
                    elif (execution.amount < -1 * old_amount):
                        ###(Old order) update open, and add executed in HISTORY
                        sql = "UPDATE HISTORY SET history_shares = " + old_amount - int(
                            execution.amount) + " WHERE HISTORY.transaction_id = " + old_transaction_id + " AND HISTORY.status = open;"
                        cur.execute(sql)
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + old_account_id + ", " + old_transaction_id + ", " + "executed" + ", " + "now()" + ", " + int(
                            execution.amount) + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        ###(New order) alive -> False
                        sql = "UPDATE TRANSACTION SET alive = FALSE WHERE TRANSACTION.transaction_id = " + new_transaction_id + ";"
                        cur.execute(sql)
                        ###(New order) add to HISTORY
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + int(
                            execution.account_id) + ", " + new_transaction_id + ", " + "executed" + ", " + "now()" + ", " + int(
                            execution.amount) + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        execution.amount -= old_amount
                else:
                    break

        else:
            ### Selling
            shares = execution.amount
            sql = "SELECT shares FROM POSITION WHERE POSITION.account_id = " + account_id + " POSITION.symbol = '" + execution.symbol + "' ;"
            cur.execute(sql)
            result = cur.fetchone()
            if (result[0] < int(execution.amount)):
                error = "The amount of selling is higher than you own!"
                print("error occurs in Order! ", error)

            ### add to TRANSACTIOn and HISTORY first
            sql = "INSERT INTO TRANSACTION(account_id, create_time, alive, amount, limitation, symbol) VALUES(" + int(
                execution.account_id) + ", " + "now()" + ", " + "TRUE" + ", " + int(execution.amount) + ", " + int(
                execution.limit) + ", '" + execution.symbol + "');"
            cur.execute(sql)
            conn.commit()
            sql = "SELECT currval(pg_get_serial_sequence('TRANSACTION','transaction_id'));"
            cur.execute(sql)
            result = cur.fetchone()  ###### PROBLEM
            new_transaction_id = result  ###### PROBLEM
            sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + account_id + ", " + new_transaction_id + ", " + "open" + ", " + "now()" + ", " + int(
                execution.amount) + ", " + int(execution.limit) + ", '" + execution.symbol + "');"
            cur.execute(sql)
            conn.commit()

            ###
            sql = "SELECT * FROM TRANSACTION WHERE TRANSACTION.symbol = '" + execution.symbol + "' TRANSACTION.limitation >= '" + execution.limit + "' + ORDER BY TRANSACTION.create_time ASC;"
            cur.execute(sql)
            buy_orders = cur.fetchall()
            for buy_order in buy_orders:
                old_transaction_id = buy_order['transaction_id']
                old_account_id = buy_order['account_id']
                old_amount = buy_order['amount']
                old_price = buy_order['price']
                symbol = buy_order['symbol']
                if execution.amount != 0:
                    if (execution.amount > -1 * old_amount):
                        ###(Old order) alive -> False
                        sql = "UPDATE TRANSACTION SET alive = FALSE WHERE TRANSACTION.transaction_id = '" + old_transaction_id + "';"
                        cur.execute(sql)
                        ###(Old order) delete open, and add executed in HISTORY
                        sql = "DELETE FROM HISTORY WHERE HISTORY.transaction_id = " + old_transaction_id + " AND HISTORY.status = open;"
                        cur.execute(sql)
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + old_account_id + ", " + old_transaction_id + ", " + "executed" + ", " + "now()" + ", " + old_amount + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        ###(New order) alive -> True
                        sql = "UPDATE TRANSACTION SET alive = TRUE WHERE TRANSACTION.transaction_id = " + new_transaction_id + ";"
                        cur.execute(sql)
                        ###(New order) add to HISTORY
                        sql = "UPDATE HISTORY SET history_shares = " + (
                                    execution.amount + old_amount) + " WHERE HISTORY.account_id = " + int(
                            execution.account_id) + " AND HISTORY.status = open ;"
                        cur.execute(sql)
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + int(
                            execution.account_id) + ", " + new_transaction_id + ", " + "executed" + ", " + "now()" + ", " + -1 * old_amount + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        execution.amount -= old_amount
                    elif (execution.amount == -1 * old_amount):
                        ###(Old order) alive -> False
                        sql = "UPDATE TRANSACTION SET alive = FALSE WHERE TRANSACTION.transaction_id = '" + old_transaction_id + "';"
                        cur.execute(sql)
                        ###(Old order) delete open, and add executed in HISTORY
                        sql = "DELETE FROM HISTORY WHERE HISTORY.transaction_id = " + old_transaction_id + " AND HISTORY.status = open;"
                        cur.execute(sql)
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + old_account_id + ", " + old_transaction_id + ", " + "executed" + ", " + "now()" + ", " + old_amount + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        ###(New order) alive -> False
                        sql = "UPDATE TRANSACTION SET alive = FALSE WHERE TRANSACTION.transaction_id = " + new_transaction_id + ";"
                        cur.execute(sql)
                        ###(New order) add to HISTORY
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + int(
                            execution.account_id) + ", " + new_transaction_id + ", " + "executed" + ", " + "now()" + ", " + -1 * old_amount + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        execution.amount -= old_amount
                    elif (execution.amount < -1 * old_amount):
                        ###(Old order) update open, and add executed in HISTORY
                        sql = "UPDATE HISTORY SET history_shares = " + old_amount + int(
                            execution.amount) + " WHERE HISTORY.transaction_id = " + old_transaction_id + " AND HISTORY.status = open;"
                        cur.execute(sql)
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + old_account_id + ", " + old_transaction_id + ", " + "executed" + ", " + "now()" + ", " + -1 * int(
                            execution.amount) + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        ###(New order) alive -> False
                        sql = "UPDATE TRANSACTION SET alive = FALSE WHERE TRANSACTION.transaction_id = " + new_transaction_id + ";"
                        cur.execute(sql)
                        ###(New order) add to HISTORY
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + int(
                            execution.account_id) + ", " + new_transaction_id + ", " + "executed" + ", " + "now()" + ", " + int(
                            execution.amount) + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        execution.amount -= old_amount


def account_handler(execution:parser.Account,conn):
    cur = conn.cursor()
    sql = "SELECT account_id FROM ACCOUNT WHERE account_id = " + execution.account_id + ";"
    cur.execute(sql)
    if (cur.rowcount != 0):
        error = "The account_id Already Existed"
        print("error occurs in Account Init! ", error)
        # msgs.append(res.ErrorResponse({"id": execution.account_id}, error))
        # break
    # msgs.append(execution.toSQL(conn))\


def position_handler(execution:parser.Position,conn):
    ### need to check whether valid or not
    cur = conn.cursor()
    sql = "SELECT account_id FROM ACCOUNT WHERE account_id = " + execution.account_id + ";"
    cur.execute(sql)
    if (cur.rowcount == 0):
        error = "The account_id doesn't exist!"
        print("error occurs in Position! ", error)
    ### if there is not errorin current execution: call toSQL()
    if (error == ""):
        execution.toSQL(conn)


def query_handler(execution:parser.Query,conn):
    ### need to check whether valid or not
    cur = conn.cursor()
    sql = "SELECT transaction_id FROM TRANSACTION WHERE transaction_id = " + execution.transaction_id + ";"
    cur.execute(sql)
    if (cur.rowcount == 0):
        error = "The transaction_id doesn't exist!"
        print("error occurs in Query! ", error)
    ### if there is not errorin current execution: call toSQL()
    if (error == ""):
        execution.toSQL(conn)


def cancel_handler(execution:parser.Cancel,conn):
    ### need to check whether valid or not
    cur = conn.cursor()
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