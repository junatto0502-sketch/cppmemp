from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QLabel, QApplication
)
from PySide6.QtCore import Qt

from db import (
    get_page, update_page_title,
    list_memos, create_memo, delete_memo, get_memo, update_memo
)

class PageWindow(QMainWindow):
    def __init__(self, page_id: int, on_changed=None):
        super().__init__()
        self.page_id = page_id
        self.on_changed = on_changed

        self.resize(900, 650)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        # page title
        top = QHBoxLayout()
        self.page_title = QLineEdit()
        self.page_title.setPlaceholderText("ページタイトル（必須）")
        self.save_page_title_btn = QPushButton("ページ名保存")
        self.save_page_title_btn.clicked.connect(self.save_page_title)
        top.addWidget(QLabel("ページ"))
        top.addWidget(self.page_title, 1)
        top.addWidget(self.save_page_title_btn)
        layout.addLayout(top)

        # add memo
        form = QHBoxLayout()
        self.memo_title = QLineEdit()
        self.memo_title.setPlaceholderText("メモタイトル（必須）")
        self.memo_body = QTextEdit()
        self.memo_body.setPlaceholderText("メモ内容（複数行OK）")
        self.memo_body.setFixedHeight(110)
        self.add_btn = QPushButton("メモ追加")
        self.add_btn.clicked.connect(self.on_add)

        form.addWidget(self.memo_title, 2)
        form.addWidget(self.memo_body, 5)
        form.addWidget(self.add_btn)
        layout.addLayout(form)

        # memos table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "タイトル", "内容（クリックでコピー）", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setColumnHidden(0, True)
        self.table.cellClicked.connect(self.on_cell_clicked)
        layout.addWidget(self.table, 1)

        # edit selected memo (optional, minimal)
        edit = QHBoxLayout()
        self.edit_id = QLabel("選択: -")
        self.edit_title = QLineEdit()
        self.edit_title.setPlaceholderText("選択中メモのタイトル")
        self.edit_body = QTextEdit()
        self.edit_body.setPlaceholderText("選択中メモの内容")
        self.edit_body.setFixedHeight(110)
        self.save_memo_btn = QPushButton("選択メモ保存")
        self.save_memo_btn.clicked.connect(self.on_save_selected)
        edit.addWidget(self.edit_id)
        edit.addWidget(self.edit_title, 2)
        edit.addWidget(self.edit_body, 5)
        edit.addWidget(self.save_memo_btn)
        layout.addLayout(edit)

        self.selected_memo_id = None

        self.load_page()
        self.reload()

    def load_page(self):
        row = get_page(self.page_id)
        if not row:
            QMessageBox.warning(self, "エラー", "ページが見つかりません。")
            self.close()
            return
        _, title = row
        self.page_title.setText(title)
        self.setWindowTitle(f"Page: {title}")

    def reload(self):
        rows = list_memos(self.page_id)
        self.table.setRowCount(0)
        for r, (memo_id, title, body) in enumerate(rows):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(memo_id)))
            self.table.setItem(r, 1, QTableWidgetItem(title or ""))
            self.table.setItem(r, 2, QTableWidgetItem(body or ""))

            del_btn = QPushButton("削除")
            del_btn.clicked.connect(lambda _, mid=memo_id: self.on_delete(mid))
            self.table.setCellWidget(r, 3, del_btn)

    def save_page_title(self):
        title = self.page_title.text().strip()
        if not title:
            QMessageBox.warning(self, "入力エラー", "ページタイトルは必須です。")
            return
        update_page_title(self.page_id, title)
        self.setWindowTitle(f"Page: {title}")
        self.statusBar().showMessage("ページ名を保存しました", 1200)
        if self.on_changed:
            self.on_changed()

    def on_add(self):
        title = self.memo_title.text().strip()
        body = self.memo_body.toPlainText()

        if not title:
            QMessageBox.warning(self, "入力エラー", "メモタイトルは必須です。")
            return

        create_memo(self.page_id, title, body)
        self.memo_title.clear()
        self.memo_body.clear()
        self.reload()
        if self.on_changed:
            self.on_changed()

    def on_delete(self, memo_id: int):
        ret = QMessageBox.question(self, "確認", "このメモを削除しますか？")
        if ret == QMessageBox.Yes:
            delete_memo(memo_id)
            if self.selected_memo_id == memo_id:
                self.selected_memo_id = None
                self.edit_id.setText("選択: -")
                self.edit_title.clear()
                self.edit_body.clear()
            self.reload()
            if self.on_changed:
                self.on_changed()

    def on_cell_clicked(self, row: int, col: int):
        memo_id = int(self.table.item(row, 0).text())

        # 内容クリックでコピー（従来挙動）
        if col == 2:
            txt = self.table.item(row, 2).text()
            if txt:
                QApplication.clipboard().setText(txt)
                self.statusBar().showMessage("内容をコピーしました", 1200)

        # 行選択で下の編集欄にロード
        self.selected_memo_id = memo_id
        memo = get_memo(memo_id)
        if memo:
            _, _, t, b = memo
            self.edit_id.setText(f"選択: {memo_id}")
            self.edit_title.setText(t or "")
            self.edit_body.setPlainText(b or "")

    def on_save_selected(self):
        if not self.selected_memo_id:
            QMessageBox.information(self, "情報", "編集するメモを選択してください。")
            return

        title = self.edit_title.text().strip()
        body = self.edit_body.toPlainText()
        if not title:
            QMessageBox.warning(self, "入力エラー", "メモタイトルは必須です。")
            return

        update_memo(self.selected_memo_id, title, body)
        self.reload()
        self.statusBar().showMessage("メモを保存しました", 1200)
        if self.on_changed:
            self.on_changed()