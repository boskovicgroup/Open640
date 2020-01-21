#!/usr/bin/env python3

import sys
import platform
import serial
import time
import configparser
import xdg

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Open640(QWidget):
    currently_collecting = False
    ser = None

    def __init__(self):
        super(Open640, self).__init__()
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
        
        writeButton = QPushButton('Write to File', self)
        writeButton.setToolTip('Write colected data to the disk.')

        clearButton = QPushButton('Clear Output', self)
        collectToggle = QPushButton('Start Collection', self)

        collectToggle.clicked.connect(lambda: self.onStartButtonClicked(dataArea))
        writeButton.clicked.connect(lambda: self.onWriteButtonClicked(dataArea))
        clearButton.clicked.connect(lambda: self.onClearOutputClicked(dataArea))

        layout.addWidget(dataArea, 0, 0, 1, 0)
        layout.addWidget(settingsButton, 1, 0)
        layout.addWidget(clearButton, 1, 1)
        layout.addWidget(collectToggle, 1, 2)
        layout.addWidget(writeButton, 1, 3)

        self.show()

    def onStartButtonClicked(self, output):
        sender = self.sender()
        if not self.currently_collecting:
            print("1")
            self.currently_collecting = True
            try:
                ser = serial.Serial(
                        "/dev/ttyAMA0",
                        baudrate = 19200,
                        bytesize = serial.SEVENBITS,
                        parity = serial.PARITY_EVEN,
                        stopbits = serial.STOPBITS_ONE,
                        xonxoff = True)
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = Open640()
    sys.exit(app.exec_())
