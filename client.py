import socket

try: 
    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # now connect to the web server on port 80 - the normal http port
    s.connect(("", 12345))
    msg = "INSERT INTO ACCOUNT(account_id, balance) VALUES(18, 100);"
    msg = str.encode(msg, 'utf-8')
    s.send(msg)
    s.close()
    print("done")
except:
    print("Error from client's socket")
