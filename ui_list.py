from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt
from db import list_pages, create_page, delete_page

class ListView(QWidget):
    def __init__(self, on_open_page):
        super().__init__()
        self.on_open_page = on_open_page

        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        self.new_title = QLineEdit()
        self.new_title.setPlaceholderText("新規ページタイトル")
        self.create_btn = QPushButton("作成")
        self.create_btn.clicked.connect(self.on_create)
        self.reload_btn = QPushButton("更新")
        self.reload_btn.clicked.connect(self.reload)

        top.addWidget(self.new_title, 1)
        top.addWidget(self.create_btn)
        top.addWidget(self.reload_btn)
        layout.addLayout(top)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "タイトル", "更新日時", "メモ数", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setColumnHidden(0, True)
        self.table.cellDoubleClicked.connect(self.on_open_by_doubleclick)
        layout.addWidget(self.table, 1)

        self.reload()

    def reload(self):
        rows = list_pages()
        self.table.setRowCount(0)

        for r, (page_id, title, updated_at, memo_count) in enumerate(rows):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(page_id)))
            self.table.setItem(r, 1, QTableWidgetItem(title or ""))

            dt_text = updated_at.strftime("%Y-%m-%d %H:%M:%S") if updated_at else ""
            it = QTableWidgetItem(dt_text)
            it.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(r, 2, it)

            it2 = QTableWidgetItem(str(memo_count))
            it2.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(r, 3, it2)

            del_btn = QPushButton("削除")
            del_btn.clicked.connect(lambda _, pid=page_id: self.on_delete(pid))
            self.table.setCellWidget(r, 4, del_btn)

    def on_create(self):
        title = self.new_title.text().strip()
        if not title:
            QMessageBox.warning(self, "入力エラー", "タイトルを入力してください。")
            return
        page_id = create_page(title)
        self.new_title.clear()
        self.reload()
        self.on_open_page(page_id)  # 作ったらそのまま遷移

    def on_delete(self, page_id: int):
        ret = QMessageBox.question(self, "確認", "このページを削除しますか？（中のメモも消えます）")
        if ret == QMessageBox.Yes:
            delete_page(page_id)
            self.reload()

    def on_open_by_doubleclick(self, row: int, col: int):
        page_id = int(self.table.item(row, 0).text())
        self.on_open_page(page_id)