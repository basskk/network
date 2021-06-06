#!/usr/bin/env python
import struct
import socket
import sys
import hashlib


def main():
    args = sys.argv[1:]
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serv_sock.bind((args[0], int(args[1])))
    
    serv_sq = 0
    checksum = 0
    line = ''
    msg_data = ''
    chunk_serv = -1
    while True:

        recv_msg, client_addr = serv_sock.recvfrom(32000)
         
        sq = int.from_bytes(recv_msg[:4], 'big') 
        chunk = int.from_bytes(recv_msg[4:8], 'big')
        num_of_chunks = int.from_bytes(recv_msg[8:12], 'big')
        checksum = recv_msg[12:28]
        hash_object = hashlib.md5(recv_msg[28:]).digest()

        if (sq == serv_sq and chunk_serv + 1 == chunk and checksum == hash_object):
            if chunk_serv == -1:
                line = bytes.decode(recv_msg[28:])
                msg_data = line

            else:
                msg_data = bytes.decode(recv_msg[28:])
                line += msg_data

            chunk_serv += 1

        serv_sock.sendto(sq.to_bytes(4, 'big') + chunk_serv.to_bytes(4, 'big'), client_addr)

        print("Recieve from client chunk: \nsq: ", sq, "\nchunk number:", chunk, "\ntotal number of chunks: ",
                num_of_chunks, "\nchecksum: ", int.from_bytes(checksum, 'big'), "\ndata: ", msg_data, "\n")

        print("Send to client: \nsq: ", sq, "\nchunk number:", chunk_serv, '\n')


        
        if (chunk == num_of_chunks):
            print("Recieve from client full msg:", line, "\n")
            line = ''
            serv_sq += 1
            chunk_serv = -1
        
    serv_sock.close()


if __name__ == "__main__":
    main()
