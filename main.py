import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from db import init_db
from ui_list import ListView
from ui_page import PageView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CppMemo")
        self.resize(900, 650)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.list_view = ListView(
            on_open_page=self.open_page,
        )
        self.page_view = PageView(
            on_back=self.back_to_list,
            on_changed=self.refresh_list,
        )

        self.stack.addWidget(self.list_view)  # index 0
        self.stack.addWidget(self.page_view)  # index 1
        self.stack.setCurrentWidget(self.list_view)

    def open_page(self, page_id: int):
        self.page_view.set_page(page_id)
        self.stack.setCurrentWidget(self.page_view)

    def back_to_list(self):
        self.list_view.reload()
        self.stack.setCurrentWidget(self.list_view)

    def refresh_list(self):
        # ページ側で追加/削除などしたら一覧も更新
        self.list_view.reload()

def main():
    init_db()
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()