import sys
import socket
import select

HEADER_SIZE = 5

def send_with_header(sock, message_str):
    """
    Encodes a string, prefixes it with a 5-byte header of its length,
    and sends it.
    """
    message_bytes = message_str.encode('utf-8')
    header_bytes = f"{len(message_bytes):<{HEADER_SIZE}}".encode('utf-8')
    sock.sendall(header_bytes + message_bytes)

def recv_n_bytes(sock, n):
    """Helper function to receive exactly n bytes."""
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Socket closed unexpectedly")
        data += chunk
    return data

def recv_with_header(sock):
    """
    Reads the 5-byte header, then reads the specified message length.
    """
    try:
        header_bytes = recv_n_bytes(sock, HEADER_SIZE)
        message_length = int(header_bytes.decode('utf-8').strip())
        message_bytes = recv_n_bytes(sock, message_length)
        return message_bytes.decode('utf-8')
    except (ConnectionError, ValueError):
        return None # Server disconnected or sent bad data

def main():
    port = 1337
    hostname = "localhost"
    if len(sys.argv) == 2:
        hostname = sys.argv[1]
    elif len(sys.argv) == 3:
        hostname = sys.argv[1]
        port = int(sys.argv[2])
    
    client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    
    try:
        client_socket.connect((hostname, port))
        data = recv_with_header(client_socket)
        if not data:
            print("Failed to connect or receive welcome")
            return

        print(data)
        if data != "Welcome! Please log in":
            print("error")
        else:
            while True:
                username = input("Please enter username: ")
                password = input("Please enter password: ")
                data = f"User: {username}\nPassword: {password}"
                send_with_header(client_socket, data)
                
                data = recv_with_header(client_socket)
                if not data:
                    print("Server disconnected.")
                    break
                
                print(data)
                if data != "Failed to login":
                    break
            
            if not data or data == "Failed to login":
                client_socket.close()
                return

            while True:
                command = input("please enter your command ")
                if command == "quit":
                    send_with_header(client_socket, command)
                    data = recv_with_header(client_socket) # Wait for server ack
                    print(data)
                    client_socket.close()
                    break
                else:
                    send_with_header(client_socket, command)
                    data = recv_with_header(client_socket)
                    if not data:
                        print("Server disconnected.")
                        break
                    print(data)

                    # --- MODIFICATION ---
                    # Check for fatal error messages from server
                    if data == "error: invalid input":
                        # This is the non-fatal caesar error.
                        # Do nothing, just loop again for next command.
                        pass
                    elif data.startswith("ERROR") or data.startswith("error:"):
                        # All other errors are fatal.
                        print("Server reported a fatal error. Closing connection.")
                        client_socket.close()
                        break
                    # --- END MODIFICATION ---

    except (ConnectionRefusedError, ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
        print("Connection to server lost.")
    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
