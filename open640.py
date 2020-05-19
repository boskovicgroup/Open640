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
        # Only write a new settings file if one does not exist
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


class SettingsWindow(Open640):
    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.title = 'Open640 - Settings'
        self.width = 400
        self.height = 300
        self.setMinimumSize(QSize(100,100))
        self.initMainWindow()
        pass

class MainWindow(QWidget, Open640):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.title = 'Open640'
        self.width = 800
        self.height = 600
        self.setMinimumSize(QSize(320,240))
        self.initMainWindow()

    def initMainWindow(self):
        self.setWindowTitle(self.title)
        layout = QGridLayout()
        layout.setSpacing(10)
        self.setLayout(layout)

        # Widgets
        dataArea = QPlainTextEdit()
        dataArea.setReadOnly(True)
        dataArea.setPlaceholderText("Collected data will appear here for review before it is written to disk.")

        settingsButton = QPushButton('Serial Settings', self)
        settingsButton.setToolTip('Change serial port settings.')

        checkSettingsButton = QPushButton('Dump Settings', self)
        settingsButton.setToolTip('Print the current settings to the screen.')

        writeButton = QPushButton('Write to File', self)
        writeButton.setToolTip('Write colected data to the disk.')

        clearButton = QPushButton('Clear Output', self)
        collectToggle = QPushButton('Start Collection', self)

        settingsButton.clicked.connect(lambda: self.onSettingsButtonClicked())
        checkSettingsButton.clicked.connect(lambda: self.onCheckButtonClicked(dataArea))
        collectToggle.clicked.connect(lambda: self.onStartButtonClicked(dataArea))
        writeButton.clicked.connect(lambda: self.onWriteButtonClicked(dataArea))
        clearButton.clicked.connect(lambda: self.onClearOutputClicked(dataArea))

        layout.addWidget(dataArea, 0, 0, 1, 0)
        layout.addWidget(settingsButton, 1, 0)
        layout.addWidget(checkSettingsButton, 1, 1)
        layout.addWidget(clearButton, 1, 2)
        layout.addWidget(collectToggle, 1, 3)
        layout.addWidget(writeButton, 1, 4)

        self.show()

    def collectData():
        self.currently_collecting = True
        try:
            ser = serial.Serial( 
                    settings.value("serial/port"),
                    baudrate = settings.value("serial/baudrate"),
                    bytesize = settings.value("serial/bytesize"),
                    parity = settings.value("serial/parity"),
                    stopbits = settings.value("serial/stopbits"),
                    xonxoff = settings.value("serial/xonxoff"))
            data = ser.read(1)
            output.setPlainText(output.toPlainText() + data_str.decode('ascii'))
        except serial.SerialException:
            alert = QMessageBox()
            alert.setText('Could not open serial port. Ensure /dev/ttyAMA0 exists and is available, then try again.')
            alert.exec_()
        return

    def onStartButtonClicked(self, output):
        sender = self.sender()
        if not self.currently_collecting:
            print("1")
            self.currently_collecting = True
            try:
                ser = serial.Serial(
                        settings.value("serial/port"),
                        baudrate = settings.value("serial/baudrate"),
                        bytesize = settings.value("serial/bytesize"),
                        parity = settings.value("serial/parity"),
                        stopbits = settings.value("serial/stopbits"),
                        xonxoff = settings.value("serial/xonxoff"))
                print("2")
                sender.setText('Stop Collection')
                # Dodgy reimplementation of do-while by copying code
                data_str = ser.read(1)
                print(len(data_str))
                print(data_str.decode('ascii'))
                output.setPlainText(output.toPlainText() + data_str.decode('ascii'))
                print(output.toPlainText())
                print("Waiting: " + str(ser.inWaiting()))
                time.sleep(0.01)  
                while True:
                    if(ser.inWaiting() > 0):
                        data_str = ser.read(1)
                        output.setPlainText(output.toPlainText() + data_str.decode('ascii'))
                        print(output.toPlainText())
                        print("Waiting: " + str(ser.inWaiting()))
                    else: 
                        break
                print("5")
                self.currently_collecting = False
                sender.setText('Start Collection') 
            except serial.SerialException:
                alert = QMessageBox()
                alert.setText('Could not open serial port. Ensure /dev/ttyAMA0 exists and is available, then try again.')
                alert.exec_()
        else: 
            self.currently_collecting = False
            try:
                if ser is not None:
                    ser.close()
                    sender.setText('Start Collection')
            except UnboundLocalError:
                print('Tried to close an unopened serial connection')

    def onClearOutputClicked(self, widget):
        widget.setPlainText("")

    def onWriteButtonClicked(self, widget):
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
            f.write(widget.toPlainText())
            f.close()

    def onSettingsButtonClicked(self): 
        pass

    def onCheckButtonClicked(self, output):
        output.setPlainText(
                "Current Settings:" +
                "\n\tPort: " + settings.value("serial/port") + 
                "\n\tBaudrate: " + str(settings.value("serial/baudrate")) +
                "\n\tBytesize: " + str(settings.value("serial/bytesize")) + " bits"
                "\n\tParity: " + settings.value("serial/parity") +
                "\n\tStop Bits: " + str(settings.value("serial/stopbits")) +
                "\n\tFlow Control: " + str(settings.value("serial/xonxoff"))
            "\n\nRemember that settings are persistent."
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    orgName = "boskoviclab.ku.edu" if sys.platform.startswith('darwin') else "BoskovicGroup"
    settings = QSettings(orgName, "Open640")
    MainWindow()
    sys.exit(app.exec_())
