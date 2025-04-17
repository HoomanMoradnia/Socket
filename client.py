import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime

class ChatClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")
        
        # Client configuration
        self.host = 'localhost'
        self.port = 8000
        self.client_socket = None
        self.username = ""
        
        # GUI Elements
        self.create_widgets()
        
    def create_widgets(self):
        # Connection Frame
        connection_frame = tk.Frame(self.root)
        connection_frame.pack(pady=10)
        
        tk.Label(connection_frame, text="Username:").pack(side=tk.LEFT)
        self.username_entry = tk.Entry(connection_frame, width=20)
        self.username_entry.pack(side=tk.LEFT, padx=5)
        
        self.connect_button = tk.Button(connection_frame, text="Connect", command=self.connect_to_server)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        self.disconnect_button = tk.Button(connection_frame, text="Disconnect", command=self.disconnect_from_server, state=tk.DISABLED)
        self.disconnect_button.pack(side=tk.LEFT, padx=5)
        
        # Chat Display
        self.chat_area = scrolledtext.ScrolledText(self.root, width=60, height=20, state='disabled')
        self.chat_area.pack(padx=10, pady=5)
        
        # Message Entry
        message_frame = tk.Frame(self.root)
        message_frame.pack(pady=10)
        
        self.message_entry = tk.Entry(message_frame, width=50)
        self.message_entry.pack(side=tk.LEFT, padx=5)
        self.message_entry.bind("<Return>", self.send_message)
        
        self.send_button = tk.Button(message_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT)
        
        # Disable message entry until connected
        self.message_entry.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
    
    def log_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)
    
    def connect_to_server(self):
        self.username = self.username_entry.get().strip()
        if not self.username:
            messagebox.showerror("Error", "Please enter a username")
            return
            
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            
            # Send username to server
            self.client_socket.sendall(self.username.encode('utf-8'))
            
            # Start thread to receive messages
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Update UI
            self.username_entry.config(state=tk.DISABLED)
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.message_entry.config(state=tk.NORMAL)
            self.send_button.config(state=tk.NORMAL)
            
            self.log_message(f"Connected to server as {self.username}")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
    
    def disconnect_from_server(self):
        if self.client_socket:
            try:
                self.client_socket.sendall("/exit".encode('utf-8'))
            except:
                pass
            self.client_socket.close()
            self.client_socket = None
            
        # Update UI
        self.username_entry.config(state=tk.NORMAL)
        self.connect_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.DISABLED)
        self.message_entry.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        
        self.log_message("Disconnected from server")
    
    def send_message(self, event=None):
        if not self.client_socket:
            return
            
        message = self.message_entry.get().strip()
        if not message:
            return
            
        try:
            # Display the message in the sender's chat immediately
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_message(f"You ({timestamp}): {message}")
            
            # Send the message to server
            self.client_socket.sendall(message.encode('utf-8'))
            self.message_entry.delete(0, tk.END)
        except Exception as e:
            self.log_message(f"Failed to send message: {e}")
            self.disconnect_from_server()
            
    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                    
                # Don't display messages that start with "You" (already shown)
                if not data.startswith("You"):
                    self.root.after(0, self.log_message, data)
            except:
                break
                
        self.root.after(0, self.disconnect_from_server)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientGUI(root)
    root.mainloop()