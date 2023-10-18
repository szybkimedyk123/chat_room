from PySide2.QtWidgets import QApplication, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QTextEdit, QVBoxLayout, QWidget
from PySide2.QtCore import Qt, QThread, Signal
import threading
import socket
import os


class ChatServer(QThread):
    client_connected = Signal(object)

    def __init__(self):
        super().__init__()
        self.socket = None
        self.clients = []

    def start_server(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen()

        self.start()

    def run(self):
        while True:
            client_socket, address = self.socket.accept()
            self.add_client(client_socket)

    def add_client(self, client_socket):
        client = ChatClient(client_socket, self)
        self.clients.append(client)
        self.client_connected.emit(client)
        client.start()

    def remove_client(self, client):
        self.clients.remove(client)


class ChatClient(QThread):
    message_received = Signal(str)
    client_disconnected = Signal(object)

    def __init__(self, socket, server):
        super().__init__()
        self.socket = socket
        self.server = server

    def run(self):
        while True:
            data = self.socket.recv(1024)
            if not data:
                self.disconnect()
                break
            try:
                message = data.decode('utf-8')
            except UnicodeDecodeError:
                message = data.decode('latin-1')
            self.message_received.emit(message)

    def send_message(self, message):
        self.socket.sendall(message.encode('utf-8'))

    def disconnect(self):
        self.socket.close()
        self.server.remove_client(self)
        self.client_disconnected.emit(self)


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Server')

        self.message_box = QTextEdit()
        self.message_box.setReadOnly(True)

        self.message_input = QLineEdit()

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_message)

        self.upload_button = QPushButton('Upload')
        self.upload_button.clicked.connect(self.upload_file)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.upload_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.message_box)
        main_layout.addLayout(input_layout)

        self.setLayout(main_layout)

    def send_message(self):
        message = self.message_input.text()
        self.message_input.clear()
        self.message_box.append(f"Serwer > {message}")
        for client in self.server.clients:
            client.send_message(message)

    def receive_message(self, message):
        self.message_box.append(f"Klient < {message}")

    def client_connected(self, client):
        client.message_received.connect(self.receive_message)
        client.client_disconnected.connect(lambda: self.client_disconnected(client))
        self.message_box.append(f"Client connected: {client.socket.getpeername()}")

    def client_disconnected(self, client):
        self.message_box.append(f"Client disconnected: {client.socket.getpeername()}")

    def set_server(self, server):
        self.server = server
        self.server.client_connected.connect(self.client_connected)

    def upload_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Upload File', os.getenv('HOME'),
                                                   filter='Word Documents (*.docx)')
        if file_name:
            with open(file_name, 'rb') as f:
                file_size = os.path.getsize(file_name)
                for client in self.server.clients:
                    client.socket.sendall(str(file_size).encode('utf-8'))
                    chunk = f.read(1024)
                    while chunk:
                        client.socket.sendall(chunk)
                        chunk = f.read(1024)


if __name__ == '__main__':
    app = QApplication([])
    window = ChatWindow()

    server = ChatServer()
    server.start_server('localhost', 9999)
    window.set_server(server)

    window.show()
    app.exec_()