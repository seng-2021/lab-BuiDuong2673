#!/usr/bin/python

import select
import socket
import string

'''
This is a template for lab3 exercise 2. It creates a server that listens for TCP and UDP connections and when it receives one it will execute either handle_tcp() or handle_udp() function. 
'''

# Hard coded values. You are allowed to hard code the target servers address if you like.
'''
If the port is not available use another one. You can't use the same ports as other groups so find a unique value from around 21XX port range 
'''
TCP_PORT = 21069 #21000
UDP_PORT = 21069 #21000
HOST = "195.148.20.105"
PORT = 20000

def handle_tcp(sock):
    '''
    This function should do the following:
    * When receiving a message from the client print the message content and somehow implicate where it came from. For example "Client sent X"
    * Create a TCP socket.
    * Forward the message to the server using the socket.
    * Print what you received from the server
    * Forward it to the client.
    * Close socket
    '''
    # receive message from client
    client, address = sock.accept()
    client_message = client.recv(4096)
    # decode the client message
    decode_client_message = client_message.decode()
    # print the message that client sent
    print("Client sent " + decode_client_message)
    # create TCP socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect socket to given address and port
    tcp_socket.connect((HOST, PORT))
    # send client message to socket
    tcp_socket.sendall(client_message)
    # receive data from server
    server_message = tcp_socket.recv(4096)
    # decode the data
    decode_server_message = server_message.decode()
    # print what I receive from server
    print("Server message: " + decode_server_message)
    # close the socket
    tcp_socket.close()
    # forward it to the client
    client.sendall(server_message)
    return


def handle_udp(sock):
    '''
    This function should do the following
    * When receiving a message from the client print the message content and somehow implicate where it came from. For example "Client sent X"
    * Create a UDP socket
    * Forward the message to the server using the socket.
    * A loop that does the following:
        * Print what you received from the server
        * Forward it to the client.
        * Break. DO NOT use message content as your break logic (if "QUIT" in message). Use socket timeout or some other mean.  
    * Close socket
    '''
    # receive message from client
    client_message, client_address = sock.recvfrom(4096)
    # decode the message
    decode_client_message = client_message.decode()
    # print the message
    print("Client sent " + decode_client_message)
    # create UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # forward the messgae to the server using the socket
    udp_socket.sendto(client_message, (HOST, PORT))
    udp_socket.settimeout(1)
    # loop
    while True:
        try: 
            # receive message from server
            server_message = udp_socket.recv(4096)
            # decode the mssage
            decode_server_message = server_message.decode()
            # print the message that I receive from server
            print("Server message " + decode_server_message)
            # forward the message to client
            sock.sendto(server_message, client_address)
        except socket.timeout:
            # break the message when timeout
            break
    # close socket
    udp_socket.close()
    print("UDP happened")
    return




def main():
    try:
        print("Creating sockets")
        '''
        Create and bind TCP and UDP sockets here. Use hard coded values TCP_PORT and UDP_PORT to choose your port. 
        Note that while loop below  uses these sockets, so name them tcp_socket and udp_socket or modify the loop below.
        '''
        # create TCP socket
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind TCP socket
        tcp_socket.bind(('', TCP_PORT))
        # TCP socket listen
        tcp_socket.listen(0)

        # create UDP socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # bind UDP socket
        udp_socket.bind(('', UDP_PORT))
        
    except OSError:
        '''
    This will be raised if you are trying to create a socket but it is still active. Likely your code crashed or otherwise closed before you closed the socket. Wait a second and the socket should become available. Alternatively you can create a logic here that binds the socket to X_PORT+1. Doing this is not mandatory
        '''
        print("OSError was rised. Port is in use. Wait a second.")

    try:
        while True:
            i, o, e = select.select([tcp_socket, udp_socket], [], [], 5)
            if tcp_socket in i:
                handle_tcp(tcp_socket)
            if udp_socket in i:
                handle_udp(udp_socket)
    except NameError:
        print("Please create the sockets. NameError was raised doe to them missing.")
    finally:
        '''
        !!Close sockets here!!
        '''
        # close the socket
        tcp_socket.close()
        udp_socket.close()
    


if __name__ == '__main__':
    main()
