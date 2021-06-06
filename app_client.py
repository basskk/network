import socket
import select
from pathlib import Path
import time 
import hashlib

def send_msg(addr, line, sq):

    chunk_size = 32000 #234
    msg_body_size = chunk_size - 3 * 32 - 16 * 8
    num_of_chunks = len(line) // msg_body_size 
    if len(line) % msg_body_size == 0:
        num_of_chunks -= 1

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    chunk = 0
    while chunk < num_of_chunks + 1:
        
        msg_data = str(line[(chunk * msg_body_size):(chunk * msg_body_size + msg_body_size)])
        msg_body = str.encode(msg_data)
        
 
        checksum = hashlib.md5(msg_body).digest()

        client_sock.sendto(sq.to_bytes(4, 'big')  + chunk.to_bytes(4, 'big') + \
                num_of_chunks.to_bytes(4, 'big') + checksum + msg_body, addr)

        print("Send to server: \nsq: ", sq, "\nchunk number:", chunk, "\ntotal number of chunks:",
                num_of_chunks, "\nchecksum:", int.from_bytes(checksum, 'big'), "\ndata:", msg_data, "\n")
        
        client_sock.setblocking(0)
        ready = select.select([client_sock], [], [], 10)

        recv_msg = None
        if ready[0]:
            recv_msg, _ = client_sock.recvfrom(64)

        if recv_msg:
            sq_serv = int.from_bytes(recv_msg[:4], 'big')
            chunk_serv = int.from_bytes(recv_msg[4:], 'big')
            print("Recieve from server:", "\nsq_num:", sq_serv, "\nchunk_num:", chunk_serv, "\n")
            if chunk_serv == chunk:
                chunk += 1
    


def main():
    server_addr = ('server', 8001)
    f = open('text.txt', 'r')

    sq = 0
    d = 1
    size = sz = Path('text.txt').stat().st_size
    line = f.read(size)
    t = time.process_time() 
    while(True):
        if (time.process_time() - t >= 5):
            t = time.process_time() 
            send_msg(server_addr, line, sq)
            sq += 1

if __name__ == "__main__":
    main()