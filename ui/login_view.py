import tkinter as tk
from tkinter import messagebox, ttk


class LoginView(ttk.Frame):
    def __init__(self, parent, db_manager, login_callback):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = db_manager
        self.login_callback = login_callback
        self.mode = tk.StringVar(value='login')
        self.configure(style='TFrame')
        self.build_ui()

    def build_ui(self):
        container = ttk.Frame(self, padding=24)
        container.pack(expand=True, fill=tk.BOTH)

        title = ttk.Label(container, text='Asymmetric Secure Encryption and Decryption System', style='Header.TLabel')
        title.pack(pady=(0, 16))

        subtitle = ttk.Label(
            container,
            text='Register once and log in later with your saved credentials.',
            style='Section.TLabel',
        )
        subtitle.pack(pady=(0, 22))

        # Mode selection
        mode_frame = ttk.Frame(container)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Radiobutton(mode_frame, text='Login (existing account)', variable=self.mode, value='login', command=self.update_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text='Register (new account)', variable=self.mode, value='register', command=self.update_mode).pack(side=tk.LEFT, padx=(12, 0))

        note_label = ttk.Label(container, text='If your username is not found, switch to Register and create an account first.', style='Section.TLabel')
        note_label.pack(fill=tk.X, pady=(0, 12))

        form_frame = ttk.Frame(container)
        form_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(form_frame, text='Username:', style='Section.TLabel').grid(row=0, column=0, sticky=tk.W, pady=6)
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=6, padx=(8, 0))

        ttk.Label(form_frame, text='Password:', style='Section.TLabel').grid(row=1, column=0, sticky=tk.W, pady=6)
        self.password_entry = ttk.Entry(form_frame, width=30, show='*')
        self.password_entry.grid(row=1, column=1, pady=6, padx=(8, 0))

        # Confirm password for register mode
        self.confirm_label = ttk.Label(form_frame, text='Confirm Password:', style='Section.TLabel')
        self.confirm_entry = ttk.Entry(form_frame, width=30, show='*')

        button_frame = ttk.Frame(container)
        button_frame.pack(pady=(12, 0))

        self.action_button = ttk.Button(button_frame, text='Login', command=self.perform_action, width=20, style='Accent.TButton')
        self.action_button.pack(side=tk.LEFT)

        self.feedback_label = ttk.Label(container, text='', foreground='#e06c75')
        self.feedback_label.pack(pady=(16, 0))

        self.update_mode()

    def update_mode(self):
        if self.mode.get() == 'register':
            self.confirm_label.grid(row=2, column=0, sticky=tk.W, pady=6)
            self.confirm_entry.grid(row=2, column=1, pady=6, padx=(8, 0))
            self.action_button.config(text='Register Account')
        else:
            self.confirm_label.grid_forget()
            self.confirm_entry.grid_forget()
            self.action_button.config(text='Login')
        self.feedback_label.config(text='')

    def perform_action(self):
        if self.mode.get() == 'login':
            self.login_user()
        else:
            self.register_user()

    def login_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            self.feedback_label.config(text='Please enter both username and password.')
            return

        success, role, message = self.db_manager.authenticate_user(username, password)
        if success:
            self.feedback_label.config(text='', foreground='#98c379')
            self.login_callback(username, role)
        else:
            self.feedback_label.config(text=message, foreground='#e06c75')
            if 'register' in message.lower():
                self.mode.set('register')
                self.update_mode()

    def register_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()
        if not username or not password:
            self.feedback_label.config(text='Please enter both username and password.')
            return
        if password != confirm:
            self.feedback_label.config(text='Passwords do not match.')
            return

        success, message = self.db_manager.register_user(username, password)
        if success:
            self.feedback_label.config(text=message, foreground='#98c379')
            messagebox.showinfo('Registration', 'Account created. You can now log in.')
            self.mode.set('login')
            self.update_mode()
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.confirm_entry.delete(0, tk.END)
        else:
            self.feedback_label.config(text=message, foreground='#e06c75')
