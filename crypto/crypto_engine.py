import base64
from cryptography.exceptions import InvalidSignature
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class CryptoEngine:
    @staticmethod
    def generate_keys(bits=2048):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=bits)
        public_key = private_key.public_key()

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode('utf-8')

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode('utf-8')

        return public_pem, private_pem

    @staticmethod
    def save_key_to_file(key_text, path):
        with open(path, 'w', encoding='utf-8') as key_file:
            key_file.write(key_text)

    @staticmethod
    def load_public_key(pem_text):
        return serialization.load_pem_public_key(pem_text.encode('utf-8'))

    @staticmethod
    def load_private_key(pem_text):
        return serialization.load_pem_private_key(pem_text.encode('utf-8'), password=None)

    @staticmethod
    def validate_key_pair(public_text, private_text):
        if not public_text.strip() or not private_text.strip():
            return False, 'Both public and private keys are required.'

        try:
            public_key = CryptoEngine.load_public_key(public_text)
            private_key = CryptoEngine.load_private_key(private_text)

            public_numbers = public_key.public_numbers()
            private_numbers = private_key.private_numbers().public_numbers
            if public_numbers != private_numbers:
                return False, 'Invalid Keys'

            test_bytes = b'key validation'
            signature = private_key.sign(
                test_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            public_key.verify(
                signature,
                test_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True, (public_key, private_key)
        except (InvalidSignature, ValueError, TypeError):
            return False, 'Invalid Keys'
        except Exception:
            return False, 'Invalid Keys'

    @staticmethod
    def hybrid_encrypt(data_bytes, public_text, private_text):
        valid, result = CryptoEngine.validate_key_pair(public_text, private_text)
        if not valid:
            raise ValueError(result)

        public_key, _ = result
        symmetric_key = Fernet.generate_key()
        cipher = Fernet(symmetric_key)
        encrypted_data = cipher.encrypt(data_bytes)
        encrypted_key = public_key.encrypt(
            symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        header = len(encrypted_key).to_bytes(4, byteorder='big')
        return header + encrypted_key + encrypted_data

    @staticmethod
    def hybrid_decrypt(payload_bytes, public_text, private_text):
        valid, result = CryptoEngine.validate_key_pair(public_text, private_text)
        if not valid:
            raise ValueError(result)

        _, private_key = result
        if len(payload_bytes) < 5:
            raise ValueError('Invalid encrypted file format.')

        key_length = int.from_bytes(payload_bytes[:4], byteorder='big')
        encrypted_key = payload_bytes[4:4 + key_length]
        encrypted_data = payload_bytes[4 + key_length:]

        symmetric_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        cipher = Fernet(symmetric_key)
        decrypted_data = cipher.decrypt(encrypted_data)
        return decrypted_data

    @staticmethod
    def create_cipher_preview(payload_bytes, max_chars=2048):
        encoded = base64.b64encode(payload_bytes).decode('utf-8')
        return encoded[:max_chars] + ('...' if len(encoded) > max_chars else '')
