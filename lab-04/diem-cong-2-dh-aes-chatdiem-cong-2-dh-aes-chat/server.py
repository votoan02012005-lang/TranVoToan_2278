import socket, threading, struct, random, hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

HOST, PORT = '127.0.0.1', 9010

p = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381"
    "FFFFFFFFFFFFFFFF", 16)
g = 2

clients = {}
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

def derive_key(shared):
    b = shared.to_bytes((shared.bit_length() + 7) // 8, 'big')
    return hashlib.sha256(b).digest()[:16]

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
        priv = random.randint(2, p - 2)                       # 1. DH key exchange
        pub = pow(g, priv, p)
        send_frame(conn, str(pub).encode())                   # gửi public key server
        client_pub = int(recv_frame(conn).decode())           # nhận public key client
        aes_key = derive_key(pow(client_pub, priv, p))         # khoá AES từ shared secret
        name = aes_decrypt(aes_key, recv_frame(conn)).decode()
        with lock:
            clients[conn] = {'aes': aes_key, 'name': name}
        print(f"[+] {name} {addr} đã tham gia.")
        broadcast(f"*** {name} đã tham gia phòng chat ***", conn)
        while True:
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
    print(f"[SERVER] DH-AES chat chạy tại {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()