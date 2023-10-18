from PySide2.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QTextEdit, QPushButton, QFileDialog
from PySide2.QtCore import Qt, QThread, Signal
import socket


class ChatClient(QThread):
    message_received = Signal(bytes)

    def __init__(self):
        super().__init__()
        self.socket = None

    def start_connection(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.start()

    def run(self):
        while True:
            data = self.socket.recv(1024)
            if not data:
                break
            self.message_received.emit(data)

    def send_message(self, message):
        self.socket.sendall(message.encode('utf-8'))

    def send_docx(self, path):
        with open(path, 'rb') as f:
            self.socket.sendall(f.read())

    def receive_docx(self, path):
        with open('received.docx', 'wb') as f:
            remaining_size = file_size
            while remaining_size > 0:
                chunk_size = min(remaining_size, 1024)
                chunk = client_socket.recv(chunk_size)
                f.write(chunk)
                remaining_size -= chunk_size


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Client - 2')

        self.message_box = QTextEdit()
        self.message_box.setReadOnly(True)

        self.message_input = QLineEdit()

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_message)

        self.send_docx_button = QPushButton('Send Docx')
        self.send_docx_button.clicked.connect(self.send_docx)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.send_docx_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.message_box)
        main_layout.addLayout(input_layout)

        self.setLayout(main_layout)

    def send_message(self):
        message = self.message_input.text()
        self.message_input.clear()
        self.message_box.append(f"> {message}")
        self.client.send_message(message)

    def receive_message(self, data):
        message = data.decode('utf-8', errors='replace')
        self.message_box.append(f"< {message}")

    def send_docx(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Word Documents (*.docx)")
        if path:
            self.client.send_docx(path)
            self.message_box.append(f"> Sent document: {path}")

    def set_client(self, client):
        self.client = client

    def receive_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Word Documents (*.docx)")
        if path:
            self.client.receive_docx(path)
            self.message_box.append(f"> Received document: {path}")



if __name__ == '__main__':
    app = QApplication([])
    window = ChatWindow()

    # Create client and connect to server
    client = ChatClient()
    client.start_connection('localhost', 9999)
    window.set_client(client)
    client.message_received.connect(window.receive_message)

    window.show()
    app.exec_()