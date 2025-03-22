import socket

def start_client():
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the server's address and port
    server_address = ('localhost', 8000)
    print(f"Connecting to {server_address[0]}:{server_address[1]}")
    client_socket.connect(server_address)

    try:
        while True:
            # Send data to the server
            message = input("Enter a message (type 'exit' to quit): ")
            if message.lower() == 'exit':
                print("Disconnecting from the server...")
                break
            client_socket.sendall(message.encode('utf-8'))

            # Receive a response from the server
            data = client_socket.recv(1024).decode('utf-8')
            print(f"Message from server: {data}")
    finally:
        # Clean up the connection
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    start_client()