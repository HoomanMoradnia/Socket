import socket

def start_client():
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the server's address and port
    server_address = ('localhost', 8000)  # Must match the server's address
    print(f"Connecting to {server_address[0]}:{server_address[1]}")
    client_socket.connect(server_address) # Request to connect to the server

    try:
        # Send data to the server
        message = "Hello, Server!"
        client_socket.sendall(message.encode('utf-8'))  # Encode string to bytes
        print(f"Sent to server: {message}")

        # Receive a response from the server
        data = client_socket.recv(1024).decode('utf-8')  # Decode bytes to string
        print(f"Received from server: {data}")
    finally:
        # Clean up the connection
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    start_client()