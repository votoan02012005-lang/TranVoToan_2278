import sys, socket, struct, threading
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QLineEdit, QPushButton, QLabel, QInputDialog)
from PyQt5.QtCore import pyqtSignal, QObject

HOST, PORT = '127.0.0.1', 9009

def send_frame(sock, data):
    sock.sendall(struct.pack('>I', len(data)) + data)

def recv_all(sock, n):
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf

def recv_frame(sock):
    header = recv_all(sock, 4)
    if not header:
        return None
    (length,) = struct.unpack('>I', header)
    return recv_all(sock, length)

def aes_encrypt(key, plaintext):
    cipher = AES.new(key, AES.MODE_CBC)
    return cipher.iv + cipher.encrypt(pad(plaintext, AES.block_size))

def aes_decrypt(key, data):
    iv, ct = data[:16], data[16:]
    return unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ct), AES.block_size)

class Signaller(QObject):
    received = pyqtSignal(str)

class ChatClient(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.signaller = Signaller()
        self.signaller.received.connect(self.show_message)
        self.init_ui()
        self.connect_server()

    def init_ui(self):
        self.setWindowTitle(f"AES-RSA Secure Chat - {self.name}")
        self.resize(450, 500)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Đăng nhập: {self.name}"))
        self.chat_box = QTextEdit(); self.chat_box.setReadOnly(True)
        layout.addWidget(self.chat_box)
        row = QHBoxLayout()
        self.input = QLineEdit(); self.input.returnPressed.connect(self.send_message)
        btn = QPushButton("Gửi"); btn.clicked.connect(self.send_message)
        row.addWidget(self.input); row.addWidget(btn)
        layout.addLayout(row)
        self.setLayout(layout)

    def connect_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        server_pub = RSA.import_key(recv_frame(self.sock))                    # 1. nhận RSA pub
        self.aes_key = get_random_bytes(16)                                   # 2. tạo AES key
        send_frame(self.sock, PKCS1_OAEP.new(server_pub).encrypt(self.aes_key))
        send_frame(self.sock, aes_encrypt(self.aes_key, self.name.encode()))  # 3. gửi tên
        threading.Thread(target=self.listen, daemon=True).start()
        self.show_message("*** Đã kết nối an toàn (AES-RSA) ***")

    def listen(self):
        while True:
            try:
                data = recv_frame(self.sock)
                if data is None:
                    break
                self.signaller.received.emit(aes_decrypt(self.aes_key, data).decode())
            except Exception:
                break

    def send_message(self):
        text = self.input.text().strip()
        if not text:
            return
        try:
            send_frame(self.sock, aes_encrypt(self.aes_key, text.encode()))
            self.show_message(f"Tôi: {text}")
            self.input.clear()
        except Exception as e:
            self.show_message(f"[Lỗi gửi: {e}]")

    def show_message(self, msg):
        self.chat_box.append(msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    name, ok = QInputDialog.getText(None, "Tên", "Nhập tên hiển thị:")
    if not ok or not name.strip():
        name = "User"
    win = ChatClient(name.strip())
    win.show()
    sys.exit(app.exec_())