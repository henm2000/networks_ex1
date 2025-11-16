import sys
import socket
import select
import math

HEADER_SIZE = 5

class newsocket:
    def __init__(self, socket):
        self.sct = socket
        self.answer = []
        self.connected = False
        
        # New fields for stateful reading
        self.read_buffer = b""
        self.bytes_expected = 0 # 0 means we are waiting for a new header

def send_with_header(sock, message_str):
    """
    Encodes a string, prefixes it with a 5-byte header of its length,
    and sends it.
    """
    message_bytes = message_str.encode('utf-8')
    header_bytes = f"{len(message_bytes):<{HEADER_SIZE}}".encode('utf-8')
    sock.sendall(header_bytes + message_bytes)

def process_message(newskt, data, path):
    """
    Handles a single, complete message from the client.
    """
    if newskt.connected == False:
        login(data, path, newskt)
    elif data == "quit":
        newskt.answer.append("quit")
    else:
        try:
            data1, data2 = data.split(": ", 1)
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
                if data1: # If split worked but command is unknown
                    newskt.answer.append("ERROR: Unknown command")
                # If split failed, ERROR was already appended

def main():
    if len(sys.argv) < 2:
        print("Usage: python server.py <user_file_path> [port]")
        sys.exit(1)

    port = 1337
    path = sys.argv[1]
    if len(sys.argv) == 3:
        port = int(sys.argv[2])
        
    server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    server_socket.bind(("", port))
    server_socket.listen()
    
    newserver_socket = newsocket(server_socket)
    
    sockets = [server_socket]
    newsockets = [newserver_socket]
    
    print(f"Server listening on port {port}...")

    while True:
        try:
            rlist, wlist, _ = select.select(sockets, sockets, [])
            
            for newskt in newsockets[:]: 
                
                # Handle Reading
                if newskt.sct in rlist:
                    if newskt.sct is server_socket:
                        temp, _ = newskt.sct.accept()
                        sockets.append(temp)
                        newtemp = newsocket(temp)
                        newsockets.append(newtemp)
                        newtemp.answer.append("Welcome! Please log in")
                        print(f"New connection from {temp.getpeername()}")
                    else:
                        try:
                            data_chunk = newskt.sct.recv(4096)
                            if not data_chunk:
                                print(f"Client {newskt.sct.getpeername()} disconnected.")
                                close(newskt, newsockets, sockets)
                                continue

                            newskt.read_buffer += data_chunk

                            while True:
                                if newskt.bytes_expected == 0: 
                                    if len(newskt.read_buffer) >= HEADER_SIZE:
                                        header = newskt.read_buffer[:HEADER_SIZE].decode('utf-8')
                                        newskt.bytes_expected = int(header.strip())
                                        newskt.read_buffer = newskt.read_buffer[HEADER_SIZE:]
                                    else:
                                        break 
                                
                                if newskt.bytes_expected > 0: 
                                    if len(newskt.read_buffer) >= newskt.bytes_expected:
                                        message_data = newskt.read_buffer[:newskt.bytes_expected]
                                        newskt.read_buffer = newskt.read_buffer[newskt.bytes_expected:]
                                        newskt.bytes_expected = 0
                                        
                                        print(f"Processing message: {message_data.decode('utf-8')}")
                                        process_message(newskt, message_data.decode('utf-8'), path)
                                    else:
                                        break
                        
                        except (ConnectionResetError, BrokenPipeError, ValueError, OSError) as e:
                            print(f"Error on socket: {e}")
                            close(newskt, newsockets, sockets)
                            continue
                
                # Handle Writing
                if newskt.sct in wlist and newskt.answer:
                    try:
                        ans = newskt.answer.pop(0)
                        send_with_header(newskt.sct, ans)
                        
                        # --- MODIFICATION ---
                        # Check for any message that should terminate the connection
                        is_terminating = False
                        if ans == "quit":
                            is_terminating = True
                        elif ans == "error: invalid input":
                            # This is the special Caesar (invalid char) error. DO NOT terminate.
                            is_terminating = False
                        elif ans.startswith("ERROR") or ans.startswith("error:"):
                            # ALL OTHER errors are fatal.
                            is_terminating = True
                        # --- END MODIFICATION ---

                        if is_terminating:
                            print(f"Closing connection after sending: {ans}")
                            close(newskt, newsockets, sockets)
                            
                    except (ConnectionResetError, BrokenPipeError, OSError) as e:
                        print(f"Write error: {e}")
                        if newskt in newsockets: # Avoid double-close
                            close(newskt, newsockets, sockets)
        
        except KeyboardInterrupt:
            print("\nShutting down server.")
            for skt in sockets:
                skt.close()
            break


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
        data1, data2 = data.split(" ")
        x = int(data1)
        y = int(data2)
    except ValueError:
        return "ERROR"
    result = math.lcm(x, y)
    return f"the lcm is: {result}"

def caesar(data):
    try:
        parts = data.split(" ")
        if len(parts) < 2:
            return "ERROR: Invalid key/format"
        key = int(parts[-1])
        plaintext = " ".join(parts[:-1]).lower()
    except ValueError:
        return "ERROR: Invalid key/format"
    
    if not plaintext:
        return "ERROR: Invalid key/format"

    # --- MODIFICATION ---
    # This check now returns the NON-FATAL error
    for char in plaintext:
        if not (char.isalpha() or char.isspace()):
            return "error: invalid input"
    # --- END MODIFICATION ---
            
    ciphertext_chars = []
    for char in plaintext:
        if char.isspace():
            ciphertext_chars.append(" ")
        else:
            new_ord = (ord(char) - 97 + key) % 26 + 97
            ciphertext_chars.append(chr(new_ord))

    ciphertext = "".join(ciphertext_chars)
    return f"the ciphertext is: {ciphertext}"
        
def close(newskt, newsockets, sockets):
    print(f"Closing socket {newskt.sct.fileno()}")
    if newskt.sct in sockets:
        sockets.remove(newskt.sct)
    if newskt in newsockets:
        newsockets.remove(newskt)
    newskt.sct.close()
    return None
     
                       
def login(data, path, newskt):
    try:
        users, passwords = data.split("\n")
        user1, user2 = users.split(": ", 1) 
        password1, password2 = passwords.split(": ", 1)
    except ValueError:
        user1 = None
        password1 = None
        user2 = None
        password2 = None
    
    if user1 != "User" or password1 != "Password":
        print(f"Login format error: {user1} / {password1}")
        newskt.answer.append("ERROR")
        return None
        
    try:
        with open(path, "r") as file:
            for line in file:
                line = line.strip()
                if not line: continue
                
                correct_user, correct_password = line.split()
                if user2 == correct_user and password2 == correct_password:
                    newskt.connected = True
                    newskt.answer.append(f"Hi {user2}, good to see you")
                    return None
        
        newskt.answer.append("Failed to login")
        
    except FileNotFoundError:
        print(f"Error: Login file '{path}' not found.")
        newskt.answer.append("ERROR")
    except Exception as e:
        print(f"Error during login: {e}")
        newskt.answer.append("ERROR")
    
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python server.py <user_file_path> [port]")
        sys.exit(1)
    main()
