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

def send_private_message(sender_socket, target_username, message):
    for client_socket, username in clients.items():
        if username == target_username:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                client_socket.sendall(f"[Private from {clients[sender_socket]}] ({timestamp}): {message}".encode('utf-8'))
                return True
            except:
                # Remove the client if sending fails
                client_socket.close()
                del clients[client_socket]
    return False

def handle_client(connection, client_address):
    global active_clients

    # Ask the client for a username
    connection.sendall("Enter your username: ".encode('utf-8'))
    username = connection.recv(1024).decode('utf-8').strip()
    print(f"New connection from {username} ({client_address})")
    clients[connection] = username  # Add client to the dictionary
    active_clients += 1  # Increment the active client counter

    # Notify all clients about the new user
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    broadcast(f"{username} has joined the chat! ({timestamp})", connection)

    try:
        while True:
            # Receive data from the client
            data = connection.recv(1024).decode('utf-8')
            if not data:
                print(f"{username} disconnected.")
                break  # Exit if the client disconnects
            
            # Check if the client wants to exit
            if data.strip().lower() == "/exit":
                print(f"{username} requested to exit.")
                break

            # Check if the client wants to list all users
            if data.strip().lower() == "/users":
                user_list = "\nConnected users:\n" + "\n".join([f"{user} ({addr[0]})" for sock, (addr, user) in clients.items()])
                connection.sendall(user_list.encode('utf-8'))
                continue

            # Check if the client wants to send a private message
            if data.startswith("/pm"):
                parts = data.split(" ", 2)
                if len(parts) == 3:
                    target_username, message = parts[1], parts[2]
                    if send_private_message(connection, target_username, message):
                        connection.sendall(f"Private message sent to {target_username}.".encode('utf-8'))
                    else:
                        connection.sendall(f"User {target_username} not found.".encode('utf-8'))
                else:
                    connection.sendall("Invalid private message format. Use /pm <username> <message>".encode('utf-8'))
                continue

            # Broadcast the message to all other clients
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"{username} ({timestamp}): {data}"
            print(f"Received from {username}: {data}")
            broadcast(message, connection)
    except Exception as e:
        print(f"Error handling client {username}: {e}")
    finally:
        # Clean up the connection
        connection.close()
        del clients[connection]  # Remove client from the dictionary
        active_clients -= 1  # Decrement the active client counter
        print(f"Connection with {username} closed.")

        # Notify all clients that the user has left
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        broadcast(f"{username} has left the chat. ({timestamp})", connection)

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
    print(f"Starting server on {server_address[0]}:{server_address[1]}")
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(5)
    print("Waiting for connections...")

    try:
        while True:
            # Accept a new connection
            connection, client_address = server_socket.accept()

            # Start a new thread to handle the client
            thread = threading.Thread(target=handle_client, args=(connection, client_address))
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