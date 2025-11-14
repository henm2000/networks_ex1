import sys
import socket
import select
import math

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
        for newskt in newsockets:
            if newskt.sct in rlist:
                if newskt.sct is server_socket:
                    temp,_ = newskt.sct.accept()
                    sockets.append(temp)
                    newtemp = newsocket(temp)
                    newsockets.append(newtemp)
                    newtemp.answer.append("Welcome! Please log in")
                else:
                    data = recv_all_strings(newskt.sct)
                    print(data)
                    if newskt.connected == False:
                        login(data,path,newskt)
                    if data == "quit":
                        newskt.answer.append("quit")
                    else:
                        try:
                            data1, data2 = data.split(": ")
                        except:
                            newskt.answer.append("ERROR")
                            data1 = None
                        match data1:
                            case "parentheses":
                                result = parentheses(data2)
                                newskt.answer.append(result)
                            case "lcm":
                                result = lcm(data2)
                                newskt.answer.append(result)
                            case "caesar":
                                result = caesar(data2)
                                newskt.answer.append(result)
                            case _:
                                pass
                    
                    


            if newskt.sct in wlist:     
                for ans in newskt.answer:
                    data = ans.encode()
                    newskt.sct.sendall(data)
                    if "quit" in newskt.answer or "ERROR" in newskt.answer:
                        print("ERROR")
                        close(newskt,newsockets,sockets)
                newskt.answer = []


def parentheses(data):
    left = 0
    right = 0
    for char in data:
        if char == "(":
            left += 1
        elif char == ")":
            right += 1
        else:
            return "ERROR"
        if right > left:
            return "the parentheses are balanced: no"
    if right != left:
        return "the parentheses are balanced: no"
    else:
        return "the parentheses are balanced: yes"    

def lcm(data):
    try:
        data1,data2 = data.split(" ")
        x = int(data1)
        y = int(data2)
    except ValueError:
        return "ERROR"
    result = math.lcm(x,y)
    return f"the lcm is: {result}"

def caesar(data):
    try:
        data = data.split(" ")
        key = int(data[-1])
        data.pop(-1)
        plaintext = " ".join(data)
    except ValueError:
        return "error: invalid input"
    for char in plaintext:
        if not (char.isalpha() or char.isspace()):
            return "error: invalid input"
    ciphertext_chars = []
    for char in plaintext:
        if char.isspace():
            ciphertext_chars.append(" ")
        elif char.isupper():
            new_ord = (ord(char) - 65 + key) % 26 + 65
            ciphertext_chars.append(chr(new_ord))
        elif char.islower():
            new_ord = (ord(char) - 97 + key) % 26 + 97
            ciphertext_chars.append(chr(new_ord))

    ciphertext = "".join(ciphertext_chars)
    return f"the ciphertext is: {ciphertext}"
        





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

    


if __name__ == "__main__":
    main()

