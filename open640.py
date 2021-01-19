#!/usr/bin/env python3
import sys

from PyQt5.QtWidgets import QApplication

from main_window import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow()
    sys.exit(app.exec_())
