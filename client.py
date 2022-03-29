import socket
from xml_parser import parse_xml

try: 
    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # now connect to the web server on port 80 - the normal http port
    s.connect(("", 12345))
    # msg = "INSERT INTO ACCOUNT(account_id, balance) VALUES(888, 10000);"
    # msg =  "<create> " \
    #               "<account id=\"123456\" balance=\"1000\"/>" \
    #               "<account id=\"13579\" balance=\"10000\"/>" \
    #                   "<symbol sym=\"SPY\">" \
    #                   "<account id=\"123456\">100000</account>" \
    #                   "</symbol>" \
    #                   "<symbol sym=\"NASDAQ\">" \
    #                   "<account id=\"13579\">50</account>" \
    #                   "</symbol>" \
    #         "</create>"
    
    msg = "<transactions id=\"123456\">" \
                            "<order sym=\"SPY\" amount=\"123\" limit=\"321\"/>" \
          "</transactions> "
    # msg = "<transactions id=\"123456\">" \
    #                         "<order sym=\"SPY\" amount=\"123\" limit=\"321\"/>" \
    #                         "<query id=\"1\"/>" \
    #                         "<cancel id=\"1\"/>" \
    #                       "</transactions> "

    # msg = "INSERT INTO POSITION(account_id, symbol, shares) VALUES(123456, 'symbol', 100000)"
   
    msg = str.encode(msg, 'utf-8')
    s.send(msg)
    s.close()
    print(msg)
    print("done")
except:
    print("Error from client's socket")
