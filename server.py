import socket
import threading

# Dictionary to store active client connections
clients = {}
# Counter to track the number of active clients
active_clients = 0
# Global variable for the server socket
server_socket = None

def handle_client(connection, client_address):
    global active_clients
    print(f"New connection from {client_address}")
    clients[connection] = client_address  # Add client to the dictionary
    active_clients += 1  # Increment the active client counter

    try:
        while True:
            # Receive data from the client
            data = connection.recv(1024).decode('utf-8')
            if not data:
                print(f"Client {client_address} disconnected.")
                break  # Exit if the client disconnects

            print(f"Message from {client_address}: {data}")

            # Send a response back to the client
            response = f"Server: {data}"
            connection.sendall(response.encode('utf-8'))
    finally:
        # Clean up the connection
        connection.close()
        del clients[connection]  # Remove client from the dictionary
        active_clients -= 1  # Decrement the active client counter
        
        # Clean up the connection
        if active_clients == 0:
            print("No more clients connected.")
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

    # Listen for incoming connections (max 5 client for now)
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