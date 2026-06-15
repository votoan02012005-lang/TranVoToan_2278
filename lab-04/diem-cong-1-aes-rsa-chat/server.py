import socket, threading, struct
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad, unpad

HOST, PORT = '127.0.0.1', 9009

rsa_key = RSA.generate(2048)
rsa_pub = rsa_key.publickey()
rsa_decryptor = PKCS1_OAEP.new(rsa_key)

clients = {}          # conn -> {'aes': bytes, 'name': str}
lock = threading.Lock()

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

def broadcast(message, sender_conn):
    with lock:
        for conn, info in list(clients.items()):
            if conn is sender_conn:
                continue
            try:
                send_frame(conn, aes_encrypt(info['aes'], message.encode('utf-8')))
            except Exception:
                pass

def handle_client(conn, addr):
    try:
        send_frame(conn, rsa_pub.export_key())                  # 1. gửi RSA public key
        aes_key = rsa_decryptor.decrypt(recv_frame(conn))        # 2. nhận AES key (đã mã RSA)
        name = aes_decrypt(aes_key, recv_frame(conn)).decode()   # 3. nhận tên (mã AES)
        with lock:
            clients[conn] = {'aes': aes_key, 'name': name}
        print(f"[+] {name} {addr} đã tham gia.")
        broadcast(f"*** {name} đã tham gia phòng chat ***", conn)
        while True:                                              # 4. vòng lặp nhận tin
            data = recv_frame(conn)
            if data is None:
                break
            msg = aes_decrypt(aes_key, data).decode()
            print(f"{name}: {msg}")
            broadcast(f"{name}: {msg}", conn)
    except Exception as e:
        print("Lỗi:", e)
    finally:
        with lock:
            info = clients.pop(conn, None)
        conn.close()
        if info:
            broadcast(f"*** {info['name']} đã rời phòng chat ***", conn)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVER] AES-RSA chat chạy tại {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()