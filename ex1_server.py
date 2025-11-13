import sys
import socket
import select

def main():
    port = 1337
    path = sys.argv[1]
    if len(sys.argv) == 3:
        port = int(sys.argv[2])
    server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    server_socket.bind(("",port))
    server_socket.listen()
    newserver_socket = newsocket(server_socket)
    sockets = [server_socket]
    newsockets = [newserver_socket]
    while True:
        rlist,wlist,_= select.select(sockets,sockets,sockets)
        for skt in newsockets:
            if skt.sct in rlist:
                if skt.sct is server_socket:
                    temp,_ = skt.sct.accept()
                    sockets.append(temp)
                    newtemp = newsocket(temp)
                    newsockets.append(newtemp)
                    newtemp.answer.append("Welcome! Please log in")
                else:
                    data = recv_all_strings(skt.sct)
                    if skt.connected == False:
                        check_connection(data,path,skt)
                    #handling other functions 
            if skt.sct in wlist:     
                for ans in skt.answer:
                    data = ans.encode()
                    skt.sct.sendall(data)


                       
def  check_connection(data,path,newskt):
    users,passwords = data.split("\n")
    user1, user2 = users.split(": ") 
    password1, password2 = passwords.split(": ")
    if user1 !="User" or password1 !="Password":
        newskt.answer.append("Failed to login")
        return None
    with open(path,"r") as file:
        for line in file:
            correct_user,correct_password = line.split("\t")
            if user2 == correct_user and password2 == correct_password:
                newskt.connected = True
                newskt.answer.append(f"Hi {user2}, good to see you.")
                return None
        newskt.answer.append("Failed to login.")
    return None

    



def recv_all_strings(sock):
    data = b""
    while True:
            chunk = sock.recv(4096)
            data += chunk
            rlist,_,__ = select.select([sock],[sock],[sock])
            if sock not in rlist:  
                break
    return data.decode('utf-8')

class newsocket:
    def __init__(self,socket):
        self.sct = socket
        self.answer = []
        self.connected = False
    def closing(self):
        self.skt.close()
    


if __name__ == "__main__":
    main()

