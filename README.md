# 🛡️ PyCrypto-EndToEnd - Hybrid RSA & Fernet Encryption Suite

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Cryptography](https://img.shields.io/badge/cryptography-Fernet%20%7C%20RSA-green.svg)](https://cryptography.io/)
[![Database](https://img.shields.io/badge/database-SQLite-lightblue.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

An end-to-end **Hybrid Cryptography Application** written in Python. This tool combines **Symmetric AES Encryption (Fernet)** for fast data encryption with **Asymmetric Encryption (RSA 2048-bit)** to securely encrypt and exchange keys. It features a desktop user interface with **user authentication & role-based dashboard control**, as well as modular CLI scripts for automated file encryption.

---

## 🏷️ Suggested Project Names for Rename / Rewrite

If you are looking to rename or refactor this sub-project, here are top recommended names:

| Suggested Name | Theme / Vibe | Description |
| :--- | :--- | :--- |
| 🛡️ **PyCrypto-EndToEnd** *(Recommended)* | Direct & Professional | Highlights complete end-to-end hybrid RSA + Fernet encryption workflow. |
| 🔐 **HybridVault-CLI** | Security & Vault | Emphasizes secure local file vaults with hybrid symmetric/asymmetric keys. |
| 🔑 **PyRSA-Fernet** | Technical & Precise | Explicitly names the two core underlying crypto engines (RSA & Fernet). |
| ⚡ **CryptaVault-Auth** | Desktop & Auth-based | Highlights local user login authentication paired with data protection. |
| 🧠 **EndToEnd-Crypto-Core** | Modular Engine | Ideal name if using this folder as a backend crypto engine library. |

---

## 📍 Where to Use This Application

1. **Secure End-to-End File Transport**:
   - Encrypting large files locally using **Fernet (AES 128-bit CBC)** without file size performance lag.
   - Encrypting the symmetric Fernet key with **RSA 2048-bit Public Key** so only the intended recipient holding the Private Key can unlock it.

2. **Role-Based Desktop Security Systems**:
   - Local user authentication backed by an **SQLite database (`users.db`)**.
   - Dashboard interface separating user roles for credential and file management.

3. **Automated Cryptography Pipelines**:
   - Using standalone Python scripts (`createKeys.py`, `encryptData.py`, `decryptData.py`) in CI/CD or automated file transfer tasks.

---

## 📦 Which Things to Install (Prerequisites & Dependencies)

Make sure you have the following prerequisites installed:

### 1. Prerequisites
* **Python 3.8+**: Runtime environment.
* **Tkinter (`python3-tk`)**: Required for the Desktop GUI dashboard (`main.py`).

### 2. Python Packages (`requirements.txt`)
* **`cryptography`**: Implements `Fernet` symmetric key generation and AES encryption.
* **`rsa`**: Implements 2048-bit PKCS#1 RSA key pair generation, key loading, and key wrapping.

---

## ⚙️ How to Install (Step-by-Step)

### Method 1: Automated Installation Script
Run the included bash setup script:
```bash
chmod +x install.sh
./install.sh
```

---

### Method 2: Manual Installation

#### 🐧 On Linux (Ubuntu / Kali / Debian):
```bash
# Update and install system requirements
sudo apt update
sudo apt install -y python3 python3-pip python3-tk

# Install Python packages
pip3 install cryptography rsa
```

#### 🪟 On Windows:
1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/) (ensure **"Add Python to PATH"** and **tcl/tk** are checked).
2. Open Command Prompt (`cmd`) in this folder and run:
   ```cmd
   pip install cryptography rsa
   ```

#### 🍎 On macOS:
```bash
brew install python python-tk
pip3 install cryptography rsa
```

---

## 🚀 How to Use

### 1. Running the Full Desktop GUI Application
To launch the user authentication portal & encrypted dashboard:

```bash
python main.py
```
* **Step 1**: Log in using your user credentials (stored in local `users.db`).
* **Step 2**: Access the dashboard to generate keys, encrypt messages, or decrypt incoming encrypted payloads.

---

### 2. Using Standalone CLI Scripts

You can also run individual cryptographic modular scripts directly:

#### A. Generate RSA & Fernet Keys:
```bash
python createKeys.py
```
*Outputs*:
* `messageKey.key` (Symmetric Fernet Key)
* `publicKey.key` (RSA Public Key PEM)
* `privateKey.key` (RSA Private Key PEM)

#### B. Encrypt Text or Files:
```bash
python encryptData.py
```
* Encrypts plain text data into `EncryptedFile`.
* Wraps the symmetric key into `encryptedMessageKey` using the Public Key.

#### C. Decrypt Text or Files:
```bash
python decryptData.py
```
* Uses `privateKey.key` to unwrap `encryptedMessageKey`.
* Uses the unwrapped symmetric key to decrypt `EncryptedFile` back into readable content.

---

## 🔐 How Hybrid Encryption Works (Architecture)

```
                       [ Plaintext Message / File ]
                                    │
                                    ▼ (Fernet Symmetric AES)
 [ Symmetric Key (messageKey.key) ] ───► [ EncryptedFile ]
           │
           ▼ (RSA 2048 Public Key)
 [ encryptedMessageKey ]
```

1. **Data Confidentiality**: Data is encrypted using **Fernet (AES-128)**, which is extremely fast and capable of handling large files.
2. **Key Security**: The Fernet key itself is encrypted using **RSA 2048-bit Public Key**.
3. **Decryption Guarantee**: Only someone possessing the corresponding **RSA 2048-bit Private Key** can decrypt `encryptedMessageKey` to retrieve the Fernet key and unlock the file.

---

## 📁 Sub-Project File Structure

```
Python-Asymmetric-Encryption-End-to-End-main/
├── main.py                # 🏠 Desktop Application Entry Point (Auth & Dashboard)
├── App.py                 # 🚀 Alternative App Launcher
├── createKeys.py          # 🔑 Key Generation Script (RSA + Fernet)
├── encryptData.py         # 🔒 Data & File Encryption Script
├── decryptData.py         # 🔓 Data & File Decryption Script
├── install.sh             # 🔧 Environment Installer Script
├── requirements.txt       # 📦 Python Dependencies
├── README.md              # 📚 Documentation Guide
├── ui/                    # 🎨 Tkinter GUI View Modules (Login & Dashboard)
├── crypto/                # 🔐 Cryptographic Utilities & Helper Modules
├── database/              # 🗄️ SQLite Database Manager (`db_manager.py`)
├── users.db               # 💾 SQLite Local User Database
└── assets/                # 🖼️ Application Icons & Graphical Assets
```

---

## 📜 License
MIT License. Created for educational and cybersecurity training purposes.
