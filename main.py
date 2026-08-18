#!/usr/bin/env python3
import tkinter as tk
from database.db_manager import DatabaseManager
from ui.login_view import LoginView
from ui.dashboard_view import DashboardView


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Asymmetric Secure Encryption and Decryption System')
        self.geometry('1280x860')
        self.configure(bg='#181a1f')
        self.resizable(True, True)

        self.db_manager = DatabaseManager()
        self.current_user = None

        self.login_frame = LoginView(self, self.db_manager, self.open_dashboard)
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        self.dashboard_frame = None

        self.protocol('WM_DELETE_WINDOW', self.on_close)

    def open_dashboard(self, username, role):
        self.current_user = username
        self.login_frame.pack_forget()
        self.dashboard_frame = DashboardView(
            self,
            self.db_manager,
            username,
            role,
            self.logout,
        )
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)

    def logout(self):
        if self.dashboard_frame:
            self.dashboard_frame.pack_forget()
            self.dashboard_frame.destroy()
            self.dashboard_frame = None

        self.current_user = None
        self.login_frame = LoginView(self, self.db_manager, self.open_dashboard)
        self.login_frame.pack(fill=tk.BOTH, expand=True)

    def on_close(self):
        self.db_manager.close()
        self.destroy()


def main():
    app = Application()
    app.mainloop()


if __name__ == '__main__':
    main()
