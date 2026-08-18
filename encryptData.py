from pathlib import Path
from cryptography.fernet import Fernet
import rsa


def Encryption(message):
    # open the symmetric key file
    with open('messageKey.key', 'rb') as skey:
        key = skey.read()

    # create the cipher
    cipher = Fernet(key)

    # encrypt the data
    encrypted_data = cipher.encrypt(message.encode('utf-8'))
    with open('EncryptedFile', 'wb') as edata:
        edata.write(encrypted_data)

    # open the public key file
    with open('publicKey.key', 'rb') as pkey:
        pkdata = pkey.read()

    # load the file
    pubkey = rsa.PublicKey.load_pkcs1(pkdata)

    # encrypt the symmetric key file with the public key
    encrypted_key = rsa.encrypt(key, pubkey)

    with open('encryptedMessageKey', 'wb') as ekey:
        ekey.write(encrypted_key)


def EncryptionFile(input_path, output_path=None):
    with open('messageKey.key', 'rb') as skey:
        key = skey.read()

    cipher = Fernet(key)

    with open(input_path, 'rb') as infile:
        data = infile.read()

    encrypted_data = cipher.encrypt(data)
    input_path = Path(input_path)
    if output_path is None:
        output_path = str(input_path.with_suffix(input_path.suffix + '.enc'))

    with open(output_path, 'wb') as outfile:
        outfile.write(encrypted_data)

    with open('publicKey.key', 'rb') as pkey:
        pkdata = pkey.read()
    pubkey = rsa.PublicKey.load_pkcs1(pkdata)
    encrypted_key = rsa.encrypt(key, pubkey)

    with open('encryptedMessageKey', 'wb') as ekey:
        ekey.write(encrypted_key)

    return output_path
