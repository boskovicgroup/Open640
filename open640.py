#!/usr/bin/env python3

import sys

from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QMessageBox
from PyQt5.QtWidgets import QApplication, QPlainTextEdit, QFileDialog
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import QSize

from settings_class import SettingsWindow
from serial_reader import Reader
from open640_class import Open640


class MainWindow(QWidget, Open640):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.collecting = False
        self.title = 'Open640'
        self.width = 800
        self.height = 600
        self.setMinimumSize(QSize(320, 240))
        self.initMainWindow()

    def initMainWindow(self):
        self.setWindowTitle(self.title)
        layout = QGridLayout()
        layout.setSpacing(10)
        self.setLayout(layout)

        # Widgets
        self.dataArea = QPlainTextEdit()
        self.dataArea.setReadOnly(True)
        self.dataArea.setPlaceholderText("Collected data will appear here for"
                                         + " review before it is written to"
                                         + " disk.")

        self.settingsButton = QPushButton('Serial Settings', self)
        self.settingsButton.setToolTip('Change serial port settings.')

        self.checkSettingsButton = QPushButton('Dump Settings', self)
        self.settingsButton.setToolTip(
            "Print the current settings to the screen."
        )

        self.writeButton = QPushButton('Write to File', self)
        self.writeButton.setToolTip('Write colected data to the disk.')

        self.clearButton = QPushButton('Clear Output', self)
        self.collectToggle = QPushButton('Start Collection', self)

        self.settingsButton.clicked.connect(
            lambda: self.onSettingsButtonClicked()
        )
        self.checkSettingsButton.clicked.connect(
            lambda: self.onCheckButtonClicked()
        )
        self.collectToggle.clicked.connect(lambda: self.onStartButtonClicked())
        self.writeButton.clicked.connect(lambda: self.onWriteButtonClicked())
        self.clearButton.clicked.connect(lambda: self.onClearOutputClicked())

        layout.addWidget(self.dataArea, 0, 0, 1, 0)
        layout.addWidget(self.settingsButton, 1, 0)
        layout.addWidget(self.checkSettingsButton, 1, 1)
        layout.addWidget(self.clearButton, 1, 2)
        layout.addWidget(self.collectToggle, 1, 3)
        layout.addWidget(self.writeButton, 1, 4)

        self.show()

    def onStartButtonClicked(self):
        if not self.collecting:
            self.collectToggle.setText('Stop Collection')
            self.collecting = True
            self.dataArea.setPlainText(
                "Waiting for data from the DU-640...\n"
                + "If stopped, the DU-640's send queue will be emptied before"
                + "reading is terminated. Data collected will be trashed.")
            self.warningCleared = False
            self.reader = Reader()
            self.reader.experimental_data.connect(self.onExperimentFinished)
            self.reader.data_live.connect(self.onExperimentUpdate)
            self.reader.success_state.connect(self.onExperimentSuccess)
            self.reader.fail_state.connect(self.onExperimentFailed)
            self.reader.start()
        else:
            # Kill the currently running thread
            alert = QMessageBox()
            alert.setText(
                "Won't start another read thread until current one finishes."
            )
            alert.exec_()

    def onExperimentFailed(self):
        self.collecting = False
        self.collectToggle.setText('Start Collection')
        alert = QMessageBox()
        alert.setText("Could not open serial port."
                      + "Ensure /dev/ttyAMA0 exists and is available, then try"
                      + " again.")
        alert.exec_()

    def onExperimentUpdate(self, data):
        if not self.warningCleared:
            self.dataArea.setPlainText("")
            self.warningCleared = True
        cursor = self.dataArea.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(data)
        self.dataArea.ensureCursorVisible()

    def onExperimentFinished(self, data):
        self.dataArea.setPlainText(data)
        self.collecting = False
        self.collectToggle.setText('Start Collection')

    def onExperimentSuccess(self):
        self.collecting = False
        self.collectToggle.setText('Start Collection')

    def onClearOutputClicked(self):
        self.dataArea.setPlainText("")

    def onWriteButtonClicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "QFileDialog.getSaveFileName()",
            "",
            "Text Files (*.txt)",
            options=options)
        if filename:
            print("Saving to " + filename + ".txt...")
            f = open(filename + '.txt', 'w')
            f.write(self.dataArea.toPlainText() + '\n')
            f.close()

    def onSettingsButtonClicked(self):
        dlg = SettingsWindow()
        dlg.exec_()

    def onCheckButtonClicked(self):
        self.dataArea.setPlainText(
            "Current Settings:"
            + "\n\tPort: " + self.settings.value("serial/port")
            + "\n\tBaudrate: " + str(self.settings.value("serial/baudrate"))
            + "\n\tBytesize: "
            + str(self.settings.value("serial/bytesize")) + " bits"
            + "\n\tParity: " + self.settings.value("serial/parity")
            + "\n\tStop Bits: " + str(self.settings.value("serial/stopbits"))
            + "\n\tFlow Control: " + str(self.settings.value("serial/xonxoff"))
            + "\n\nRemember that settings are persistent."
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow()
    sys.exit(app.exec_())
