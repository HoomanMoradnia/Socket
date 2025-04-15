import socket
import threading
from datetime import datetime

# Dictionary to store active client connections (key: socket, value: username)
clients = {}
# Counter to track the number of active clients
active_clients = 0
# Global variable for the server socket
server_socket = None

def broadcast(message, sender_socket=None):
    for client_socket in clients:
        if client_socket != sender_socket:
            try:
                client_socket.sendall(message.encode('utf-8'))
            except:
                # Remove the client if sending fails
                client_socket.close()
                del clients[client_socket]

def handle_client(connection, client_address):
    global active_clients
    
    # Ask the client for a username
    connection.sendall("Enter your username: ".encode('utf-8'))
    username = connection.recv(1024).decode('utf-8').strip()
    print(f"New connection from {username} ({client_address})")
    clients[connection] = (client_address, username) # Add client to the dictionary
    active_clients += 1 # Increment the active client counter
    
    # Notify all clients about the new user
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    broadcast(f"{username} has joined the chat! ({timestamp})", connection)

    try:
        while True:
            # Receive data from the client
            data = connection.recv(1024).decode('utf-8')
            if not data:
                print(f"{username} disconnected.")
                break # Exit if the client disconnects

            # Check if the client wants to exit
            if data.strip().lower() == "/exit":
                print(f"{username} requested to exit.")
                break

            elif data.strip().lower() == "/help":
                help_msg = """
Available commands:
- /exit - Exit the chat
- /users - List online users
- /pm <username> <message> - Private message
- /help - Show this help"""
                connection.sendall(help_msg.encode('utf-8'))

            # Check if the client wants to list all users
            elif data.strip().lower() == "/users":
                user_list = "Online users:\n" + "\n".join(
                    [f"{user} ({addr[0]})" for sock, (addr, user) in clients.items()]
                )
                connection.sendall(user_list.encode('utf-8'))

            # Check if the client wants to send a private message
            elif data.startswith("/pm"):
                parts = data.split(" ", 2)
                if len(parts) == 3:
                    target_user, msg = parts[1], parts[2]
                    sent = False
                    for sock, (addr, user) in clients.items():
                        if user == target_user:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            sock.sendall(f"[Private message from {username}] ({timestamp}): {msg}".encode('utf-8'))
                            sent = True
                            break
                    if sent:
                        connection.sendall(f"Private message sent to {target_user}".encode('utf-8'))
                    else:
                        connection.sendall(f"User {target_user} not found".encode('utf-8'))
                else:
                    connection.sendall("Invalid format. Use: /pm username message".encode('utf-8'))

            else:
                # Normal message broadcast
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                broadcast(f"{username} ({timestamp}): {data}", connection)

    except Exception as e:
        print(f"Error handling client {username}: {e}")
    finally:
        # Clean up the connection
        if connection in clients:
            del clients[connection] # Remove client from the dictionary
            active_clients -= 1 # Decrement the active client counter
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            broadcast(f"{username} has left ({timestamp})", connection)
        connection.close()
        print(f"{username} disconnected")

        # Shut down the server if there are no more clients
        if active_clients == 0:
            print("No more clients connected. Shutting down the server...")
            global server_socket
            if server_socket:
                server_socket.close()
                print("Server shut down.")

def start_server():
    global server_socket

    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to a specific address and port
    server_address = ('localhost', 8000)
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(5)
    print(f"Server started on {server_address}")

    try:
        while True:
            # Accept a new connection
            connection, address = server_socket.accept()

            # Start a new thread to handle the client
            thread = threading.Thread(target=handle_client, args=(connection, address))
            thread.start()
    except OSError as e:
        # Handle the case where the server socket is closed
        if server_socket:
            print(f"Server socket error: {e}")
    finally:
        # Ensure the server socket is closed
        if server_socket:
            server_socket.close()
            print("Server socket closed.")

if __name__ == "__main__":
    start_server()