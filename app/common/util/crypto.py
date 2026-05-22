# -*- coding: utf-8 -*-

import base64
import hashlib
import os


class AESCipher:
    """AES 加解密工具 (使用 CBC 模式)

    依赖: pip install pycryptodome
    如果不需要 AES 功能，可以只使用下面的 hash/base64 工具函数
    """

    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, plaintext):
        """AES-256-CBC 加密"""
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad
        except ImportError:
            raise ImportError("请安装 pycryptodome: pip install pycryptodome")

        iv = os.urandom(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(iv + encrypted).decode('utf-8')

    def decrypt(self, ciphertext):
        """AES-256-CBC 解密"""
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import unpad
        except ImportError:
            raise ImportError("请安装 pycryptodome: pip install pycryptodome")

        raw = base64.b64decode(ciphertext)
        iv = raw[:16]
        encrypted = raw[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
        return decrypted.decode('utf-8')


def md5(text):
    """MD5 哈希"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def sha256(text):
    """SHA256 哈希"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def base64_encode(text):
    """Base64 编码"""
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')


def base64_decode(text):
    """Base64 解码"""
    return base64.b64decode(text.encode('utf-8')).decode('utf-8')


def generate_random_string(length=32):
    """生成随机字符串 (用于 token、验证码等)"""
    return os.urandom(length).hex()[:length]
