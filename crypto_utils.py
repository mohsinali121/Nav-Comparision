import base64
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os


def get_key_iv():
    key = base64.b64decode(os.getenv("DECRYPT_KEY"))
    iv = os.getenv("DECRYPT_NO").encode("utf-8")[:16]
    return key, iv


def decrypt_data(pass_data: str):
    key, iv = get_key_iv()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_bytes = (
        decryptor.update(base64.b64decode(pass_data)) + decryptor.finalize()
    )

    # Remove padding manually (PKCS7 Padding)
    pad_length = decrypted_bytes[-1]  # Last byte gives the padding length
    original_data = decrypted_bytes[:-pad_length].decode("utf-8")

    # Debugging: Print decrypted output
    print(f"Decrypted Output Before JSON Parsing: {original_data}")

    # Remove custom `}*#$*` suffix if present
    if original_data.endswith("}*#$*"):
        original_data = original_data[:-4]
    print("reaching here and returning ", json.loads(original_data))
    return json.loads(original_data)  # Convert to JSON


def encrypt_data(pass_data):
    key, iv = get_key_iv()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    if isinstance(pass_data, str):
        input_data = pass_data
    else:
        input_data = json.dumps(pass_data)

    # Padding for AES block size (16 bytes)
    pad_length = 16 - (len(input_data) % 16)
    input_data += chr(pad_length) * pad_length

    encrypted_bytes = (
        encryptor.update(input_data.encode("utf-8")) + encryptor.finalize()
    )
    return base64.b64encode(encrypted_bytes).decode("utf-8")
