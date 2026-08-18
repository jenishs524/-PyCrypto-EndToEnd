import datetime
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from crypto.crypto_engine import CryptoEngine


class DashboardView(ttk.Frame):
    def __init__(self, parent, db_manager, username, role, logout_callback):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = db_manager
        self.username = username
        self.role = role
        self.logout_callback = logout_callback

        self.input_mode = tk.StringVar(value='file')
        self.input_file_path = tk.StringVar()
        self.encrypted_file_path = tk.StringVar()
        self.status_text = tk.StringVar(value='Ready')
        self.progress_value = tk.IntVar(value=0)

        self.public_key_text = ''
        self.private_key_text = ''
        self.public_key_source = ''  # 'manual' or 'auto-generated'
        self.private_key_source = ''  # 'manual' or 'auto-generated'
        self.last_decrypted_data = None
        self.last_decrypted_filename = 'decrypted_output.txt'

        self.build_ui()
        self.db_manager.log_action(self.username, 'dashboard_open')

    def build_ui(self):
        header_frame = ttk.Frame(self, padding=14)
        header_frame.pack(fill=tk.X)

        welcome_label = ttk.Label(
            header_frame,
            text=f'Welcome, {self.username} ({self.role})',
            style='Header.TLabel',
        )
        welcome_label.pack(side=tk.LEFT)

        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)

        ttk.Button(button_frame, text='Generate Keys', command=self.generate_keys, style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(button_frame, text='Logout', command=self.logout, width=12).pack(side=tk.LEFT)

        self.build_workflow_panel()
        self.build_content_panels()
        self.build_log_panel()
        self.build_status_bar()

    def build_workflow_panel(self):
        workflow = ttk.LabelFrame(self, text='Asymmetric Encryption Workflow', padding=12)
        workflow.pack(fill=tk.X, padx=14, pady=(0, 12))

        steps = [
            ('🖥️ Sender', 'Originator of plaintext data'),
            ('📄 Plaintext data', 'Original message before encryption'),
            ('🔐 Ciphered Data', 'Encrypted content using public/private keys'),
            ('�️ Provide Keys', 'Load public and private keys for decryption'),
            ('🔓 Recovered Data', 'Recovered original data before recipient'),
            ('🗄️ Recipient', 'Final recipient of decrypted message'),
        ]

        step_frame = tk.Frame(workflow, bg='#181a1f')
        step_frame.pack(fill=tk.X)

        for index, (title, subtitle) in enumerate(steps):
            box = tk.Frame(step_frame, bg='#242933', bd=1, relief=tk.SOLID)
            box.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4, pady=4)
            tk.Label(box, text=title, bg='#242933', fg='#e6e6e6', font=('Segoe UI', 10, 'bold')).pack(pady=(10, 4))
            tk.Label(box, text=subtitle, bg='#242933', fg='#abb2bf', font=('Segoe UI', 9), wraplength=120, justify=tk.CENTER).pack(pady=(0, 10))
            if index < len(steps) - 1:
                arrow = tk.Label(step_frame, text='→', bg='#181a1f', fg='#61afef', font=('Segoe UI', 18, 'bold'))
                arrow.pack(side=tk.LEFT, padx=2)

    def build_content_panels(self):
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=14)

        left_panel = ttk.Frame(container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), pady=(0, 8))

        middle_panel = ttk.Frame(container)
        middle_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        right_panel = ttk.Frame(container)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=(0, 8))

        self.build_input_panel(left_panel)
        self.build_cipher_panel(middle_panel)
        self.build_output_panel(right_panel)

    def build_input_panel(self, parent):
        input_card = ttk.LabelFrame(parent, text='Input Source', padding=12)
        input_card.pack(fill=tk.BOTH, expand=True)

        mode_frame = ttk.Frame(input_card)
        mode_frame.pack(fill=tk.X)
        ttk.Radiobutton(mode_frame, text='File Input', variable=self.input_mode, value='file', command=self.update_input_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text='Text Input', variable=self.input_mode, value='text', command=self.update_input_mode).pack(side=tk.LEFT, padx=12)

        self.file_frame = ttk.Frame(input_card)
        self.file_frame.pack(fill=tk.X, pady=(12, 0))
        ttk.Label(self.file_frame, text='Select file:', style='Section.TLabel').grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(self.file_frame, textvariable=self.input_file_path, width=32).grid(row=0, column=1, padx=8)
        ttk.Button(self.file_frame, text='Browse', command=self.browse_input_file).grid(row=0, column=2)

        self.text_frame = ttk.Frame(input_card)
        self.text_frame.pack(fill=tk.BOTH, expand=True, pady=(14, 0))
        ttk.Label(self.text_frame, text='Plain message:', style='Section.TLabel').pack(anchor=tk.W)
        self.message_text = scrolledtext.ScrolledText(self.text_frame, height=7, background='#242933', foreground='#e6e6e6')
        self.message_text.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        self.build_key_panel(input_card)
        self.update_input_mode()

    def build_key_panel(self, parent):
        key_frame = ttk.LabelFrame(parent, text='Public / Private Keys', padding=12)
        key_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        # Public Key Section
        ttk.Label(key_frame, text='Public Key', style='Section.TLabel').pack(anchor=tk.W)
        self.public_key_label = ttk.Label(key_frame, text='', foreground='#abb2bf', font=('Segoe UI', 8))
        self.public_key_label.pack(anchor=tk.W)
        self.public_key_text_widget = scrolledtext.ScrolledText(key_frame, height=6, background='#242933', foreground='#e6e6e6')
        self.public_key_text_widget.pack(fill=tk.BOTH, expand=True, pady=(6, 8))
        self.public_key_text_widget.bind('<<Change>>', self.on_public_key_change)
        self.public_key_text_widget.bind('<KeyRelease>', self.on_public_key_change)

        button_frame1 = ttk.Frame(key_frame)
        button_frame1.pack(side=tk.LEFT, pady=(0, 12))
        ttk.Button(button_frame1, text='Load Public Key', command=self.load_public_key).pack(side=tk.LEFT)
        ttk.Button(button_frame1, text='Copy', command=self.copy_public_key).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(button_frame1, text='Save', command=self.save_public_key).pack(side=tk.LEFT, padx=(8, 0))

        # Private Key Section
        ttk.Label(key_frame, text='Private Key', style='Section.TLabel').pack(anchor=tk.W, pady=(12, 0))
        self.private_key_label = ttk.Label(key_frame, text='', foreground='#abb2bf', font=('Segoe UI', 8))
        self.private_key_label.pack(anchor=tk.W)
        self.private_key_text_widget = scrolledtext.ScrolledText(key_frame, height=6, background='#242933', foreground='#e6e6e6')
        self.private_key_text_widget.pack(fill=tk.BOTH, expand=True, pady=(6, 8))
        self.private_key_text_widget.bind('<<Change>>', self.on_private_key_change)
        self.private_key_text_widget.bind('<KeyRelease>', self.on_private_key_change)

        button_frame2 = ttk.Frame(key_frame)
        button_frame2.pack(side=tk.LEFT, pady=(0, 0))
        ttk.Button(button_frame2, text='Load Private Key', command=self.load_private_key).pack(side=tk.LEFT)
        ttk.Button(button_frame2, text='Copy', command=self.copy_private_key).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(button_frame2, text='Save', command=self.save_private_key).pack(side=tk.LEFT, padx=(8, 0))

    def build_cipher_panel(self, parent):
        cipher_card = ttk.LabelFrame(parent, text='Encryption Center', padding=12)
        cipher_card.pack(fill=tk.BOTH, expand=True)

        ttk.Label(cipher_card, text='🔒 Encryption / Cipher', style='Section.TLabel').pack(anchor=tk.W)
        ttk.Button(cipher_card, text='Encrypt', command=self.start_encrypt, style='Accent.TButton').pack(fill=tk.X, pady=(8, 10))

        ttk.Label(cipher_card, text='Cipher text preview', style='Section.TLabel').pack(anchor=tk.W)
        self.cipher_text = scrolledtext.ScrolledText(cipher_card, height=16, background='#242933', foreground='#e6e6e6')
        self.cipher_text.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

    def build_output_panel(self, parent):
        decrypt_card = ttk.LabelFrame(parent, text='Decryption Center', padding=12)
        decrypt_card.pack(fill=tk.BOTH, expand=True)

        ttk.Label(decrypt_card, text='Encrypted file (.enc)', style='Section.TLabel').pack(anchor=tk.W)
        file_frame = ttk.Frame(decrypt_card)
        file_frame.pack(fill=tk.X, pady=(8, 8))
        ttk.Entry(file_frame, textvariable=self.encrypted_file_path, width=34).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(file_frame, text='Browse', command=self.browse_encrypted_file).pack(side=tk.LEFT)

        ttk.Button(decrypt_card, text='Decrypt', command=self.start_decrypt, style='Accent.TButton').pack(fill=tk.X, pady=(0, 10))

        ttk.Label(decrypt_card, text='Decrypted output', style='Section.TLabel').pack(anchor=tk.W)
        self.decrypted_text = scrolledtext.ScrolledText(decrypt_card, height=16, background='#242933', foreground='#e6e6e6')
        self.decrypted_text.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        ttk.Button(decrypt_card, text='Save Decrypted Result', command=self.save_decrypted_output).pack(pady=(10, 0), anchor=tk.W)

    def build_log_panel(self):
        log_card = ttk.LabelFrame(self, text='Activity Log', padding=12)
        log_card.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 12))

        self.log_text = scrolledtext.ScrolledText(log_card, height=8, background='#242933', foreground='#e6e6e6')
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def build_status_bar(self):
        status_card = ttk.Frame(self, padding=12)
        status_card.pack(fill=tk.X, padx=14, pady=(0, 14))

        ttk.Label(status_card, text='Status:', style='Section.TLabel').pack(side=tk.LEFT)
        ttk.Label(status_card, textvariable=self.status_text, foreground='#98c379').pack(side=tk.LEFT, padx=(8, 0))

        self.progress = ttk.Progressbar(status_card, variable=self.progress_value, maximum=100, length=360)
        self.progress.pack(side=tk.RIGHT)

    def update_input_mode(self):
        if self.input_mode.get() == 'file':
            self.text_frame.forget()
            self.file_frame.pack(fill=tk.X, pady=(12, 0))
        else:
            self.file_frame.forget()
            self.text_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

    def browse_input_file(self):
        filename = filedialog.askopenfilename(title='Select input file')
        if filename:
            self.input_file_path.set(filename)
            self.log('Selected input file: ' + os.path.basename(filename))

    def browse_encrypted_file(self):
        filename = filedialog.askopenfilename(title='Select encrypted file', filetypes=[('Encrypted files', '*.enc'), ('All files', '*.*')])
        if filename:
            self.encrypted_file_path.set(filename)
            self.log('Selected encrypted file: ' + os.path.basename(filename))

    def load_public_key(self):
        filename = filedialog.askopenfilename(title='Load public key', filetypes=[('PEM files', '*.pem *.key'), ('All files', '*.*')])
        if filename:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as key_file:
                self.public_key_text = key_file.read()
            self.public_key_text_widget.delete('1.0', tk.END)
            self.public_key_text_widget.insert(tk.END, self.public_key_text)
            self.public_key_source = 'manual'
            self.update_key_labels()
            self.log('Loaded public key from: ' + os.path.basename(filename))

    def load_private_key(self):
        filename = filedialog.askopenfilename(title='Load private key', filetypes=[('PEM files', '*.pem *.key'), ('All files', '*.*')])
        if filename:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as key_file:
                self.private_key_text = key_file.read()
            self.private_key_text_widget.delete('1.0', tk.END)
            self.private_key_text_widget.insert(tk.END, self.private_key_text)
            self.private_key_source = 'manual'
            self.auto_generate_public_from_private()
            self.log('Loaded private key from: ' + os.path.basename(filename))

    def copy_public_key(self):
        public_key_text = self.public_key_text_widget.get('1.0', tk.END).strip()
        self.copy_to_clipboard(public_key_text)
        self.log('Copied public key to clipboard')

    def copy_private_key(self):
        private_key_text = self.private_key_text_widget.get('1.0', tk.END).strip()
        self.copy_to_clipboard(private_key_text)
        self.log('Copied private key to clipboard')

    def copy_to_clipboard(self, text):
        if not text:
            messagebox.showwarning('Empty content', 'Nothing available to copy.')
            return
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)

    def generate_keys(self):
        public_key, private_key = CryptoEngine.generate_keys()
        self.public_key_text = public_key
        self.private_key_text = private_key
        self.public_key_source = 'auto-generated'
        self.private_key_source = 'auto-generated'
        self.public_key_text_widget.delete('1.0', tk.END)
        self.public_key_text_widget.insert(tk.END, public_key)
        self.private_key_text_widget.delete('1.0', tk.END)
        self.private_key_text_widget.insert(tk.END, private_key)
        self.update_key_labels()
        self.log('Generated new RSA key pair')
        messagebox.showinfo('Keys Generated', 'A new RSA key pair has been generated and loaded.')

    def start_encrypt(self):
        self.status_text.set('Validating keys...')
        self.progress_value.set(5)
        self.public_key_text = self.public_key_text_widget.get('1.0', tk.END).strip()
        self.private_key_text = self.private_key_text_widget.get('1.0', tk.END).strip()

        if not self.public_key_text or not self.private_key_text:
            messagebox.showerror('Missing Keys', 'Both public and private keys are required for encryption.')
            self.status_text.set('Missing keys')
            return

        self.status_text.set('Validating key pair...')
        self.progress_value.set(15)
        valid, result = CryptoEngine.validate_key_pair(self.public_key_text, self.private_key_text)
        if not valid:
            messagebox.showerror('Invalid Keys', result)
            self.status_text.set('Invalid keys')
            self.log('Encryption blocked: invalid key pair')
            return

        if self.input_mode.get() == 'file':
            input_path = self.input_file_path.get().strip()
            if not input_path or not os.path.isfile(input_path):
                messagebox.showwarning('Select File', 'Please select a valid input file.')
                self.status_text.set('File required')
                return
            output_path = filedialog.asksaveasfilename(
                title='Save encrypted file',
                defaultextension='.enc',
                filetypes=[('Encrypted file', '*.enc')],
                initialfile=os.path.basename(input_path) + '.enc',
            )
            if not output_path:
                self.status_text.set('Encryption cancelled')
                return
            self.log('Encrypting file: ' + os.path.basename(input_path))
            self.encrypt_file(input_path, output_path)
        else:
            message = self.message_text.get('1.0', tk.END).strip()
            if not message:
                messagebox.showwarning('Enter Message', 'Please enter text to encrypt.')
                self.status_text.set('Text required')
                return
            output_path = filedialog.asksaveasfilename(
                title='Save encrypted file',
                defaultextension='.enc',
                filetypes=[('Encrypted file', '*.enc')],
                initialfile='message.enc',
            )
            if not output_path:
                self.status_text.set('Encryption cancelled')
                return
            self.log('Encrypting text message')
            self.encrypt_text(message.encode('utf-8'), output_path)

    def encrypt_text(self, data_bytes, output_path):
        self.status_text.set('Reading data...')
        self.progress_value.set(25)
        self.parent.update_idletasks()

        payload = CryptoEngine.hybrid_encrypt(data_bytes, self.public_key_text, self.private_key_text)

        self.status_text.set('Encrypting...')
        self.progress_value.set(55)
        self.parent.update_idletasks()

        with open(output_path, 'wb') as output_file:
            output_file.write(payload)

        self.status_text.set('Generating cipher text...')
        self.progress_value.set(80)
        cipher_preview = CryptoEngine.create_cipher_preview(payload, max_chars=1800)
        self.cipher_text.delete('1.0', tk.END)
        self.cipher_text.insert(tk.END, cipher_preview)
        self.progress_value.set(100)
        self.status_text.set('Encryption complete')
        self.log('Text encrypted and saved: ' + os.path.basename(output_path))
        self.db_manager.log_action(self.username, 'encrypt')
        messagebox.showinfo('Encryption Complete', f'Encrypted output saved to:\n{output_path}')

    def encrypt_file(self, input_path, output_path):
        self.status_text.set('Reading file...')
        self.progress_value.set(25)
        self.parent.update_idletasks()

        with open(input_path, 'rb') as source_file:
            file_bytes = source_file.read()

        payload = CryptoEngine.hybrid_encrypt(file_bytes, self.public_key_text, self.private_key_text)

        self.status_text.set('Encrypting...')
        self.progress_value.set(55)
        self.parent.update_idletasks()

        with open(output_path, 'wb') as output_file:
            output_file.write(payload)

        self.status_text.set('Generating cipher text...')
        self.progress_value.set(80)
        cipher_preview = CryptoEngine.create_cipher_preview(payload, max_chars=1800)
        self.cipher_text.delete('1.0', tk.END)
        self.cipher_text.insert(tk.END, cipher_preview)
        self.progress_value.set(100)
        self.status_text.set('Encryption complete')
        self.log('File encrypted and saved: ' + os.path.basename(output_path))
        self.db_manager.log_action(self.username, 'encrypt')
        messagebox.showinfo('Encryption Complete', f'File encrypted successfully:\n{output_path}')

    def start_decrypt(self):
        self.status_text.set('Validating keys...')
        self.progress_value.set(10)
        self.public_key_text = self.public_key_text_widget.get('1.0', tk.END).strip()
        self.private_key_text = self.private_key_text_widget.get('1.0', tk.END).strip()

        if not self.public_key_text or not self.private_key_text:
            messagebox.showerror('Missing Keys', 'Both public and private keys are required for decryption.')
            self.status_text.set('Missing keys')
            return

        valid, result = CryptoEngine.validate_key_pair(self.public_key_text, self.private_key_text)
        if not valid:
            messagebox.showerror('Invalid Keys', result)
            self.status_text.set('Invalid keys')
            self.log('Decryption blocked: invalid key pair')
            return

        encrypted_path = self.encrypted_file_path.get().strip()
        if not encrypted_path or not os.path.isfile(encrypted_path):
            messagebox.showwarning('Select File', 'Please select a valid encrypted file.')
            self.status_text.set('Encrypted file required')
            return

        default_name = os.path.splitext(os.path.basename(encrypted_path))[0] + '_decrypted'
        output_path = filedialog.asksaveasfilename(
            title='Save decrypted file',
            defaultextension='.bin',
            initialfile=default_name,
            filetypes=[('All files', '*.*')],
        )
        if not output_path:
            self.status_text.set('Decryption cancelled')
            return

        self.log('Decrypting file: ' + os.path.basename(encrypted_path))
        self.decrypt_file(encrypted_path, output_path)

    def decrypt_file(self, encrypted_path, output_path):
        self.status_text.set('Loading cipher...')
        self.progress_value.set(20)
        self.parent.update_idletasks()

        with open(encrypted_path, 'rb') as encrypted_file:
            payload = encrypted_file.read()

        self.status_text.set('Decrypting...')
        self.progress_value.set(50)
        self.parent.update_idletasks()

        try:
            decrypted_data = CryptoEngine.hybrid_decrypt(payload, self.public_key_text, self.private_key_text)
        except ValueError as error:
            messagebox.showerror('Decryption Error', str(error))
            self.status_text.set('Invalid Keys')
            self.log('Decryption failed: ' + str(error))
            return

        with open(output_path, 'wb') as output_file:
            output_file.write(decrypted_data)

        self.status_text.set('Processing result...')
        self.progress_value.set(80)
        self.parent.update_idletasks()

        self.last_decrypted_data = decrypted_data
        self.last_decrypted_filename = output_path
        try:
            text = decrypted_data.decode('utf-8')
        except UnicodeDecodeError:
            text = '[Binary data saved to file]'

        self.decrypted_text.delete('1.0', tk.END)
        self.decrypted_text.insert(tk.END, text)
        self.progress_value.set(100)
        self.status_text.set('Decryption complete')
        self.log('Decrypted file saved: ' + os.path.basename(output_path))
        self.db_manager.log_action(self.username, 'decrypt')
        messagebox.showinfo('Decryption Complete', f'Decrypted file saved to:\n{output_path}')

    def save_decrypted_output(self):
        if not self.last_decrypted_data:
            messagebox.showwarning('No Result', 'There is no decrypted result to save.')
            return
        save_path = filedialog.asksaveasfilename(
            title='Save decrypted file',
            initialfile=os.path.basename(self.last_decrypted_filename),
            filetypes=[('All files', '*.*')],
        )
        if not save_path:
            return
        with open(save_path, 'wb') as output_file:
            output_file.write(self.last_decrypted_data)
        self.log('Saved decrypted output to: ' + os.path.basename(save_path))
        messagebox.showinfo('Saved', f'Decrypted output saved to:\n{save_path}')

    def logout(self):
        self.db_manager.log_action(self.username, 'logout')
        self.logout_callback()

    def update_key_labels(self):
        """Update labels to show if keys are manual or auto-generated"""
        pub_label = f"(Source: {self.public_key_source})" if self.public_key_source else ""
        priv_label = f"(Source: {self.private_key_source})" if self.private_key_source else ""
        self.public_key_label.config(text=pub_label)
        self.private_key_label.config(text=priv_label)

    def on_public_key_change(self, event=None):
        """Handle public key text changes"""
        self.public_key_text = self.public_key_text_widget.get('1.0', tk.END).strip()
        if self.public_key_text:
            self.public_key_source = 'manual'
            self.update_key_labels()

    def on_private_key_change(self, event=None):
        """Handle private key text changes and auto-generate public key"""
        self.private_key_text = self.private_key_text_widget.get('1.0', tk.END).strip()
        if self.private_key_text:
            self.private_key_source = 'manual'
            self.auto_generate_public_from_private()

    def auto_generate_public_from_private(self):
        """Automatically derive public key from private key"""
        if not self.private_key_text.strip():
            return
        
        try:
            private_key = CryptoEngine.load_private_key(self.private_key_text)
            public_key = private_key.public_key()
            
            from cryptography.hazmat.primitives import serialization
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode('utf-8')
            
            self.public_key_text = public_pem
            self.public_key_text_widget.delete('1.0', tk.END)
            self.public_key_text_widget.insert(tk.END, public_pem)
            self.public_key_source = 'auto-generated'
            self.update_key_labels()
            self.log('✓ Public key auto-generated from private key')
        except Exception as error:
            # Invalid private key, no action needed
            pass

    def save_public_key(self):
        """Save public key to file"""
        public_key_text = self.public_key_text_widget.get('1.0', tk.END).strip()
        if not public_key_text:
            messagebox.showwarning('Empty Key', 'Public key is empty. Nothing to save.')
            return
        
        save_path = filedialog.asksaveasfilename(
            title='Save public key',
            defaultextension='.pem',
            filetypes=[('PEM files', '*.pem'), ('Key files', '*.key'), ('All files', '*.*')],
            initialfile='public_key.pem'
        )
        if save_path:
            try:
                CryptoEngine.save_key_to_file(public_key_text, save_path)
                self.log('Public key saved: ' + os.path.basename(save_path))
                messagebox.showinfo('Saved', f'Public key saved to:\n{save_path}')
            except Exception as error:
                messagebox.showerror('Save Error', f'Failed to save public key:\n{str(error)}')

    def save_private_key(self):
        """Save private key to file"""
        private_key_text = self.private_key_text_widget.get('1.0', tk.END).strip()
        if not private_key_text:
            messagebox.showwarning('Empty Key', 'Private key is empty. Nothing to save.')
            return
        
        save_path = filedialog.asksaveasfilename(
            title='Save private key',
            defaultextension='.pem',
            filetypes=[('PEM files', '*.pem'), ('Key files', '*.key'), ('All files', '*.*')],
            initialfile='private_key.pem'
        )
        if save_path:
            try:
                CryptoEngine.save_key_to_file(private_key_text, save_path)
                self.log('Private key saved: ' + os.path.basename(save_path))
                messagebox.showinfo('Saved', f'Private key saved to:\n{save_path}')
            except Exception as error:
                messagebox.showerror('Save Error', f'Failed to save private key:\n{str(error)}')

    def log(self, message):
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f'[{timestamp}] {message}\n')
        self.log_text.see(tk.END)
