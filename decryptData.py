from pathlib import Path
import rsa
from cryptography.fernet import Fernet


def Decryption():
    # load the private key to decrypt the encrypted symmetric key
    with open('privateKey.key', 'rb') as prkey:
        pkey = prkey.read()
        private_key = rsa.PrivateKey.load_pkcs1(pkey)

    with open('encryptedMessageKey', 'rb') as e:
        ekey = e.read()

    dpubkey = rsa.decrypt(ekey, private_key)
    cipher = Fernet(dpubkey)

    with open('EncryptedFile', 'rb') as encrypted_data:
        edata = encrypted_data.read()

    decrypted_data = cipher.decrypt(edata)
    return decrypted_data.decode('utf-8')


def DecryptionFile(input_path, output_path=None):
    with open('privateKey.key', 'rb') as prkey:
        pkey = prkey.read()
        private_key = rsa.PrivateKey.load_pkcs1(pkey)

    with open('encryptedMessageKey', 'rb') as e:
        ekey = e.read()

    dpubkey = rsa.decrypt(ekey, private_key)
    cipher = Fernet(dpubkey)

    with open(input_path, 'rb') as infile:
        encrypted_data = infile.read()

    decrypted_data = cipher.decrypt(encrypted_data)

    input_path = Path(input_path)
    if output_path is None:
        output_path = str(input_path.with_suffix('.dec'))

    with open(output_path, 'wb') as outfile:
        outfile.write(decrypted_data)

    return output_path
