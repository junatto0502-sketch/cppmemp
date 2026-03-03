import sys
from PySide6.QtWidgets import QApplication
from db import init_db
from ui_list import ListWindow

def main():
    init_db()
    app = QApplication(sys.argv)
    w = ListWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()