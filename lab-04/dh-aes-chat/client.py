import sys, socket, struct, threading, random, hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QLineEdit, QPushButton, QLabel, QInputDialog)
from PyQt5.QtCore import pyqtSignal, QObject

HOST, PORT = '127.0.0.1', 9010

p = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381"
    "FFFFFFFFFFFFFFFF", 16)
g = 2

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

def derive_key(shared):
    b = shared.to_bytes((shared.bit_length() + 7) // 8, 'big')
    return hashlib.sha256(b).digest()[:16]

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
        self.setWindowTitle(f"DH-AES Secure Chat - {self.name}")
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
        server_pub = int(recv_frame(self.sock).decode())          # 1. DH
        priv = random.randint(2, p - 2)
        my_pub = pow(g, priv, p)
        send_frame(self.sock, str(my_pub).encode())
        self.aes_key = derive_key(pow(server_pub, priv, p))        # khoá AES chung
        send_frame(self.sock, aes_encrypt(self.aes_key, self.name.encode()))
        threading.Thread(target=self.listen, daemon=True).start()
        self.show_message("*** Đã kết nối an toàn (Diffie-Hellman + AES) ***")

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