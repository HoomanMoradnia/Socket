import socket
import threading
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext

class ChatServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Server")
        
        # Server configuration
        self.host = 'localhost'
        self.port = 8000
        self.clients = {}
        self.active_clients = 0
        self.server_socket = None
        
        # GUI Elements
        self.create_widgets()
        
    def create_widgets(self):
        # Server Controls Frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        self.start_button = tk.Button(control_frame, text="Start Server", command=self.start_server)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(control_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Log Display
        self.log_area = scrolledtext.ScrolledText(self.root, width=60, height=20, state='disabled')
        self.log_area.pack(padx=10, pady=5)
        
        # Client List
        self.client_listbox = tk.Listbox(self.root, width=60, height=10)
        self.client_listbox.pack(padx=10, pady=5)
        
    def log_message(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_area.config(state='disabled')
        self.log_area.see(tk.END)
        
    def update_client_list(self):
        self.client_listbox.delete(0, tk.END)
        for sock, (addr, username) in self.clients.items():
            self.client_listbox.insert(tk.END, f"{username} ({addr[0]})")
    
    def broadcast(self, message, sender_socket=None):
        for client_socket in self.clients:
            if client_socket != sender_socket:
                try:
                    client_socket.sendall(message.encode('utf-8'))
                except:
                    client_socket.close()
                    del self.clients[client_socket]
                    self.active_clients -= 1
                    self.update_client_list()
    
    def handle_client(self, connection, client_address):
        # Get username
        #connection.sendall("Enter your username: ".encode('utf-8'))
        username = connection.recv(1024).decode('utf-8').strip()
        self.clients[connection] = (client_address, username)
        self.active_clients += 1
        
        self.log_message(f"{username} connected from {client_address}")
        self.update_client_list()
        
        # Notify all clients
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.broadcast(f"{username} has joined the chat! ({timestamp})", connection)

        try:
            while True:
                data = connection.recv(1024).decode('utf-8')
                if not data:
                    self.log_message(f"{username} disconnected.")
                    break

                # Command handling
                if data.strip().lower() == "/exit":
                    self.log_message(f"{username} requested to exit.")
                    break

                elif data.strip().lower() == "/help":
                    help_msg = """
Available commands:
- /exit - Exit the chat
- /users - List online users
- /pm <username> <message> - Private message
- /help - Show this help"""
                    connection.sendall(help_msg.encode('utf-8'))

                elif data.strip().lower() == "/users":
                    user_list = "Online users:\n" + "\n".join(
                        [f"{user} ({addr[0]})" for sock, (addr, user) in self.clients.items()]
                    )
                    connection.sendall(user_list.encode('utf-8'))

                elif data.startswith("/pm"):
                    parts = data.split(" ", 2)
                    if len(parts) == 3:
                        target_user, msg = parts[1], parts[2]
                        sent = False
                        for sock, (addr, user) in self.clients.items():
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
                    self.log_message(f"{username}: {data}")
                    self.broadcast(f"{username} ({timestamp}): {data}", connection)

        except Exception as e:
            self.log_message(f"Error with {username}: {e}")
        finally:
            # Cleanup
            if connection in self.clients:
                del self.clients[connection]
                self.active_clients -= 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.broadcast(f"{username} has left ({timestamp})", connection)
                self.update_client_list()
            connection.close()
            self.log_message(f"{username} disconnected")

            if self.active_clients == 0 and self.server_socket:
                self.log_message("No clients left, server running")

    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            self.log_message(f"Server started on {self.host}:{self.port}")
            
            def accept_connections():
                while True:
                    try:
                        connection, address = self.server_socket.accept()
                        thread = threading.Thread(target=self.handle_client, args=(connection, address))
                        thread.start()
                    except OSError:
                        break
            
            accept_thread = threading.Thread(target=accept_connections)
            accept_thread.start()
            
        except Exception as e:
            self.log_message(f"Failed to start server: {e}")
            self.start_button.config(state=tk.NORMAL)

    def stop_server(self):
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            self.log_message("Server stopped")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatServerGUI(root)
    root.mainloop()