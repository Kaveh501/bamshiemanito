# telegram_link.py

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl

DEFAULT_USERNAME = "Kavehdesigner"


def create_telegram_button(username=DEFAULT_USERNAME, label="📲 Contact Telegram Support"):
    """
    Creates a QPushButton that opens a Telegram chat with the given username.
    :param username: Telegram username (without @)
    :param label: Button text
    :return: QPushButton
    """
    button = QPushButton(label)
    button.clicked.connect(lambda: open_telegram_chat(username))
    return button


def open_telegram_chat(username):
    """
    Opens Telegram chat in default browser or app.
    """
    url = f"https://t.me/{username}"
    QDesktopServices.openUrl(QUrl(url))
