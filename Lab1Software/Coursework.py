#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# The modules required
import struct
import sys
import socket
import secrets

list = {
    "key_list": [],
    "server_key_list": [],
    "chunk_list": []
}

def send_and_receive_tcp(address, port, message):
    # initialize variables to track encrypt, multipart and parity feature
    enc = False
    mul = False
    par = False
    # add \r\n if the message does not already end with it
    if not message.endswith("\\r\\n"):
        message += "\r\n"
    # check for encryption feature
    if "ENC" in message:
        enc = True
        list["key_list"] = get_key_list()
        if message.endswith("\r\n"):
            message += "\r\n".join(list["key_list"]) + "\r\n.\r\n"
        if message.endswith("\\r\\n"):
            message = message[: message.index("\\")]
            message += "\r\n" + "\r\n".join(list["key_list"]) + "\r\n.\r\n"
    # check for multipart feature
    if "MUL" in message:
        mul = True
    # check for parity feature
    if "PAR" in message:
        par = True
    if "MUL" in message or "PAR" in message and "ENC" not in message:
        if message.endswith("\\r\\n"):
            message = message[: message.index("\\")]

    print("You gave arguments: {} {} {}".format(address, port, message))
    # create TCP socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect socket to given address and port
    tcp_socket.connect((address, port))
    # python3 sendall() requires bytes like object. encode the message with str.encode() command
    tcp_socket.sendall(message.encode())
    # send given message to socket
    # receive data from socket
    received_data = tcp_socket.recv(4096)
    # data you received is in bytes format. turn it to string with .decode() command
    received_data = received_data.decode()
    # print received data
    print("\nReceived message using TCP: " + received_data)
    # close the socket
    tcp_socket.close()
    # Get your CID and UDP port from the message
    data = received_data.split(" ")
    cid = data[1]
    udp_port = int(data[2].split("\r\n")[0])
    # Continue to UDP messaging. You might want to give the function some
    # other parameters like the above mentioned cid and port.
    send_and_receive_udp(address, cid, udp_port, enc, mul, par, data[2])
    return


def send_and_receive_udp(address, cid, udp_port, enc, mul, par, keys):
    '''
    Implement UDP part here.
    '''
    # initial message
    message = "Hello from " + cid + "\r\n"

    print("Sending {}\n".format(repr(message)))
    # create UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Encryption
    if enc:
        # get the keys from the server
        list["server_key_list"] = keys.split("\r\n")[1: -2]
        # encrypt the initial message
        key = list["key_list"].pop(0)
        message = xor(message, key)

    # pack first message
    data = pack_packet(message, cid)
    # send the first UDP message to server
    udp_socket.sendto(data, (address, udp_port))

    # receive and send UDP messages
    send(address, udp_port, udp_socket, enc, mul, par)

    # close the socket
    udp_socket.close()
    return


def send(address, udp_port, sock, enc, mul, par):
    ack = True
    eom = False
    done = False
    full_message = ""
    remain = 0
    temp_ack = True
    # loop though the last message
    while not eom:
        while not done:
            data = sock.recv(4096)
            # unpack the packet
            cid, ack, eom, data_remaining, length, message = struct.unpack("!8s??HH128s", data)
            # decode the message
            message = message.decode()
            # filter the message to only contain the content
            message = message[:length]
            # if it is the last message, print message
            if eom:
                print(message)
            # if parity feature is needed
            if par:
                # check for parity
                message = check_parity(message)
                # if incorrect
                if message == "":
                    ack = False
                else:
                    ack = True
                temp_ack = ack
            # if encryption feature is needed
            if enc:
                # decrypt message from server
                if len(list["server_key_list"]) != 0:
                    # get 1 server key and remove it from the list
                    server_key = list["server_key_list"].pop(0)
                    message = xor(message, server_key)
            # add the message to the full message   
            full_message += message
            # update the done value
            done = data_remaining <= 0
        # if not the last message
        if not eom:
            # if the multipart feature is needed
            if mul:
                # split message into chunks
                if not list["chunk_list"]:
                    remain = len(full_message)
                    full_message = " ".join(full_message.split(" ")[::-1])                    
                    msg = ""
                    length = 0
                    for i in range(len(full_message)):
                        msg += full_message[i]
                        length += 1
                        if length == 64 or i == len(full_message) - 1:
                            length = 0
                            list["chunk_list"].append(msg)
                            msg = ""
                if len(list["chunk_list"]) != 0:
                    # get 1 chunk and remove it from the list
                    message = list["chunk_list"].pop(0)
                    remain -= len(message)
            if not mul:
                # split the full message into a list of words
                word_list = message.split(" ")
                # reverse the order of the words in the list
                word_list.reverse()
                # join the reverse list back into a message
                message = ' '.join(word_list) 
            # if encryption feature is needed
            if enc:
                # encrypt the message
                if len(list["key_list"]) != 0:
                    server_key = list["key_list"].pop(0)
                    message = xor(message, server_key)
            # if parity feature is needed
            if par:
                # add parity
                message = add_parity(message)
            # if a message is not acknowledged
            if not temp_ack:
                message = "Send again"
            # pack the packet
            packet = pack_packet(message, cid.decode(), ack, eom, remain)
            # send the packet to server
            sock.sendto(packet, (address, udp_port))
            # if finish handle a message, clean the value of the full_message and done to start handle the next message
            if remain == 0:
                full_message = ""
                done = False
# pack the packet
def pack_packet(message, cid, ack=True, eom=False, data_remaining=0):
    packet = struct.pack("!8s??HH128s", cid.encode(), ack, eom, data_remaining, len(message), message.encode())
    return packet

# functions for parity feature
def get_parity(n):
    while n > 1:
        n = (n >> 1) ^ (n & 1)
    return n

# add even parity bit to each character in the message content
def add_parity(message):
    a_message = ""
    for character in message:
        character = ord(character)
        character <<= 1
        character += get_parity(character)
        a_message += chr(character)
    return a_message

# check if the parity is performed correctly
def check_parity(message):
    a_message = ""
    for character in message:
        character = ord(character)
        char = character >> 1
        if (character & 1) != get_parity(char):
            return ""
        a_message += chr(char)
    return a_message


# get random key with secrets
def get_random_key():
    key = secrets.token_hex(32)
    return key

# encrypt the message with key
def xor(message, key):
    result = str()
    if len(message) > len(key):
        return None
    for i in range(len(message)):
        m = ord(message[i])
        k = ord(key[i])
        result += chr(m ^ k)
    return result

# save the key get from the key exchange to the key list
def get_key_list():
    key_list = []
    for i in range(0, 20):
        key_list.append(get_random_key())
    return key_list
                

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