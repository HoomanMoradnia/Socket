import socket
import threading

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
    clients[connection] = username  # Add client to the dictionary
    active_clients += 1  # Increment the active client counter

    # Notify all clients about the new user
    broadcast(f"{username} has joined the chat!", connection)

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

            # Broadcast the message to all other clients
            message = f"{username}: {data}"
            print(f"Received from {username}: {data}")
            broadcast(message, connection)
    finally:
        # Clean up the connection
        connection.close()
        del clients[connection]  # Remove client from the dictionary
        active_clients -= 1  # Decrement the active client counter
        print(f"Connection with {username} closed.")

        # Notify all clients that the user has left
        broadcast(f"{username} has left the chat.", connection)

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