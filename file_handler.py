import os
import io
import base64

import pandas as pd

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_key_from_password(password, salt=b''):
    """_summary_

    Args:
        password (string): Password for generated base64encode
        salt (bytes, optional): _description_. Defaults to b''.

    Returns:
        _type_: base64encode generated from password
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key)

def encrypt_file_with_password(password, input_file, output_file):
    """

    Args:
        password (string): Chosen password to lock file
        input_file (string): Path to input file
        output_file (string): Path to output file
    """
    salt = os.urandom(16)
    key = generate_key_from_password(password, salt)

    with open(input_file, 'rb') as f:
        data = f.read()

    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data)

    with open(output_file, 'wb') as f:
        f.write(salt + encrypted_data)

def decrypt_file_with_password(password, input_file):
    """_summary_

    Args:
        password (string): Password to attempt unlock
        input_file (string): Path to locked file

    Returns:
        DataFrame: A populated dataframe upon successful unlock; empty dataframe if unsuccessful
    """
    with open(input_file, 'rb') as f:
        salt = f.read(16)
        encrypted_data = f.read()

    key = generate_key_from_password(password, salt)
    cipher = Fernet(key)

    try:
        decrypted_data = cipher.decrypt(encrypted_data)
        file_like = io.BytesIO(decrypted_data)
        df = pd.read_csv(file_like)
    except InvalidToken:
        df = pd.DataFrame()
    return df
