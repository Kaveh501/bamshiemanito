

import os
import sys
import shutil
import hashlib
import string
import random
import sqlite3

from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QDialog, QFormLayout, QDialogButtonBox,
    QFileDialog, QMessageBox, QScrollArea, QGridLayout, QMenu
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

# تنظیمات جداگانه
from config import PASSWORD_FILE, DEFAULT_PASSWORD, LICENSE_FILE, LOCAL_LICENSE_FILE, IMAGES_FOLDER, BG_IMAGE
from telegram_link import create_telegram_button

# === UTILS ===


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_license_ok_path():
    base_path = os.path.abspath(".")  # مسیر اجرای فعلی  exe
    return os.path.join(base_path, "license.ok")


def create_license_ok():
    path = get_license_ok_path()
    with open(path, "w") as f:
        f.write("valid")


def get_local_license_path():
    home = os.path.expanduser("~")
    folder = os.path.join(home, ".bamshie_manito")
    if not os.path.exists(folder):
        os.makedirs(folder)
    return os.path.join(folder, "local_license.data")


def generate_license_key(length=12):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_licenses_file(filename=LICENSE_FILE, count=1000):
    with open(filename, 'w') as f:
        for _ in range(count):
            f.write(f"{generate_license_key()},False\n")


def load_valid_licenses(filename=LICENSE_FILE):
    valid = {}
    file_path = resource_path(filename)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                key, used = line.strip().split(',')
                if used == 'False':
                    valid[key] = False
    return valid


def get_password(filename=PASSWORD_FILE):
    path = resource_path(filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    else:
        return DEFAULT_PASSWORD


def save_password(new_pass, filename=PASSWORD_FILE):
    path = resource_path(filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_pass)


def save_local_license(code):
    hashed = hashlib.sha256(code.encode()).hexdigest()
    path = resource_path(LOCAL_LICENSE_FILE)
    with open(path, 'w') as f:
        f.write(hashed)


def is_local_license_valid():
    path = get_local_license_path()
    if not os.path.exists(path):
        return False
    try:
        with open(path, 'r') as f:
            stored_hash = f.read().strip()
        valid_licenses = load_valid_licenses()
        for key in valid_licenses.keys():
            if hashlib.sha256(key.encode()).hexdigest() == stored_hash:
                return True
        return False
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
            path = resource_path(LICENSE_FILE)
            lines = []
            with open(path, 'r') as f:
                lines = f.readlines()
            with open(path, 'w') as f:
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
        self.setWindowTitle("Teach Bamshie Manito")
        self.setMinimumWidth(300)

        self.layout = QVBoxLayout(self)

        # مرحله اول: ورود رمز
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(QLabel("Enter Admin Password:"))
        self.layout.addWidget(self.pass_input)

        self.next_btn = QPushButton("Next ➡️")
        self.layout.addWidget(self.next_btn)
        self.next_btn.clicked.connect(self.check_password)

        # مرحله دوم: سوال و جواب
        self.q_input = QLineEdit()
        self.a_input = QLineEdit()
        self.q_input.setPlaceholderText("Your question here...")
        self.a_input.setPlaceholderText("Answer to teach...")

        self.q_input.hide()
        self.a_input.hide()

        self.layout.addWidget(QLabel("Question:"))
        self.layout.addWidget(self.q_input)
        self.layout.addWidget(QLabel("Answer:"))
        self.layout.addWidget(self.a_input)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.hide()
        self.layout.addWidget(self.button_box)

    def check_password(self):
        if self.pass_input.text() == get_password():
            self.pass_input.setDisabled(True)
            self.next_btn.hide()
            self.q_input.show()
            self.a_input.show()
            self.button_box.show()
        else:
            QMessageBox.warning(self, "Error", "Wrong password!")

    def get_qa(self):
        return self.q_input.text().strip(), self.a_input.text().strip()


class ClickableLabel(QLabel):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        save = menu.addAction("Save Image")
        if menu.exec_(self.mapToGlobal(event.pos())) == save:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save As", self.image_path, "Images (*.png *.jpg *.jpeg *.gif)"
            )
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

        images_folder_path = os.path.join(os.getcwd(), "user_data", "images")
        images = []
        if os.path.exists(images_folder_path):
            images = [f for f in os.listdir(images_folder_path) if f.lower().endswith(
                (".png", ".jpg", ".jpeg", ".gif"))]

        if not images:
            layout.addWidget(QLabel("No images found!"))
            return
        row = col = 0
        for img in images:
            path = os.path.join(images_folder_path, img)
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

        # new
        user_data_folder = os.path.join(os.getcwd(), "user_data")
        images_folder = os.path.join(user_data_folder, "images")
        if not os.path.exists(images_folder):
            os.makedirs(images_folder)

        self.knowledge_base = {}  # اضافه‌شد برای جلوگیری از ارور
        self.profile_name = None

        self.bg = QLabel(self)
        bg_image_path = resource_path("bamshi.jpg")

        if not os.path.exists(bg_image_path):
            print("❌ Background image not found:", bg_image_path)
        else:
            pixmap = QPixmap(bg_image_path)
            if pixmap.isNull():
                print("❌ Failed to load background image:", bg_image_path)
            else:
                self.bg.setPixmap(pixmap.scaled(
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
        bg_image_path = resource_path("bamshi.jpg")
        if os.path.exists(bg_image_path):
            pixmap = QPixmap(bg_image_path)
            if not pixmap.isNull():
                self.bg.setPixmap(pixmap.scaled(
                    self.size(), Qt.IgnoreAspectRatio))
        self.bg.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def db_init(self):
        db_path = resource_path("chatbot_data.db")
        self.conn = sqlite3.connect(db_path)
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
        dlg = TeachDialog()
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
            user_data_folder = os.path.join(os.getcwd(), "user_data")
            images_folder = os.path.join(user_data_folder, "images")
            dest = os.path.join(images_folder, name)
            try:
                shutil.copy(path, dest)
                QMessageBox.information(
                    self, "Success", f"Image uploaded to:\n{dest}")
            except Exception as e:
                QMessageBox.warning(
                    self, "Error", f"Failed to upload image:\n{str(e)}")

    def open_gallery(self):
        dlg = PasswordDialog()
        if dlg.exec():
            GalleryWindow().exec()

    def change_password(self):
        ChangePasswordDialog().exec()

# === MAIN ===


def ensure_writable_copy(filename):
    src = resource_path(filename)
    dst = os.path.join(os.getcwd(), filename)
    if not os.path.exists(dst) and os.path.exists(src):
        shutil.copy(src, dst)
    return dst


if __name__ == "__main__":
    ensure_writable_copy("license.data")
    ensure_writable_copy("chatbot_data.db")

    app = QApplication(sys.argv)

    license_ok_path = get_license_ok_path()

    if os.path.exists(license_ok_path) or is_local_license_valid():
        chatbot = ChatBotGUI()
        chatbot.show()
        sys.exit(app.exec())
    else:
        login = LoginDialog()
        if login.exec() == QDialog.Accepted:
            save_local_license(login.license_input.text())
            create_license_ok()
            chatbot = ChatBotGUI()
            chatbot.user_code = login.entered_code
            chatbot.show()
            sys.exit(app.exec())
        else:
            sys.exit()
