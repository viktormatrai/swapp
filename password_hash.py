import hashlib


def hash_pw(password):
    hash_object = hashlib.md5(password.encode())
    hashed_pw = hash_object.hexdigest()
    return hashed_password
