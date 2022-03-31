import socket
from logging import exception

if __name__ == '__main__':
    try:
        # create an INET, STREAMing socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # now connect to the web server on port 80 - the normal http port
        s.connect(("localhost", 12345))
        msg = "This is the end!"
        msg = str(len(msg)) + '\r\n' + msg
        msg = str.encode(msg, 'utf-8')
        s.send(msg)
        s.close()
        print("done")
    except(exception):
        print(exception)
        print("Error from client's socket")
