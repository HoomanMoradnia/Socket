import socket

def start_server():
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    server_address = ('localhost', 8000)  # Use any available port
    print(f"Starting server on {server_address[0]}:{server_address[1]}")
    server_socket.bind(server_address) # Bind the socket to the address and port

    # Listen for incoming connections (max 1 client for now)
    server_socket.listen(1)
    print("Waiting for a connection...")

    # Accept a connection
    connection, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    try:
        # Receive data from the client
        data = connection.recv(1024).decode('utf-8')  # Decode bytes to string
        print(f"Received from client: {data}")

        # Send a response back to the client
        response = "Hello, Client!"
        connection.sendall(response.encode('utf-8'))  # Encode string to bytes
        print(f"Sent to client: {response}")
    finally:
        # Clean up the connection
        connection.close()
        print("Connection closed.")
        server_socket.close()
        print("Server shut down.")

if __name__ == "__main__":
    start_server()