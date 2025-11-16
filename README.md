# networks_ex1


Exercise 1 - Client-Server Application Readme

Overview

This project implements a basic client-server application. The server is designed to handle multiple clients concurrently using select and serves various computational requests. Clients can connect, log in, and send commands to the server.

Transport Protocol: TCP

We chose TCP as the transport-layer protocol for this application.

Reasoning:

Reliability: TCP guarantees that all data sent is received, and in the correct order. This is critical for our application, as a single dropped or out-of-order packet could corrupt a command or login attempt, making the application unusable.

Connection-Oriented: The application follows a clear session-based flow (Connect -> Log In -> Send Commands -> Quit). TCP's connection-oriented nature maps perfectly to this, providing a stable "session" for each client.

Simplicity: Using TCP allows us to focus on our application-level protocol without worrying about re-implementing reliability, order, or flow control, which we would have to do if we used UDP.

Application-Level Protocol

To solve the challenge of TCP being a continuous stream (where a single recv might get half a message, or multiple messages), we designed a custom, unambiguous framing protocol.

Core Concept: The 5-Byte Header

Every single message sent—by either the client or the server—is prefixed with a 5-byte header.

Header Content: This header is a 5-byte ASCII string that represents the exact length of the data message that follows. The number is left-padded with spaces.

Example 1: To send "Hello" (5 bytes), the sender first sends the header b"5    " followed by b"Hello".

Example 2: To send "Welcome! Please log in" (24 bytes), the sender first sends b"24   " followed by the message.

Stateful Receiving: This protocol allows the receiver (both client and server) to operate in a simple, stateful way, guaranteeing no data is read incorrectly.

State 1: Waiting for Header: The receiver reads data into a buffer until it has at least 5 bytes. If it receives only 3 bytes, it waits for the next 2.

State 2: Waiting for Body: Once 5 bytes are received, they are parsed to get the message length, N. The receiver now knows it must read exactly N more bytes. If it's expecting 24 bytes but only receives 10, it stores them and waits for the remaining 14.

Processing: Once the full N bytes of the message body have been received, the complete message is processed. The receiver then returns to State 1 to wait for the next 5-byte header.

This method robustly handles partial messages (slow networks) and multiple messages arriving in one recv call (the receiver simply loops, processing each complete message from its buffer).

Protocol Flow

Connection: Client connects to the server.

Server Sends: Welcome! Please log in

Client Sends: User: {username}\nPassword: {password}

Server Responds:

On success: Hi {username}, good to see you (Client proceeds to command loop).

On failure: Failed to login (Client stays in the login loop and tries again).

On fatal error: ERROR: ... (Server disconnects).

Command Loop (Post-Login):

Client Sends: A command, e.g., lcm: 10 20 or caesar: Hello! 2 or quit.

Server Responds:

Success: the lcm is: 20 or the ciphertext is: jgnnq (Connection stays open).

Non-Fatal Error: error: invalid input (This only happens for the caesar command if the string contains invalid characters. The connection stays open).

Fatal Error: ERROR or ERROR: Unknown command (Server disconnects).

Quit: quit (Server disconnects).
