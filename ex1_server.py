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
        print('1')
        rlist,wlist,_= select.select(sockets,sockets,sockets)
        print('2')
        for skt in newsockets:
            if skt.sct in rlist:
                if skt.sct is server_socket:
                    temp,_ = skt.sct.accept()
                    sockets.append(temp)
                    newtemp = newsocket(temp)
                    newsockets.append(newtemp)
                    newtemp.answer.append("Welcome! Please log in")
                    print('1')
                else:
                    data = recv_all_strings(skt.sct)
                    print(data)
                    if skt.connected == False:
                        login(data,path,skt)


            if skt.sct in wlist:     
                for ans in skt.answer:
                    data = ans.encode()
                    skt.sct.sendall(data)
                    if "quit" in skt.answer or "ERROR" in skt.answer:
                        print("ERROR")
                        close(skt,newsockets,sockets)
                skt.answer = []



def close(newskt,newsockets,sockets):
    print("close")
    sockets.remove(newskt.sct)
    newsockets.remove(newskt)
    newskt.sct.close()
    return None

            
    

                       
def  login(data,path,newskt):
    try:
        users,passwords = data.split("\n")
        user1, user2 = users.split(": ") 
        password1, password2 = passwords.split(": ")
    except ValueError:
        user1 = None
        password1 = None
        user2 = None
        password2 = None
    print(2)
    if user1 !="User" or password1 !="Password":
        print(f"{user1} {user2} {password1} {password2}")
        newskt.answer.append("ERROR")
        return None
    with open(path,"r") as file:
        for line in file:
            print(line)
            correct_user, correct_password = line.split()
            print(correct_user)
            if user2 == correct_user and password2 == correct_password:
                newskt.connected = True
                newskt.answer.append(f"Hi {user2}, good to see you")
                return None
        newskt.answer.append("Failed to login")
    return None

   



def recv_all_strings(sock):
    data = b""
    while True:
            chunk = sock.recv(4096)
            data += chunk
            rlist,_,__ = select.select([sock],[sock],[sock],1)
            if sock not in rlist or not chunk:  
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

