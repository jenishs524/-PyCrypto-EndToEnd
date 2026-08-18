#!/usr/bin/env python3
"""Compatibility launcher for the login-enabled Asemmitrick application."""

from main import Application


def main():
    app = Application()
    app.mainloop()


if __name__ == '__main__':
    main()
