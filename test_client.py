import socket

try: 
    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # now connect to the web server on port 80 - the normal http port
    s.connect(("", 12345))
    msg = ""
    msg = str.encode(msg, 'utf-8')
    s.send(msg)
    s.close()
    print("done")
except:
    print("Error from client's socket")
