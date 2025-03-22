import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                print("Disconnected from the server.")
                break
            print(data)
        except:
            print("An error occurred while receiving messages.")
            break

def start_client():
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the server's address and port
    server_address = ('localhost', 8000)
    print(f"Connecting to {server_address[0]}:{server_address[1]}")
    client_socket.connect(server_address)

    # Receive the username prompt from the server
    username_prompt = client_socket.recv(1024).decode('utf-8')
    print(username_prompt, end="")  # Display the prompt without a newline

    # Ask the user for a username
    username = input()
    client_socket.sendall(username.encode('utf-8'))

    # Start a thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    try:
        while True:
            # Send data to the server
            message = input()
            client_socket.sendall(message.encode('utf-8'))

            # Exit if the user types /exit
            if message.strip().lower() == "/exit":
                print("Exiting...")
                break
    finally:
        # Clean up the connection
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    start_client()