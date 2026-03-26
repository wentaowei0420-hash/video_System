import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from video_app.frontend.window import MainWindow
from video_system_settings import ensure_runtime_directories


def main():
    ensure_runtime_directories()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Microsoft YaHei UI", 9))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
