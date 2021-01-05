from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton
from PyQt5.QtCore import QSize


class BatchWindow(QWidget):
    def __init__(self):
        super(BatchWindow, self).__init__()
        self.title = "Open640 - Batch Collector"
        self.setWindowTitle(self.title)
        self.width = 800
        self.height = 600
        self.setMinimumSize(QSize(320, 240))
        self.initLayout()

    def initLayout(self):
        layout = QGridLayout()
        layout.setSpacing(10)
        self.setLayout(layout)

        self.startButton = QPushButton('Start Collection')
        self.startButton.setToolTip('Begin a batch collection.')

        self.startButton.clicked.connect(lambda: self.onStartButtonClicked())

        layout.addWidget(self.startButton, 0, 0, 1, 0)

    def onStartButtonClicked(self):
        pass

    def onNextButtonClicked(self):
        pass

    def onCloseButtonClicked(self):
        pass
