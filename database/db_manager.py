import hashlib
import json
import os
import sqlite3
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path='database/app.db', credentials_path='database/credentials.json'):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.credentials_path = credentials_path
        self.credentials = self.load_credentials_file()

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                last_login TEXT
            );
            '''
        )
        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );
            '''
        )
        self.conn.commit()

    def load_credentials_file(self):
        os.makedirs(os.path.dirname(self.credentials_path), exist_ok=True)
        if not os.path.exists(self.credentials_path):
            return {}
        try:
            with open(self.credentials_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def save_credentials_file(self):
        os.makedirs(os.path.dirname(self.credentials_path), exist_ok=True)
        with open(self.credentials_path, 'w', encoding='utf-8') as f:
            json.dump(self.credentials, f, indent=2)

    @staticmethod
    def hash_password(password, salt=None):
        if salt is None:
            salt = os.urandom(16).hex()
        password_bytes = (password + salt).encode('utf-8')
        password_hash = hashlib.sha256(password_bytes).hexdigest()
        return salt, password_hash

    def register_user(self, username, password, role='user'):
        if username in self.credentials or self.get_user(username) is not None:
            return False, 'Username already exists.'

        salt, password_hash = self.hash_password(password)
        self.cursor.execute(
            'INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)',
            (username, password_hash, salt, role),
        )
        self.conn.commit()

        self.credentials[username] = {
            'password_hash': password_hash,
            'salt': salt,
            'role': role,
            'last_login': None,
        }
        self.save_credentials_file()

        self.log_action(username, 'register')
        return True, 'Registration successful.'

    def authenticate_user(self, username, password):
        user = self.get_user(username)
        if user is None:
            return False, None, 'User not found. Please register first.'

        salt = user['salt']
        _, password_hash = self.hash_password(password, salt)
        if password_hash != user['password_hash']:
            return False, None, 'Incorrect password.'

        self.update_last_login(username)
        self.log_action(username, 'login')
        return True, user['role'], 'Login successful.'

    def get_user(self, username):
        self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = self.cursor.fetchone()
        if row is not None:
            return row

        credential = self.credentials.get(username)
        if credential is None:
            return None

        return {
            'username': username,
            'password_hash': credential['password_hash'],
            'salt': credential['salt'],
            'role': credential.get('role', 'user'),
            'last_login': credential.get('last_login'),
        }
        self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return self.cursor.fetchone()

    def update_last_login(self, username):
        now = datetime.now().isoformat(timespec='seconds')
        self.cursor.execute('UPDATE users SET last_login = ? WHERE username = ?', (now, username))
        self.conn.commit()
        if username in self.credentials:
            self.credentials[username]['last_login'] = now
            self.save_credentials_file()

    def log_action(self, username, action):
        timestamp = datetime.now().isoformat(timespec='seconds')
        self.cursor.execute(
            'INSERT INTO logs (username, action, timestamp) VALUES (?, ?, ?)',
            (username, action, timestamp),
        )
        self.conn.commit()

    def get_logs(self, limit=100):
        self.cursor.execute('SELECT username, action, timestamp FROM logs ORDER BY id DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
