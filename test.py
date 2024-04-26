import hashlib


def check_virus(file_path):
    with open(file_path, 'rb') as file:
        file_bytes = file.read()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        print(file_hash)


if __name__ == '__main__':
    check_virus(".gitignore")
