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
                return res.ErrorResponse({"sym": execution.symbol, "amount": execution.amount, "limit": execution.limit}, error)

            sql = "UPDATE ACCOUNT SET balance = " + str(result[0] - (int(execution.limit) * int(
                execution.amount))) + " WHERE ACCOUNT.account_id = '" + execution.account_id + "' ;"
            cur.execute(sql)

            sql = "INSERT INTO TRANSACTION(account_id, create_time, alive, amount, limitation, symbol) VALUES(" + execution.account_id + ", " + "now()" + ", " + "TRUE" + ", " + execution.amount + ", " + execution.limit + ", '" + execution.symbol + "');"
            cur.execute(sql)
            conn.commit()
            sql = "SELECT currval(pg_get_serial_sequence('TRANSACTION','transaction_id'));"
            cur.execute(sql)
            result = cur.fetchone()  ###### PROBLEM
            new_transaction_id = str(result[0])  ###### PROBLEM
            sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + account_id + ", " + new_transaction_id + ", '" + "open" + "', " + "now()" + ", " + execution.amount + ", " + execution.limit + ", '" + execution.symbol + "');"

            cur.execute(sql)
            conn.commit()

            ###
            sql = "SELECT * FROM TRANSACTION WHERE TRANSACTION.symbol = '" + execution.symbol + "'AND TRANSACTION.limitation <= '" + execution.limit + "'AND TRANSACTION.amount < 0  ORDER BY TRANSACTION.create_time ASC;"
            cur.execute(sql)
            sell_orders = cur.fetchall()
            executed_shares = 0
            for sell_order in sell_orders:
                old_transaction_id = str(sell_order[0])
                old_account_id = str(sell_order[1])
                old_amount = sell_order[4]
                old_price = str(sell_order[5])
                symbol = str(sell_order[6])
                if int(execution.amount) != 0:
                    if (int(execution.amount) > -1 * old_amount):
                        ###(Old order) alive -> False
                        sql = "UPDATE TRANSACTION SET alive = FALSE WHERE TRANSACTION.transaction_id = '" + old_transaction_id + "';"
                        cur.execute(sql)
                        ###(Old order) delete open, and add executed in HISTORY
                        sql = "DELETE FROM HISTORY WHERE HISTORY.transaction_id = " + old_transaction_id + " AND HISTORY.status = 'open';"
                        cur.execute(sql)
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + old_account_id + ", " + old_transaction_id + ", " + "'executed'" + ", " + "now()" + ", " + str(old_amount) + ", " + old_price + ", '" + symbol + "');"
                        cur.execute(sql)
                        ###(New order) alive -> True
                        sql = "UPDATE TRANSACTION SET alive = TRUE WHERE TRANSACTION.transaction_id = " + new_transaction_id + ";"
                        cur.execute(sql)
                        ###(New order) add to HISTORY
                        sql = "UPDATE HISTORY SET history_shares = " + str( int(execution.amount) + old_amount) + " WHERE HISTORY.account_id = " +  execution.account_id + " AND HISTORY.status = 'open' ;"
                        cur.execute(sql)
                        ### the new order's amount should be deducted
                        sql = "UPDATE TRANSACTION SET amount =" + str(int(execution.amount) + old_amount) + "WHERE TRANSACTION.transaction_id = " + new_transaction_id + ";"
                        cur.execute(sql)
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + execution.account_id + ", " + new_transaction_id + ", " + "'executed'" + ", " + "now()" + ", " + str(old_amount) + ", " + old_price + ",' " + symbol + "');"
                        cur.execute(sql)
                        execution.amount = str(int(execution.amount)+old_amount)
                        executed_shares += -1 * old_amount
                    elif (int(execution.amount) == -1 * old_amount):
                        ###(Old order) alive -> False
                        sql = "UPDATE TRANSACTION SET alive = FALSE WHERE TRANSACTION.transaction_id = '" + old_transaction_id + "';"
                        cur.execute(sql)
                        ###(Old order) delete open, and add executed in HISTORY
                        sql = "DELETE FROM HISTORY WHERE HISTORY.transaction_id = " + old_transaction_id + " AND HISTORY.status = open;"
                        cur.execute(sql)
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + old_account_id + ", " + old_transaction_id + ", " + "'executed'" + ", " + "now()" + ", " + str(old_amount) + ", " + old_price + ", '" + symbol + "');"
                        cur.execute(sql)
                        ###(New order) alive -> False
                        sql = "UPDATE TRANSACTION SET alive = FALSE WHERE TRANSACTION.transaction_id = " + new_transaction_id + ";"
                        cur.execute(sql)
                        ###(New order) add to HISTORY
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + execution.account_id + ", " + new_transaction_id + ", " + "'executed'" + ", " + "now()" + ", " + str(old_amount) + ", " + old_price + ", '" + symbol + "');"
                        cur.execute(sql)
                        execution.amount = str(0)
                        executed_shares += -1 * old_amount
                    elif (int(execution.amount) < -1 * old_amount):
                        ###(Old order) update open, and add executed in HISTORY
                        sql = "UPDATE HISTORY SET history_shares = " + str(old_amount - int(execution.amount)) + " WHERE HISTORY.transaction_id = " + old_transaction_id + " AND HISTORY.status = 'open';"
                        cur.execute(sql)
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + old_account_id + ", " + old_transaction_id + ", " + "'executed'" + ", " + "now()" + ", " + execution.amount + ", " + old_price + ", '" + symbol + "');"
                        cur.execute(sql)
                        ###(New order) alive -> False
                        sql = "UPDATE TRANSACTION SET alive = FALSE WHERE TRANSACTION.transaction_id = " + new_transaction_id + ";"
                        cur.execute(sql)
                        ###(old order) update amount = old_amount - execution.amount
                        sql = "UPDATE TRANSACTION SET amount =" + str(old_amount + int(execution.amount))+"WHERE TRANSACTION.transaction_id = " + old_transaction_id + ";"
                        cur.execute(sql)
                        ###(New order) add to HISTORY
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" +  execution.account_id + ", " + new_transaction_id + ", " + "'executed'" + ", " + "now()" + ", " + str(execution.amount) + ", " + old_price + ", '" + symbol + "');"
                        cur.execute(sql)
                        executed_shares += int(execution.amount)
                        execution.amount = str(0)
            ## update the buyed shares into the buyer's account
            sql = "SELECT shares FROM POSITION WHERE account_id = '" + execution.account_id + "'AND POSITION.symbol = '" + execution.symbol+"';"
            cur.execute(sql)
            share_before_execution = cur.fetchone()
            if share_before_execution is None:
                sql = "INSERT INTO POSITION(account_id, symbol, shares) VALUES(" + execution.account_id +",'"+ execution.symbol+"'," + str(executed_shares) + ");"
                cur.execute(sql)
            else:
                sql = "UPDATE POSITION SET SHARES = "+str(executed_shares + share_before_execution[0]) +"WHERE POSITION.account_id = '"+ execution.account_id+"'AND POSITION.symbol = '" + execution.symbol +"';"
                cur.execute(sql)
            conn.commit()
        else:
            ### Selling
            shares = execution.amount
            sql = "SELECT shares FROM POSITION WHERE POSITION.account_id = " + account_id + "AND POSITION.symbol = '" + execution.symbol + "' ;"
            cur.execute(sql)
            result = cur.fetchone()
            if (result[0] < -int(execution.amount)):
                error = "The amount of selling is higher than you own!"
                print("error occurs in Order! ", error)
            sql = "UPDATE POSITION SET shares = " + str(result[0]+int(execution.amount)) + " WHERE POSITION.account_id = '" + execution.account_id + "' AND symbol = '"+ execution.symbol+ "';"
            cur.execute(sql)
            ### add to TRANSACTIOn and HISTORY first
            sql = "INSERT INTO TRANSACTION(account_id, create_time, alive, amount, limitation, symbol) VALUES(" +execution.account_id + ", " + "now()" + ", " + "'TRUE'" + ", " + execution.amount + ", " +execution.limit + ", '" + execution.symbol + "');"
            cur.execute(sql)
            conn.commit()
            sql = "SELECT currval(pg_get_serial_sequence('TRANSACTION','transaction_id'));"
            cur.execute(sql)
            result = cur.fetchone()
            new_transaction_id = str(result[0])
            sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + account_id + "," + new_transaction_id + "," + "'open'" + "," + "now()" + "," + execution.amount + "," + execution.limit + ", '" + execution.symbol + "');"
            cur.execute(sql)
            conn.commit()

            ###
            sql = "SELECT * FROM TRANSACTION WHERE TRANSACTION.symbol = '" + execution.symbol + "'AND TRANSACTION.limitation >= '" + execution.limit + "'AND TRANSACTION.amount > 0 "+" ORDER BY TRANSACTION.create_time ASC;"
            cur.execute(sql)
            buy_orders = cur.fetchall()
            for buy_order in buy_orders:
                old_transaction_id = str(buy_order[0])
                old_account_id = str(buy_order[1])
                old_amount = buy_order[4]
                old_price = str(buy_order[5])
                symbol = str(buy_order[6])
                if execution.amount != 0:
                    if (int(execution.amount) > -1 * old_amount):
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
                            execution.account_id) + ", " + new_transaction_id + ", " + "executed" + ", " + "now()" + ", " + str(-1 * old_amount) + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        execution.amount -= old_amount
                    elif (execution.amount == -1 * old_amount):
                        ###(Old order) alive -> False
                        sql = "UPDATE TRANSACTION SET alive = FALSE WHERE TRANSACTION.transaction_id = '" + old_transaction_id + "';"
                        cur.execute(sql)
                        ###(Old order) delete open, and add executed in HISTORY
                        sql = "DELETE FROM HISTORY WHERE HISTORY.transaction_id = " + old_transaction_id + " AND HISTORY.status = open;"
                        cur.execute(sql)
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + old_account_id + ", " + old_transaction_id + ", " + "executed" + ", " + "now()" + ", " + str(old_amount) + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        ###(New order) alive -> False
                        sql = "UPDATE TRANSACTION SET alive = FALSE WHERE TRANSACTION.transaction_id = " + new_transaction_id + ";"
                        cur.execute(sql)
                        ###(New order) add to HISTORY
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + int(
                            execution.account_id) + ", " + new_transaction_id + ", " + "executed" + ", " + "now()" + ", " + str(-1 * old_amount) + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        execution.amount -= old_amount
                    elif (execution.amount < -1 * old_amount):
                        ###(Old order) update open, and add executed in HISTORY
                        sql = "UPDATE HISTORY SET history_shares = " + str(old_amount + int(execution.amount)) + " WHERE HISTORY.transaction_id = " + old_transaction_id + " AND HISTORY.status = open;"
                        cur.execute(sql)
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + old_account_id + ", " + old_transaction_id + ", " + "executed" + ", " + "now()" + ", " + str(-1 * int(
                            execution.amount)) + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        ###(New order) alive -> False
                        sql = "UPDATE TRANSACTION SET alive = FALSE WHERE TRANSACTION.transaction_id = " + new_transaction_id + ";"
                        cur.execute(sql)
                        ###(New order) add to HISTORY
                        sql = "INSERT INTO HISTORY(account_id, transaction_id, status, history_time, history_shares, price, symbol) VALUES(" + execution.account_id + ", " + new_transaction_id + ", " + "executed" + ", " + "now()" + ", " + execution.amount + ", " + old_price + ", " + symbol + ");"
                        cur.execute(sql)
                        execution.amount -= old_amount


def account_handler(execution:parser.Account,conn):
    cur = conn.cursor()
    sql = "SELECT account_id FROM ACCOUNT WHERE account_id = " + execution.account_id + ";"
    cur.execute(sql)
    if (cur.rowcount != 0):
        error = "The account_id Already Existed"
        print("error occurs in Account Init! ", error)
        return res.ErrorResponse({"id": execution.account_id}, error)
        # break
    execution.toSQL(conn)
    return res.CreateResponse(execution.account_id)
    # msgs.append(execution.toSQL(conn))\


def position_handler(execution:parser.Position,conn):
    ### need to check whether valid or not
    cur = conn.cursor()
    sql = "SELECT account_id FROM ACCOUNT WHERE account_id = " + execution.account_id + ";"
    cur.execute(sql)
    if (cur.rowcount == 0):
        error = "The account_id doesn't exist!"
        print("error occurs in Position! ", error)
        return res.ErrorResponse({"id":execution.account_id,"sym":execution.sym})
    ### if there is not errorin current execution: call toSQL()
    execution.toSQL(conn)
    return res.CreateResponse(execution.account_id,execution.sym)


def query_handler(execution:parser.Query,conn):
    ### need to check whether valid or not
    cur = conn.cursor()
    sql = "SELECT transaction_id FROM TRANSACTION WHERE transaction_id = " + execution.transaction_id + ";"
    cur.execute(sql)
    if (cur.rowcount == 0):
        error = "The transaction_id doesn't exist!"
        print("error occurs in Query! ", error)
        return res.ErrorResponse({"id":execution.transaction_id})
    ### if there is not errorin current execution: call toSQL()
    sql = "SELECT * FROM TRANSACTION WHERE TRANSACTION.transaction_id = " + str(execution.transaction_id) + ";"
    print(sql)
    cur = conn.cursor()
    cur.execute(sql)
    query_results = cur.fetchall()
    # sub_transactions = []
    # for query_result in query_results:
    #     sub_transactions.append(res.SubTransaction(query_result[]))
    #TODO
    return res.QueryResponse()


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