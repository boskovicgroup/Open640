from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QSize


class BatchWindow(QWidget):
    def __init__(self):
        super(BatchWindow, self).__init__()
        self.title = "Open640 - Batch Collector"
        self.width = 800
        self.height = 600
        self.setMinimumSize(QSize(320, 240))
        self.initLayout()

    def initLayout(self):
        pass

    def onStartButtonClicked(self):
        pass

    def onNextButtonClicked(self):
        pass

    def onCloseButtonClicked(self):
        pass
