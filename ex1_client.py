import sys
import socket
import select

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
    print('hello')
    data = recv_all_strings(client_socket)
    print('2')
    print(data)
    if data != "Welcome! Please log in":
        print("error")
    else:
        
        while True:
            username = input("Please enter username: ")
            password = input("Please enter password: ")
            data = f"User: {username}\nPassword: {password}"
            client_socket.sendall(data.encode())
            data = recv_all_strings(client_socket)
            print(data)
            if data != "Failed to login":
                break
        #while True:
            #commands
        data = recv_all_strings(client_socket)
        print(data)


def recv_all_strings(sock):
    data = b""
    while True:
            chunk = sock.recv(4096)
            data += chunk
            rlist,wlist,xlist = select.select([sock],[sock],[sock],1)
            if sock not in rlist:  
                break
    return data.decode('utf-8')


if __name__ == "__main__":
    main()

