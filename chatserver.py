import sys
import select
import re
import socket


VERSION = '1' # chat_system version
# try input

try:
    ARGS = sys.argv[1].split(':')
    IP = str(ARGS[0])
    PORT = int(ARGS[1])
except Exception as e:
    print("Usage: python chat_server.py serv_ip:serv_port",e)
    sys.exit()
# try bind the server to address
try:
    # create a socket
    server = socket.socket()
    server.bind((IP,PORT))
except Exception as e:
    print("Not able to bind the server to the given ip:port address",e)
    sys.exit()
server.listen(100)
conns = []
conns.append(server)
temp_conns = []
perm_conns = []
perm_conns_dict = {}

def broadcast(msg,conn):
    for socket in perm_conns:
        if socket!=conn:
            try:
                socket.sendall(msg.encode('ascii'))
                #print('message sent to ',perm_conns_dict[socket])
            except Exception as e:
                print('not able to send message to', perm_conns_dict[socket])
                socket.close()
                perm_conns.remove(socket)
                del perm_conns_dict[socket]
                temp_conns.remove(socket)
def main():
    print('Chat Server started!--> Successfully Running!')
    while True:
        readsockets, writesockets, errorsockets = select.select(conns,[],[])
        for socket in readsockets:
            if socket==server:
                # Try sending the hello msg to new connection
                try:
                    newconn, addr = server.accept()
                    hello_msg = 'Hello '+VERSION
                    newconn.sendall(hello_msg.encode('ascii'))
                    conns.append(newconn)
                    temp_conns.append(newconn)
                except Exception as e:
                    print("Error can't accept connection from anonymous client", e)
                    continue # don't break or exit
            elif socket in temp_conns:
                try:
                    # try receiveing nick name
                    nick = socket.recv(1024).decode('ascii')
                    if nick:
                        received = re.search(r'NICK\s(\S*)',nick)
                        name = str(received.group(1))
                        if len(name)>12:
                            error_msg = 'Error your nick name length should be less than 13 characters'
                            socket.sendall(error_msg.encode('ascii'))
                        elif (re.search(r'!',name) or re.search(r'@',name) or re.search(r'#',name) or re.search(r'\$',name) or re.search(r'%',name) or re.search(r'\*',name) or re.search(r'\^',name)):
                            error_msg = "Error! Shouldn't use special characters in name".encode('ascii')
                            socket.sendall(error_msg.encode('ascii'))
                        elif received:
                            ok = 'OK'
                            socket.sendall(ok.encode('ascii'))
                            perm_conns.append(socket)
                            perm_conns_dict[socket] = name
                            temp_conns.remove(socket)
                        else:
                            socket.sendall('ERROR no nick set'.encode('ascii'))
                    else:
                        socket.close()
                        conns.remove(socket)
                        temp_conns.remove(socket)
                except Exception as e:
                    print("Cannot resolve nick from client sock",socket,e)
                    continue # don't break or exit
            elif socket in perm_conns:
                try:
                    msg = socket.recv(1024).decode('ascii')
                   # print('message received from',perm_conns_dict[socket],msg[4:])
                    if msg:
                        received = re.search(r'MSG\s', msg)
                        if len(msg)>259:
                            error_msg = "Error! Message shouldn't exceed 256 characters"
                            socket.sendall(error_msg.encode('ascii'))
                        elif received:
                            message_to_send = 'MSG '+str(perm_conns_dict[socket])+'> '+msg[4:]
                   #         print('msg sent')
                            broadcast(message_to_send, socket)
                        else:
                            socket.sendall('ERROR malformed command'.encode('ascii'))
                    else:
                        socket.close()
                        conns.remove(socket)
                        perm_conns.remove(socket)
                        del perm_conns_dict[socket]
                except Exception as e:
                    print("Error occured while receiving message from",perm_conns_dict[socket],e)
                    continue
            else:
                pass
    server.close()
if __name__=='__main__':
     main()


