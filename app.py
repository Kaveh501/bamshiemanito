

import hashlib
import string
import random
import sys
import os
import shutil
import sqlite3

from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QDialog, QFormLayout, QDialogButtonBox,
    QFileDialog, QMessageBox, QScrollArea, QGridLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QMenu, QFileDialog


# new path
def resource_path(relative_path):
    """برمی‌گردونه مسیر درست فایل چه در زمان اجرا و چه در حالت بسته‌بندی شده"""
    try:
        base_path = sys._MEIPASS  # موقعی که از داخل exe اجرا میشه
    except AttributeError:
        base_path = os.path.abspath(".")  # موقعی که از سورس اجرا میشه
    return os.path.join(base_path, relative_path)

# code generator


def generate_license_key(length=12):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_licenses_file(filename='license.data', count=1000):
    with open(filename, 'w') as f:
        for _ in range(count):
            key = generate_license_key()
            f.write(f"{key},False\n")


if __name__ == "__main__":
    generate_licenses_file()
    print("✅ فایل license.data با 1000 کد لایسنس ساخته شد.")


def main():
    print("به بامشی منی خوش اوومدید 🤗")


if __name__ == "__main__":
    main()

behavior_modes = {
    "شوخ": "😜 حالت بات روی 'شوخ' تنظیم شد.",
    "جدی": "🧐 حالت بات روی 'جدی' تنظیم شد.",
    "عاشق": "😍 حالت بات روی 'عاشق' تنظیم شد."
}

IMAGES_FOLDER = "images"
PASSWORD = "2143"

if not os.path.exists(IMAGES_FOLDER):
    os.makedirs(IMAGES_FOLDER)

# === اضافه شده: بارگذاری لایسنس‌ها ===


def load_valid_licenses(filename='license.data'):
    valid_licenses = {}
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    key, used = parts
                    if used == 'False':  # فقط لایسنس‌های استفاده نشده
                        valid_licenses[key] = False
    return valid_licenses

# === اضافه شده: صفحه ورود لایسنس و کد ۴ رقمی ===


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ورود با لایسنس و کد ۴ رقمی")
        self.setModal(True)

        self.valid_licenses = load_valid_licenses()

        layout = QFormLayout(self)

        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("کد لایسنس را وارد کنید")

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("کد ۴ رقمی دلخواه خود را وارد کنید")
        self.code_input.setMaxLength(4)
        self.code_input.setEchoMode(QLineEdit.Password)

        layout.addRow("لایسنس:", self.license_input)
        layout.addRow("کد ۴ رقمی:", self.code_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.check_inputs)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        self.entered_code = None

    def check_inputs(self):
        license_key = self.license_input.text().strip()
        code = self.code_input.text().strip()

        if license_key not in self.valid_licenses:
            QMessageBox.warning(
                self, "خطا", "کد لایسنس اشتباه است یا استفاده شده.")
            return

        if not (code.isdigit() and len(code) == 4):
            QMessageBox.warning(
                self, "خطا", "کد ۴ رقمی باید دقیقا ۴ رقم عددی باشد.")
            return

        self.entered_code = code

        # اختیاری: علامت استفاده از لایسنس در فایل (مثلاً)
        self.mark_license_used(license_key)

        self.accept()

    def mark_license_used(self, license_key):
        # خواندن کل لایسنس‌ها و تغییر وضعیت لایسنس مورد نظر
        try:
            lines = []
            with open('license.data', 'r') as f:
                lines = f.readlines()
            with open('license.data', 'w') as f:
                for line in lines:
                    key, used = line.strip().split(',')
                    if key == license_key:
                        f.write(f"{key},True\n")
                    else:
                        f.write(line)
        except Exception as e:
            print(f"خطا در به‌روزرسانی فایل لایسنس‌ها: {e}")

# ——————— بقیه کلاس‌های قبلی ات رو همونجوری نگه داشتم ————————


class TeachDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("انتقال داده و خاطرات به بامشی منی ")
        self.setModal(True)
        self.layout = QFormLayout(self)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addRow("رمز:", self.password_input)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.layout.addWidget(self.buttons)
        self.buttons.accepted.connect(self.check_password)
        self.buttons.rejected.connect(self.reject)

        self.question_input = QLineEdit()
        self.answer_input = QLineEdit()

        self.state = 'password'

    def check_password(self):
        if self.state == 'password':
            if self.password_input.text() == PASSWORD:
                self.layout.removeWidget(self.password_input)
                self.password_input.deleteLater()
                self.layout.removeWidget(self.buttons)
                self.buttons.deleteLater()

                self.layout.addRow("سوال:", self.question_input)
                self.layout.addRow("جواب:", self.answer_input)

                self.buttons = QDialogButtonBox(
                    QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                self.layout.addWidget(self.buttons)
                self.buttons.accepted.connect(self.accept)
                self.buttons.rejected.connect(self.reject)

                self.state = 'question_answer'
            else:
                self.password_input.setText('')
                self.password_input.setPlaceholderText(
                    "رمز اشتباهه، دوباره تلاش کن.")
        else:
            self.accept()

    def get_question_answer(self):
        return self.question_input.text().strip(), self.answer_input.text().strip()


class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ورود رمز گالری 🖼️")
        self.setModal(True)
        layout = QVBoxLayout(self)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("رمز را وارد کنید:"))
        layout.addWidget(self.password_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        buttons.accepted.connect(self.check_password)
        buttons.rejected.connect(self.reject)

    def check_password(self):
        if self.password_input.text() == PASSWORD:
            self.accept()
        else:
            QMessageBox.warning(self, "خطا", "رمز اشتباه است!")
            self.password_input.clear()
# save pic


class ClickableLabel(QLabel):
    def __init__(self, image_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_path = image_path

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        save_action = menu.addAction("ذخیره عکس")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == save_action:
            self.save_image()

    def save_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(
            self, "ذخیره عکس به عنوان", self.image_path,
            "Images (*.png *.jpg *.jpeg *.gif)", options=options)
        if filename:
            try:
                import shutil
                shutil.copyfile(self.image_path, filename)
            except Exception as e:
                QMessageBox.warning(self, "خطا", f"ذخیره عکس انجام نشد:\n{e}")


class GalleryWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("گالری تصاویر بامشی منی")
        self.resize(600, 400)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        grid = QGridLayout(content)

        images = [f for f in os.listdir(IMAGES_FOLDER) if f.lower().endswith(
            (".png", ".jpg", ".jpeg", ".gif"))]
        if not images:
            label = QLabel("گالری خالی است 🌚")
            label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(label)
            return

        row, col = 0, 0
        # داخل متد __init__ کلاس GalleryWindow، اون قسمت که عکس‌ها رو می‌سازی این‌جوری تغییر بده:

        for img_name in images:
            img_path = os.path.join(IMAGES_FOLDER, img_name)
            pixmap = QPixmap(img_path)
            pixmap = pixmap.scaled(
                150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl = ClickableLabel(img_path)
            lbl.setPixmap(pixmap)
            lbl.setToolTip(img_name)
            grid.addWidget(lbl, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1


class ChatBotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("😻 هوش مصنوعی بامشی منی")
        self.setGeometry(100, 100, 600, 580)

        # اینو اضافه کردم که کد ۴ رقمی رو نگه داریم
        self.user_code = None

        # افزودن بک‌گراند

        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, 600, 580)
        self.bg_label.lower()  # بک‌گراند بیاد عقب

# حالا عکس رو روی اون ست می‌کنیم
        bg_path = resource_path("bamshi.jpg")
        self.bg_label.setPixmap(QPixmap(bg_path).scaled(
            self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

        self.setStyleSheet("""
            QTextEdit, QLineEdit, QLabel, QComboBox {
                background-color: rgba(255, 255, 255, 160);
                color: #000;
                font-size: 18px;
                border-radius: 8px;
                padding: 4px;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #aaa;
                border-radius: 8px;
                padding: 16px;
            }
        """)

        self.bg_label.setGeometry(0, 0, 600, 580)
        self.bg_label.lower()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.db_init()
        self.load_knowledge()

        self.profile_name = None
        self.greeted = False

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(behavior_modes.keys())
        self.layout.addWidget(QLabel("😌 حالت رفتاری:"))
        self.layout.addWidget(self.mode_selector)

        self.language_selector = QComboBox()
        self.language_selector.addItems(["فارسی", "English"])
        self.layout.addWidget(QLabel("🌐 زبان:"))
        self.layout.addWidget(self.language_selector)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        self.input_box = QLineEdit()
        self.send_button = QPushButton("📤 ارسال")

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)
        self.layout.addLayout(input_layout)

        self.teach_button = QPushButton("🎓 یاد بده به بامشی (رمز می‌خواد)")
        self.layout.addWidget(self.teach_button)

        btn_layout = QHBoxLayout()
        self.upload_btn = QPushButton("📤 آپلود عکس")
        self.gallery_btn = QPushButton("🖼 دیدن گالری (رمز می‌خواد)")
        btn_layout.addWidget(self.upload_btn)
        btn_layout.addWidget(self.gallery_btn)
        self.layout.addLayout(btn_layout)

        self.send_button.clicked.connect(self.handle_message)
        self.input_box.returnPressed.connect(self.send_button.click)
        self.teach_button.clicked.connect(self.open_teach_dialog)

        self.upload_btn.clicked.connect(self.upload_image)
        self.gallery_btn.clicked.connect(self.open_gallery)

        self.show_name_request()

    def resizeEvent(self, event):
        self.bg_label.setPixmap(QPixmap("bamshi.jpg").scaled(
            self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def db_init(self):
        self.conn = sqlite3.connect("chatbot_data.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                question TEXT PRIMARY KEY,
                answer TEXT
            )
        """)
        self.conn.commit()
        self.knowledge_base = {}

    def load_knowledge(self):
        self.cursor.execute("SELECT question, answer FROM knowledge")
        rows = self.cursor.fetchall()
        for q, a in rows:
            self.knowledge_base[q] = a

    def show_name_request(self):
        self.chat_display.clear()
        self.chat_display.append("😻 لطفاً اسمت رو وارد کن تا شروع کنیم.")
        self.input_box.clear()

    def handle_message(self):
        user_msg = self.input_box.text().strip()
        if not user_msg:
            return

        if self.profile_name is None:
            self.profile_name = user_msg
            self.chat_display.append(
                f"👋 سلام {self.profile_name} کرتیم! بزن بریم...")
            self.input_box.clear()
            return

        self.chat_display.append(f"👤 {self.profile_name}: {user_msg}")
        self.input_box.clear()

        QTimer.singleShot(400, lambda: self.respond(user_msg))

    def respond(self, text):
        response = self.generate_answer(text)
        self.chat_display.append(f"😻 بامشی منی: {response}")

    def generate_answer(self, text):
        mode = self.mode_selector.currentText()
        lang = self.language_selector.currentText()

        lower_text = text.lower()
        for known_q in self.knowledge_base.keys():
            if lower_text == known_q.lower():
                return self.knowledge_base[known_q]

        if mode == "شوخ":
            base = f"😂 هنوز جواب '{text}' رو یاد نگرفتم، ولی حسابی می‌خندم!"
            return base
        elif mode == "جدی":
            base = f"📚 درباره '{text}' اطلاعاتی ندارم، لطفاً بعداً سؤال کن."
            return base
        elif mode == "عاشق":
            base = f"❤️ عاشقانه می‌گویم، اما درباره '{text}' چیز زیادی نمی‌دانم."
            return base
        else:
            return "🤔 نمی‌فهمم چی می‌گی!"

    def open_teach_dialog(self):
        dlg = TeachDialog(self)
        if dlg.exec():
            question, answer = dlg.get_question_answer()
            if question and answer:
                self.knowledge_base[question] = answer
                self.cursor.execute(
                    "INSERT OR REPLACE INTO knowledge (question, answer) VALUES (?, ?)", (question, answer))
                self.conn.commit()
                self.chat_display.append(
                    f"🎓 بات یاد گرفت: '{question}' جوابش '{answer}' هست.")
            else:
                self.chat_display.append("⚠️ سوال یا جواب خالیه!")

    def upload_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب تصویر برای آپلود", "", "Images (*.png *.jpg *.jpeg *.gif)", options=options)
        if file_path:
            try:
                base_name = os.path.basename(file_path)
                dest_path = os.path.join(IMAGES_FOLDER, base_name)
                counter = 1
                name, ext = os.path.splitext(base_name)
                while os.path.exists(dest_path):
                    dest_path = os.path.join(
                        IMAGES_FOLDER, f"{name}_{counter}{ext}")
                    counter += 1
                shutil.copyfile(file_path, dest_path)
                QMessageBox.information(self, "موفق", "عکس آپلود شد! 🎉")
            except Exception as e:
                QMessageBox.warning(self, "خطا", f"آپلود عکس انجام نشد:\n{e}")

    def open_gallery(self):
        dlg = PasswordDialog(self)
        if dlg.exec():
            gallery = GalleryWindow(self)
            gallery.exec()


# add new one
LOCAL_LICENSE_FILE = "license.ok"


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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # اگر فایل لایسنس محلی وجود داشت، دیگه نپرس!
    if os.path.exists(LOCAL_LICENSE_FILE):
        print("✅ لایسنس محلی معتبر یافت شد. ورود خودکار انجام شد.")
        chatbot = ChatBotGUI()
        chatbot.show()
        sys.exit(app.exec())

    else:
        # نیاز به ورود لایسنس و کد چهاررقمی فقط بار اول
        login = LoginDialog()
        if login.exec() == QDialog.Accepted:
            license_code = login.license_input.text().strip()
            save_local_license(license_code)
            chatbot = ChatBotGUI()
            chatbot.user_code = login.entered_code
            chatbot.show()
            sys.exit(app.exec())
        else:
            sys.exit()
