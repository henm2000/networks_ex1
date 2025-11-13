import sys
import socket

def main():
    port = 1337
    hostname = "localhost"
    if len(sys.argv) == 2:
        hostname = sys.argv[1]
    elif len(sys.argv) == 3:
        hostname = sys.argv[1]
        port = int(sys.argv[2])
    client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    client_socket.connect((hostname,port))
    data = recv_all_strings(client_socket)
    if data != "Welcome! Please log in":
        print("error")
    else:
        while True:
            username = input("Please enter username")
            password = input("Please enter password")
            data = f"User: {username}\n Password: {password}"
            client_socket.sendall(data.encode())
            data = recv_all_strings(client_socket)
            if data != "Failed to login.":
                break
        #while True:
            #commands
        print("connected")



def recv_all_strings(sock):
    data = b""
    while True:
            chunk = sock.recv(4096)
            data += chunk
            rlist,wlist,xlist = socket.select([sock],[sock],[sock])
            if sock not in rlist:  
                break
    return data.decode('utf-8')


if __name__ == "__main__":
    main()

