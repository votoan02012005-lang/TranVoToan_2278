import random

# Tham số công khai p (số nguyên tố lớn) và g (generator) - chuẩn 1024-bit MODP
p = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381"
    "FFFFFFFFFFFFFFFF", 16)
g = 2

def gen_private_key():
    return random.randint(2, p - 2)

def gen_public_key(private_key):
    return pow(g, private_key, p)

def gen_shared_secret(their_public, my_private):
    return pow(their_public, my_private, p)

if __name__ == "__main__":
    # Alice tạo cặp khoá
    a_priv = gen_private_key()
    a_pub = gen_public_key(a_priv)

    # Bob tạo cặp khoá
    b_priv = gen_private_key()
    b_pub = gen_public_key(b_priv)

    # Hai bên trao đổi public key rồi tự tính khoá bí mật chung
    alice_shared = gen_shared_secret(b_pub, a_priv)
    bob_shared = gen_shared_secret(a_pub, b_priv)

    print("Alice public key:", hex(a_pub)[:40], "...")
    print("Bob   public key:", hex(b_pub)[:40], "...")
    print("Khoá chung (Alice):", hex(alice_shared)[:40], "...")
    print("Khoá chung (Bob)  :", hex(bob_shared)[:40], "...")
    print("Hai khoá chung khớp nhau?", alice_shared == bob_shared)