import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import unpad

HOST, PORT = '127.0.0.1', 65432

# 1. Tạo cặp khoá RSA
key = RSA.generate(2048)
private_key = key
public_key = key.publickey()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f"[SERVER] Đang lắng nghe tại {HOST}:{PORT} ...")

conn, addr = server.accept()
print(f"[SERVER] Client kết nối: {addr}")

# 2. Gửi RSA public key cho client
conn.sendall(public_key.export_key())

# 3. Nhận AES key (đã mã hoá bằng RSA, dài đúng 256 byte với RSA-2048)
enc_aes_key = conn.recv(256)
aes_key = PKCS1_OAEP.new(private_key).decrypt(enc_aes_key)
print(f"[SERVER] AES key đã giải mã: {aes_key.hex()}")

# 4. Nhận iv + ciphertext, giải mã bằng AES
data = conn.recv(4096)
iv, ciphertext = data[:16], data[16:]
plaintext = unpad(AES.new(aes_key, AES.MODE_CBC, iv).decrypt(ciphertext), AES.block_size)
print(f"[SERVER] Tin nhắn nhận được: {plaintext.decode()}")

conn.close()
server.close()