import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

HOST, PORT = '127.0.0.1', 65432

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# 1. Nhận RSA public key
public_key = RSA.import_key(client.recv(4096))

# 2. Tạo AES key ngẫu nhiên (16 byte)
aes_key = get_random_bytes(16)

# 3. Mã hoá AES key bằng RSA rồi gửi
enc_aes_key = PKCS1_OAEP.new(public_key).encrypt(aes_key)
client.sendall(enc_aes_key)

# 4. Mã hoá tin nhắn bằng AES (CBC) rồi gửi iv + ciphertext
message = input("Nhập tin nhắn cần gửi: ").encode()
cipher = AES.new(aes_key, AES.MODE_CBC)
ciphertext = cipher.encrypt(pad(message, AES.block_size))
client.sendall(cipher.iv + ciphertext)
print("[CLIENT] Đã gửi tin nhắn mã hoá.")

client.close()