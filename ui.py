from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QLabel, QApplication
)

from db import fetch_all, insert_memo, delete_memo, fetch_one


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("URL/Password Memo (PySide6 + PostgreSQL)")
        self.resize(900, 500)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        form = QHBoxLayout()
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("タイトル（必須）")
        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("ユーザー名")
        self.pass_edit = QLineEdit()
        self.pass_edit.setPlaceholderText("パスワード")
        self.pass_edit.setEchoMode(QLineEdit.Password)
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("URL")

        self.add_btn = QPushButton("追加")
        self.add_btn.clicked.connect(self.on_add)

        form.addWidget(QLabel("タイトル"))
        form.addWidget(self.title_edit, 2)
        form.addWidget(QLabel("ユーザー名"))
        form.addWidget(self.user_edit, 2)
        form.addWidget(QLabel("パスワード"))
        form.addWidget(self.pass_edit, 2)
        form.addWidget(QLabel("URL"))
        form.addWidget(self.url_edit, 3)
        form.addWidget(self.add_btn)
        layout.addLayout(form)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "タイトル", "ユーザー名", "パスワード", "URL", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self.on_cell_clicked)
        self.table.setColumnHidden(0, True)
        layout.addWidget(self.table)

        self.reload()

    def reload(self):
        rows = fetch_all()
        self.table.setRowCount(0)

        for r, (memo_id, title, username, password, url) in enumerate(rows):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(memo_id)))
            self.table.setItem(r, 1, QTableWidgetItem(title or ""))
            self.table.setItem(r, 2, QTableWidgetItem(username or ""))
            self.table.setItem(r, 3, QTableWidgetItem("●●●●●" if (password or "") else ""))
            self.table.setItem(r, 4, QTableWidgetItem(url or ""))

            del_btn = QPushButton("削除")
            del_btn.clicked.connect(lambda _, mid=memo_id: self.on_delete(mid))
            self.table.setCellWidget(r, 5, del_btn)

    def on_add(self):
        title = self.title_edit.text().strip()
        username = self.user_edit.text().strip()
        password = self.pass_edit.text()
        url = self.url_edit.text().strip()

        if not title:
            QMessageBox.warning(self, "入力エラー", "タイトルは必須です。")
            return

        insert_memo(title, username, password, url)

        self.title_edit.clear()
        self.user_edit.clear()
        self.pass_edit.clear()
        self.url_edit.clear()
        self.reload()

    def on_delete(self, memo_id: int):
        ret = QMessageBox.question(self, "確認", "このメモを削除しますか？")
        if ret == QMessageBox.Yes:
            delete_memo(memo_id)
            self.reload()

    def on_cell_clicked(self, row: int, col: int):
        memo_id = int(self.table.item(row, 0).text())

        if col not in (1, 2, 3, 4):
            return

        record = fetch_one(memo_id)
        if not record:
            return

        title, username, password, url = record
        value = {1: title, 2: username, 3: password, 4: url}.get(col) or ""
        if value == "":
            return

        QApplication.clipboard().setText(value)
        self.statusBar().showMessage("コピーしました", 1500)