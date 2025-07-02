import os
import sys
import shutil
import hashlib
import string
import random
import sqlite3


from config import PASSWORD_FILE, DEFAULT_PASSWORD, LICENSE_FILE, LOCAL_LICENSE_FILE, IMAGES_FOLDER, BG_IMAGE
from telegram_link import create_telegram_button

from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QDialog, QFormLayout, QDialogButtonBox,
    QFileDialog, QMessageBox, QScrollArea, QGridLayout, QMenu
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

# 🔗 تنظیمات جداگانه
from config import PASSWORD_FILE, DEFAULT_PASSWORD, LICENSE_FILE, LOCAL_LICENSE_FILE, IMAGES_FOLDER, BG_IMAGE

# === UTILS ===


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def generate_license_key(length=12):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_licenses_file(filename=LICENSE_FILE, count=1000):
    with open(filename, 'w') as f:
        for _ in range(count):
            f.write(f"{generate_license_key()},False\n")


def load_valid_licenses(filename=LICENSE_FILE):
    valid = {}
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                key, used = line.strip().split(',')
                if used == 'False':
                    valid[key] = False
    return valid


def get_password(filename=PASSWORD_FILE):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read().strip()
    else:
        return DEFAULT_PASSWORD


def save_password(new_pass, filename=PASSWORD_FILE):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_pass)


def save_local_license(code):
    hashed = hashlib.sha256(code.encode()).hexdigest()
    with open(LOCAL_LICENSE_FILE, 'w') as f:
        f.write(hashed)


def is_local_license_valid(code):
    if not os.path.exists(LOCAL_LICENSE_FILE):
        return False
    try:
        with open(LOCAL_LICENSE_FILE, 'r') as f:
            stored_hash = f.read().strip()
        return stored_hash == hashlib.sha256(code.encode()).hexdigest()
    except:
        return False

# === DIALOGS ===


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login with License")
        self.valid_licenses = load_valid_licenses()
        self.entered_code = None

        layout = QFormLayout(self)
        self.license_input = QLineEdit()
        self.code_input = QLineEdit()
        self.code_input.setMaxLength(4)
        self.code_input.setEchoMode(QLineEdit.Password)

        layout.addRow("License Code:", self.license_input)
        layout.addRow("PIN (4-digit):", self.code_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.check_inputs)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def check_inputs(self):
        license_key = self.license_input.text().strip()
        code = self.code_input.text().strip()

        if license_key not in self.valid_licenses:
            QMessageBox.warning(self, "Error", "Invalid or used license key.")
            return

        if not (code.isdigit() and len(code) == 4):
            QMessageBox.warning(self, "Error", "PIN must be 4 digits.")
            return

        self.entered_code = code
        self.mark_license_used(license_key)
        self.accept()

    def mark_license_used(self, key):
        try:
            lines = []
            with open(LICENSE_FILE, 'r') as f:
                lines = f.readlines()
            with open(LICENSE_FILE, 'w') as f:
                for line in lines:
                    k, used = line.strip().split(',')
                    if k == key:
                        f.write(f"{k},True\n")
                    else:
                        f.write(line)
        except:
            pass


class PasswordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Gallery Password 🛅")
        layout = QVBoxLayout(self)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Enter Password: 🛅"))
        layout.addWidget(self.password_input)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.check_password)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def check_password(self):
        if self.password_input.text() == get_password():
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Wrong password!")
            self.password_input.clear()


class ChangePasswordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Change Gallery Password 🛅")
        layout = QFormLayout(self)
        self.old = QLineEdit()
        self.old.setEchoMode(QLineEdit.Password)
        self.new = QLineEdit()
        self.new.setEchoMode(QLineEdit.Password)
        layout.addRow("Current Password:", self.old)
        layout.addRow("New Password:", self.new)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.change_password)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def change_password(self):
        old_pass = self.old.text()
        new_pass = self.new.text()
        if old_pass != get_password():
            QMessageBox.warning(self, "Error", "Old password is incorrect.")
            return
        if len(new_pass) < 4:
            QMessageBox.warning(
                self, "Error", "New password must be at least 4 characters.")
            return
        save_password(new_pass)
        QMessageBox.information(self, "Success", "Password changed.")
        self.accept()


class TeachDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teach Bamshi Manito")
        layout = QFormLayout(self)
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        layout.addRow("Password:", self.password)
        self.q = QLineEdit()
        self.a = QLineEdit()
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.check_pass)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)
        self.setLayout(layout)
        self.step = 1

    def check_pass(self):
        if self.step == 1:
            if self.password.text() == get_password():
                layout = self.layout()
                layout.removeRow(0)
                layout.removeRow(0)
                layout.insertRow(0, "Question:", self.q)
                layout.insertRow(1, "Answer:", self.a)
                self.step = 2
            else:
                self.password.setText("")
                self.password.setPlaceholderText("Wrong password")
        else:
            self.accept()

    def get_qa(self):
        return self.q.text().strip(), self.a.text().strip()


class ClickableLabel(QLabel):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        save = menu.addAction("Save Image")
        if menu.exec_(self.mapToGlobal(event.pos())) == save:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save As", self.image_path, "Images (*.png *.jpg *.jpeg *.gif)")
            if filename:
                shutil.copyfile(self.image_path, filename)


class GalleryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bamshie Manito Gallery 🖼️")
        self.resize(600, 400)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        content = QWidget()
        scroll.setWidget(content)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        grid = QGridLayout(content)
        images = [f for f in os.listdir(IMAGES_FOLDER) if f.lower().endswith(
            (".png", ".jpg", ".jpeg", ".gif"))]
        if not images:
            layout.addWidget(QLabel("No images found!"))
            return
        row = col = 0
        for img in images:
            path = os.path.join(IMAGES_FOLDER, img)
            pixmap = QPixmap(path).scaled(150, 150, Qt.KeepAspectRatio)
            lbl = ClickableLabel(path)
            lbl.setPixmap(pixmap)
            grid.addWidget(lbl, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

# === MAIN WINDOW ===


class ChatBotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bamshie Manito 😻")
        self.resize(600, 580)
        self.profile_name = None
        self.user_code = None
        self.knowledge_base = {}
        self.greeted = False

        self.bg = QLabel(self)
        self.bg.setPixmap(QPixmap(resource_path(BG_IMAGE)).scaled(
            self.size(), Qt.IgnoreAspectRatio))
        self.bg.lower()

        self.setStyleSheet("""
            QTextEdit, QLineEdit, QLabel, QComboBox, QPushButton {
                background: rgba(255,255,255,0.8);
                    font-size: 8pt;
                    font-family: "Segoe UI", "Arial", sans-serif;
            
            }
        """)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Funny", "Serious", "Romantic"])

        self.language_selector = QComboBox()
        self.language_selector.addItems(["English"])

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        self.input_box = QLineEdit()
        self.send_button = QPushButton("Send")

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)

        self.teach_button = QPushButton("Teach Bamshie Manito👩‍🏫")
        self.upload_btn = QPushButton("Upload Image🌸")
        self.gallery_btn = QPushButton("Open Gallery🖼️")
        self.change_pass_btn = QPushButton("Change Password🛅")
        self.telegram_btn = create_telegram_button()

        btns = QHBoxLayout()
        btns.addWidget(self.upload_btn)
        btns.addWidget(self.gallery_btn)
        btns.addWidget(self.change_pass_btn)
        btns.addWidget(self.telegram_btn)

        self.layout.addWidget(QLabel("Mode:😌"))
        self.layout.addWidget(self.mode_selector)
        self.layout.addWidget(QLabel("Language:🌏"))
        self.layout.addWidget(self.language_selector)
        self.layout.addWidget(self.chat_display)
        self.layout.addLayout(input_layout)
        self.layout.addWidget(self.teach_button)
        self.layout.addLayout(btns)

        self.send_button.clicked.connect(self.handle_message)
        self.input_box.returnPressed.connect(self.send_button.click)
        self.teach_button.clicked.connect(self.open_teach_dialog)
        self.upload_btn.clicked.connect(self.upload_image)
        self.gallery_btn.clicked.connect(self.open_gallery)
        self.change_pass_btn.clicked.connect(self.change_password)

        self.db_init()
        self.load_knowledge()
        self.show_name_request()

    def resizeEvent(self, event):
        self.bg.setPixmap(QPixmap(resource_path(BG_IMAGE)).scaled(
            self.size(), Qt.IgnoreAspectRatio))
        self.bg.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def db_init(self):
        self.conn = sqlite3.connect("chatbot_data.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS knowledge (question TEXT PRIMARY KEY, answer TEXT)"
        )
        self.conn.commit()

    def load_knowledge(self):
        self.cursor.execute("SELECT question, answer FROM knowledge")
        for q, a in self.cursor.fetchall():
            self.knowledge_base[q.lower()] = a

    def show_name_request(self):
        self.chat_display.append("Hi! What's your name?")
        self.input_box.clear()

    def handle_message(self):
        text = self.input_box.text().strip()
        if not text:
            return
        if not self.profile_name:
            self.profile_name = text
            self.chat_display.append(f"🤗 Hello {self.profile_name}!")
        else:
            self.chat_display.append(f"{self.profile_name}: {text}")
            QTimer.singleShot(400, lambda: self.respond(text))
        self.input_box.clear()

    def respond(self, text):
        response = self.generate_answer(text)
        self.chat_display.append(f"Bamshi: {response}")

    def generate_answer(self, text):
        lower = text.lower()
        if lower in self.knowledge_base:
            return self.knowledge_base[lower]
        mode = self.mode_selector.currentText()
        if mode == "Funny":
            return f"😂 I don't know '{text}' yet, but that sounds hilarious!"
        elif mode == "Serious":
            return f"📚 I have no data on '{text}'. Ask me later."
        elif mode == "Romantic":
            return f"❤️ I don't know much about '{text}', but I love the way you said it."

    def open_teach_dialog(self):
        class TeachDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Teach Bamshi")
                self.layout = QFormLayout(self)

                self.password_input = QLineEdit()
                self.password_input.setEchoMode(QLineEdit.Password)
                self.q_input = QLineEdit()
                self.a_input = QLineEdit()
                self.step = 1

                self.layout.addRow("Password:", self.password_input)

                self.buttons = QDialogButtonBox(
                    QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                self.buttons.accepted.connect(self.validate)
                self.buttons.rejected.connect(self.reject)
                self.layout.addRow(self.buttons)

            def validate(self):
                if self.step == 1:
                    if self.password_input.text() == get_password():
                        self.layout.removeRow(0)
                        self.layout.insertRow(0, "Question:", self.q_input)
                        self.layout.insertRow(1, "Answer:", self.a_input)
                        self.step = 2
                    else:
                        self.password_input.clear()
                        self.password_input.setPlaceholderText(
                            "Wrong password")
                else:
                    self.accept()

            def get_qa(self):
                return self.q_input.text().strip(), self.a_input.text().strip()

        dlg = TeachDialog(self)
        if dlg.exec():
            q, a = dlg.get_qa()
            if q and a:
                self.knowledge_base[q.lower()] = a
                self.cursor.execute(
                    "INSERT OR REPLACE INTO knowledge VALUES (?,?)", (q, a))
                self.conn.commit()
                self.chat_display.append(f"Taught: {q} → {a}")

    def upload_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.gif)"
        )
        if path:
            name = os.path.basename(path)
            dest = os.path.join(IMAGES_FOLDER, name)
            shutil.copy(path, dest)

    def open_gallery(self):
        dlg = PasswordDialog()
        if dlg.exec():
            GalleryWindow().exec()

    def change_password(self):
        ChangePasswordDialog().exec()


# === MAIN ===


if __name__ == "__main__":
    app = QApplication(sys.argv)

    if os.path.exists(LOCAL_LICENSE_FILE):
        chatbot = ChatBotGUI()
        chatbot.show()
        sys.exit(app.exec())

    login = LoginDialog()
    if login.exec() == QDialog.Accepted:
        save_local_license(login.license_input.text())
        chatbot = ChatBotGUI()
        chatbot.user_code = login.entered_code
        chatbot.show()
        sys.exit(app.exec())
    else:
        sys.exit()
