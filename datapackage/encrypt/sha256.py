#   © 2021 정선우 <seonwoo0808@kakao.com>
#   datapackage\encrypt\sha256.py

import hashlib

def encrypt(string):
    string =hashlib.sha256(string.encode())
    string = string.hexdigest()
    return string
