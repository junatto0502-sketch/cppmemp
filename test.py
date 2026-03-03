import PySide6
from PySide6 import QtCore
from PySide6 import QtWidgets
import os
import sys

# 環境変数にPySide6を登録
dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

# とりあえずウィンドウと文字を表示
app = QtWidgets.QApplication()
label = QtWidgets.QLabel("こんにちは。", alignment=QtCore.Qt.AlignCenter)
label.setStyleSheet("font-size: 128px;")
label.show()
sys.exit(app.exec())
