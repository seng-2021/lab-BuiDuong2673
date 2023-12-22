#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# The modules required
import sys
import socket
'''
Use this template to create exercise 1 of lab3. Follow the hints found in the comments to complete the task.
'''
 
 
def send_and_receive_tcp(address, port, message):
    # create TCP socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect socket to given address and port
    tcp_socket.connect((address, port))
    # python3 sendall() requires bytes like object. Encode the message with .encode() command
    encoded_message = message.encode("UTF-8")
    # send given message to socket
    tcp_socket.sendall(encoded_message)
    # receive data from socket
    receive_data = tcp_socket.recv(1024)
    # data you received is in bytes format. turn it to string with .decode() command
    decoded_received_data = receive_data.decode()
    # print received data
    print("Receive data: " + decoded_received_data)
    # close the socket
    tcp_socket.close()

    # Uncomment for second part of the exercise:
    send_and_receive_udp(address, port, decoded_received_data)
    return
 
 
def send_and_receive_udp(address, port, message):
    # create UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # You turned the message in to str in previous function. Turn it back to bytes
    encoded_message = message.encode()
    # send given message to given address and port using the socket.
    udp_socket.sendto(encoded_message, (address, port))

    # Loop the following
    while True:
        # receive data from socket
        receive_data = udp_socket.recv(1024)
        # Data you receive is in bytes format. Turn it to string with .decode() command
        decoded_receive_data = receive_data.decode()
        # print received data
        print("Receive data: " + decoded_receive_data)
        # if received data contains the word 'QUIT' break the loop
        if "QUIT" in decoded_receive_data:
            break
    # close the socket
    udp_socket.close()
    return
 
 
def main():
    USAGE = 'usage: %s <server address> <server port> <message>' % sys.argv[0]
 
    try:
        # Get the server address, port and message from command line arguments
        server_address = str(sys.argv[1])
        server_tcpport = int(sys.argv[2])
        message = str(sys.argv[3])
    except IndexError:
        print("Index Error")
    except ValueError:
        print("Value Error")
    # Print usage instructions and exit if we didn't get proper arguments
        sys.exit(USAGE)
 
    send_and_receive_tcp(server_address, server_tcpport, message)
 
 
if __name__ == '__main__':
    # Call the main function when this script is executed
    main()
