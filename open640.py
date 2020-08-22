#!/usr/bin/env python3

import sys
import os
import platform
import serial
import time
import configparser
import xdg

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Open640:
    def __init__(self):
        # Only write a new settings file if one does not exist. In this case,
        # checking for a particular setting is equivalent to checking for the
        # file itself.
        if not settings.contains("serial/xonxoff"):
            self.registerDefaultSettings()

    def registerDefaultSettings(self):
        settings.beginGroup("serial")
        settings.setValue("port", "/dev/ttyAMA0")
        settings.setValue("baudrate", 9600)
        settings.setValue("bytesize", serial.SEVENBITS)
        settings.setValue("parity", serial.PARITY_EVEN)
        settings.setValue("stopbits", serial.STOPBITS_ONE)
        settings.setValue("xonxoff", True)
        settings.endGroup()
        settings.setValue("app/autoclear", False)

    def validateByteSize(self, bits):
        if (bits == 5):
            return serial.FIVEBITS
        if (bits == 6):
            return serial.SIXBITS
        if (bits == 7):
            return serial.SEVENBITS
        if (bits == 8):
            return serial.EIGHTBITS
        raise ValueError("Bytesize must be in the range [5, 8]")

    def validateParity(self, parity):
        parity = parity.lower()
        if (parity == 'e' or parity == 'even'):
            return serial.PARITY_EVEN
        if (parity == 'o' or parity == 'odd'):
            return serial.PARITY_ODD
        if (parity == 'm' or parity == 'mark'):
            return serial.PARITY_MARK
        if (parity == 's' or parity == 'space'):
            return serial.PARITY_SPACE
        if (parity == 'n' or parity == 'none'):
            return serial.PARITY_NONE
        raise ValueError("Parity must be one of: even, odd, mark, space, or none")

    def validateParityTextBox(self, parity):
        if (parity == 'E'):
            return "Even"
        if (parity == 'O'):
            return "Odd"
        if (parity == 'M'):
            return "Mark"
        if (parity == 'S'):
            return "Space"
        if (parity == 'N'):
            return "None"

    def validateStopBits(self, bits):
        if (bits == 1):
            return serial.STOPBITS_ONE
        if (bits == 1.5):
            return serial.STOPBITS_ONE_POINT_FIVE
        if (bits == 2):
            return serial.STOPBITS_TWO
        raise ValueError("Stopbits must be 1, 1.5, or 2. We don't know what 1.5 means either.")


class Reader(QThread):
    experimental_data = pyqtSignal(object)
    fail_state = pyqtSignal(object)
    data_live = pyqtSignal(object)
    success_state = pyqtSignal(object)
    ser = None

    def __init__(self):
        super(Reader, self).__init__()

    @pyqtSlot()
    def run(self):
        print("Thread start.")
        self.collectData()
        self.success_state.emit(None)
        print("Thread end.")

    def LiveUpdateTest(self):
        for character in "This is the test string for the live updating data feature.":
            time.sleep(0.05)

    def collectData(self):
        try:
            print("Entered collection method.")
            # For the purposes of testing multithreading, these are fixed in place.
            self.ser = serial.Serial(
                "/dev/ttyAMA0",
                baudrate=9600,
                bytesize=serial.SEVENBITS,
                parity=serial.PARITY_EVEN,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=True)
            # Dodgy reimplementation of do-while by copying code
            raw_data = self.ser.read(1)
            data_str = raw_data.decode('ascii')
            print(raw_data.decode('ascii'))
            print("Waiting: " + str(self.ser.inWaiting()))
            time.sleep(0.01)
            data_str = ""
            clk = 0
            while True:
                if (self.ser.inWaiting() > 0):
                    raw_data = self.ser.read(1)
                    data_str = data_str + raw_data.decode('ascii')
                    print("Waiting: " + str(self.ser.inWaiting()))
                    clk = (clk + 1) // 5
                    if not clk:
                        self.data_live.emit(data_str)
                        data_str = ""
                    time.sleep(0.0007)
                else:
                    break
            self.data_live.emit(data_str)
            self.ser.close()
            self.ser = None
        except serial.SerialException:
            self.fail_state.emit(None)

    def stop(self):
        # Trash Serial Connection
        if self.ser is not None:
            # Ensure the DU-640's outgoing queue is empty so that it doesn't
            # jam itself.
            while (self.ser.inWaiting() > 0):
                self.ser.read(1)
            ser.close()
        self.threadactive = False
        self.wait()


class SettingsWindow(QDialog, Open640):
    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.width = 400
        self.height = 300
        self.setMinimumSize(QSize(320, 240))
        self.initSettingsWindow()

    def initSettingsWindow(self):
        self.setWindowTitle('Open640 - Settings')
        layout = QGridLayout(self)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.portLabel = QLabel("Port")
        self.baudLabel = QLabel("Baudrate")
        self.byteLabel = QLabel("Byte Size")
        self.parityLabel = QLabel("Parity")
        self.stopLabel = QLabel("Stop Bits")

        self.portBox = QLineEdit(self)
        self.portBox.setText(settings.value("serial/port"))
        self.portBox.setToolTip("The address of the port that will be used for communication.")

        self.baudrateBox = QLineEdit(self)
        self.baudrateBox.setText(str(settings.value("serial/baudrate")))
        self.baudrateBox.setToolTip("Communications speed; this must match the setting on the DU-640.")

        self.byteBox = QLineEdit(self)
        self.byteBox.setText(str(settings.value("serial/bytesize")))
        self.byteBox.setToolTip("Size of incoming data, in bits. This must match the setting on the DU-640.")

        self.parityBox = QLineEdit(self)
        self.parityBox.setText(self.validateParityTextBox(str(settings.value("serial/parity"))))
        self.parityBox.setToolTip(
            "Parity checking type. Can be even, odd, or none. This must match the setting on the DU-640.")

        self.stopBox = QLineEdit(self)
        self.stopBox.setText(str(settings.value("serial/stopbits")))
        self.stopBox.setToolTip("Number of stop bits. Can be 1, 1.5, or 2. This must match the setting on the DU-640.")

        self.fcButton = QCheckBox(self)
        self.fcButton.setText("Software Flow Control")
        self.fcButton.setChecked(True if settings.value("serial/xonxoff") == 'true' else False)
        self.fcButton.setToolTip(
            "Enable or disable flow control to control DU-640 from a computer. This must match the setting on the DU-640.")

        self.autoclearButton = QCheckBox(self)
        self.autoclearButton.setChecked(True if settings.value("app/autoclear") == 'true' else False)
        self.autoclearButton.setText("Autoclear output on save")

        self.saveButton = QPushButton('Save Changes')

        self.closeButton = QPushButton('Close Dialog')

        self.saveButton.clicked.connect(lambda: self.onSaveButtonClicked())
        self.closeButton.clicked.connect(lambda: self.onCloseButtonClicked())

        row1 = [self.portLabel, self.baudLabel, self.byteLabel, self.parityLabel]
        row2 = [self.portBox, self.baudrateBox, self.byteBox, self.parityBox]
        row4 = [self.stopBox, self.fcButton, self.autoclearButton]
        for index, row in enumerate([row1, row2]):
            for entry in zip(row, range(0, 4)):
                layout.addWidget(entry[0], index, entry[1])
        layout.addWidget(self.stopLabel, 2, 0)
        for entry in zip(row4, range(0, 3)):
            layout.addWidget(entry[0], 3, entry[1])
        layout.addWidget(self.closeButton, 4, 2)
        layout.addWidget(self.saveButton, 4, 3)

        self.show()

    def onCloseButtonClicked(self):
        self.close()

    def onSaveButtonClicked(self):
        try:
            localBytesize = self.validateByteSize(int(self.byteBox.text()))
            localParity = self.validateParity(self.parityBox.text())
            localStopbits = self.validateStopBits(float(self.stopBox.text()))
            du640_baudrates = [4800, 9600, 19200]
            if int(self.baudrateBox.text()) not in du640_baudrates:
                raise ValueError("Baudrate must be one of 4800, 9600, 19200")
        except ValueError as e:
            alert = QMessageBox()
            alert.setText(
                "There is something wrong with your settings, and they have not yet been committed.\n\nError: " + str(
                    e))
            alert.exec_()
            return

        settings.beginGroup("serial")
        settings.setValue("port", self.portBox.text())
        settings.setValue("baudrate", int(self.baudrateBox.text()))
        settings.setValue("bytesize", localBytesize)
        settings.setValue("parity", localParity)
        settings.setValue("stopbits", localStopbits)
        settings.setValue("xonxoff", self.fcButton.isChecked())
        settings.endGroup()
        settings.setValue("app/autoclear", self.autoclearButton.isChecked())
        self.close()


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
        self.dataArea.setPlaceholderText("Collected data will appear here for review before it is written to disk.")

        self.settingsButton = QPushButton('Serial Settings', self)
        self.settingsButton.setToolTip('Change serial port settings.')

        self.checkSettingsButton = QPushButton('Dump Settings', self)
        self.settingsButton.setToolTip('Print the current settings to the screen.')

        self.writeButton = QPushButton('Write to File', self)
        self.writeButton.setToolTip('Write colected data to the disk.')

        self.clearButton = QPushButton('Clear Output', self)
        self.collectToggle = QPushButton('Start Collection', self)

        self.settingsButton.clicked.connect(lambda: self.onSettingsButtonClicked())
        self.checkSettingsButton.clicked.connect(lambda: self.onCheckButtonClicked())
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
                "Waiting for data from the DU-640...\nIf stopped, the DU-640's send queue will be emptied before reading is terminated. Data collected will be trashed.")
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
            alert.setText('Won\'t start another read thread until current thread finishes.')
            alert.exec_()

    def onExperimentFailed(self):
        self.collecting = False
        self.collectToggle.setText('Start Collection')
        alert = QMessageBox()
        alert.setText('Could not open serial port. Ensure /dev/ttyAMA0 exists and is available, then try again.')
        alert.exec_()

    def onExperimentUpdate(self, data):
        if not self.warningCleared:
            self.dataArea.setPlainText("")
            self.warningCleared = True
        cursor = self.dataArea.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(data)

        #self.dataArea.setPlainText(self.dataArea.toPlainText() + data)
        #self.dataArea.setCenterOnScroll(True)
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
            "Current Settings:" +
            "\n\tPort: " + settings.value("serial/port") +
            "\n\tBaudrate: " + str(settings.value("serial/baudrate")) +
            "\n\tBytesize: " + str(settings.value("serial/bytesize")) + " bits"
                                                                        "\n\tParity: " + settings.value(
                "serial/parity") +
            "\n\tStop Bits: " + str(settings.value("serial/stopbits")) +
            "\n\tFlow Control: " + str(settings.value("serial/xonxoff")) +
            "\n\nRemember that settings are persistent."
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    orgName = "boskoviclab.ku.edu" if sys.platform.startswith('darwin') else "BoskovicGroup"
    settings = QSettings(orgName, "Open640")
    MainWindow()
    sys.exit(app.exec_())
