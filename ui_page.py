from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QPushButton, QMessageBox
)
from db import get_page, update_page

class PageWindow(QMainWindow):
    def __init__(self, page_id: int, on_saved=None):
        super().__init__()
        self.page_id = page_id
        self.on_saved = on_saved

        self.setWindowTitle("Page")
        self.resize(800, 600)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        top = QHBoxLayout()
        self.title_edit = QLineEdit()
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save)

        top.addWidget(self.title_edit, 1)
        top.addWidget(self.save_btn)
        layout.addLayout(top)

        self.body_edit = QTextEdit()
        layout.addWidget(self.body_edit, 1)

        self.load()

    def load(self):
        row = get_page(self.page_id)
        if not row:
            QMessageBox.warning(self, "エラー", "ページが見つかりません。")
            self.close()
            return
        _, title, body = row
        self.title_edit.setText(title)
        self.body_edit.setPlainText(body)
        self.setWindowTitle(f"Page: {title}")

    def save(self):
        title = self.title_edit.text().strip()
        body = self.body_edit.toPlainText()

        if not title:
            QMessageBox.warning(self, "入力エラー", "タイトルは必須です。")
            return

        update_page(self.page_id, title, body)
        self.setWindowTitle(f"Page: {title}")
        self.statusBar().showMessage("保存しました", 1200)
        if self.on_saved:
            self.on_saved()