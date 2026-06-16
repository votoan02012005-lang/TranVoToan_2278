import hashlib

def hash_text(text):
    data = text.encode('utf-8')
    print(f"Văn bản gốc: {text}")
    print(f"MD5    : {hashlib.md5(data).hexdigest()}")
    print(f"SHA-1  : {hashlib.sha1(data).hexdigest()}")
    print(f"SHA-256: {hashlib.sha256(data).hexdigest()}")
    print(f"SHA-512: {hashlib.sha512(data).hexdigest()}")

if __name__ == "__main__":
    text = input("Nhập chuỗi cần băm: ")
    print("-" * 40)
    hash_text(text)