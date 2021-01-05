import serial
import sys
from PyQt5.QtCore import QSize, QSettings, pyqtSignal
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton
from PyQt5.QtWidgets import QGridLayout, QMessageBox, QCheckBox


class SettingsWindow(QDialog):
    current_settings = pyqtSignal(object)

    def __init__(self):
        super(SettingsWindow, self).__init__()
        orgName = None
        if sys.platform.startswith('darwin'):
            orgName = "boskoviclab.ku.edu"
        else:
            orgName = "BoskovicGroup"
        self.settings = QSettings(orgName, "Open640")
        if not self.settings.contains("serial/xonxoff"):
            self.registerDefaultSettings()
        self.width = 400
        self.height = 300
        self.setMinimumSize(QSize(320, 240))
        self.initSettingsWindow()

    def emitCurrentSettings(self):
        self.current_settings.emit(
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

    def registerDefaultSettings(self):
        self.settings.beginGroup("serial")
        self.settings.setValue("port", "/dev/ttyAMA0")
        self.settings.setValue("baudrate", 9600)
        self.settings.setValue("bytesize", serial.SEVENBITS)
        self.settings.setValue("parity", serial.PARITY_EVEN)
        self.settings.setValue("stopbits", serial.STOPBITS_ONE)
        self.settings.setValue("xonxoff", True)
        self.settings.endGroup()
        self.settings.setValue("app/autoclear", False)

    def initSettingsWindow(self):
        self.setWindowTitle('Open640 - Settings')
        layout = QGridLayout(self)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.portLabel = QLabel("Port")
        self.baudLabel = QLabel("Baudrate")
        self.byteLabel = QLabel("Byte Size")
        self.parLabel = QLabel("Parity")
        self.stopLabel = QLabel("Stop Bits")

        self.portBox = QLineEdit(self)
        self.portBox.setText(self.settings.value("serial/port"))
        self.portBox.setToolTip(
            "The address of the port that will be used for communication."
        )

        self.baudrateBox = QLineEdit(self)
        self.baudrateBox.setText(str(self.settings.value("serial/baudrate")))
        self.baudrateBox.setToolTip("Communications speed; this "
                                    + "must match the setting on the DU-640.")

        self.byteBox = QLineEdit(self)
        self.byteBox.setText(str(self.settings.value("serial/bytesize")))
        self.byteBox.setToolTip("Size of incoming data, in bits."
                                + "This must match the setting on the DU-640.")

        self.parityBox = QLineEdit(self)
        self.parityBox.setText(
            self.validateParityTextBox(
                str(self.settings.value("serial/parity"))
            )
        )
        self.parityBox.setToolTip("Parity checking type. Can be even, odd, or"
                                  + "none. This must match the setting on the"
                                  + "DU-640.")

        self.stopBox = QLineEdit(self)
        self.stopBox.setText(str(self.settings.value("serial/stopbits")))
        self.stopBox.setToolTip("Number of stop bits. Can be 1, 1.5, or 2."
                                + "This must match the setting on the DU-640.")

        self.fcButton = QCheckBox(self)
        self.fcButton.setText("Software Flow Control")
        self.fcButton.setChecked(
            True if self.settings.value("serial/xonxoff") == 'true' else False
        )
        self.fcButton.setToolTip(
            "Enable or disable flow control to control DU-640 from a computer."
            + "This must match the setting on the DU-640.")

        self.autoclearButton = QCheckBox(self)
        self.autoclearButton.setChecked(
            True if self.settings.value("app/autoclear") == 'true' else False
        )
        self.autoclearButton.setText("Autoclear output on save")

        self.saveButton = QPushButton('Save Changes')

        self.closeButton = QPushButton('Close Dialog')

        self.saveButton.clicked.connect(lambda: self.onSaveButtonClicked())
        self.closeButton.clicked.connect(lambda: self.onCloseButtonClicked())

        row1 = [self.portLabel, self.baudLabel, self.byteLabel, self.parLabel]
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
                "There is something wrong with your settings, and they have"
                "not yet been committed.\n\nError: " + str(e)
            )
            alert.exec_()
            return

        self.settings.beginGroup("serial")
        self.settings.setValue("port", self.portBox.text())
        self.settings.setValue("baudrate", int(self.baudrateBox.text()))
        self.settings.setValue("bytesize", localBytesize)
        self.settings.setValue("parity", localParity)
        self.settings.setValue("stopbits", localStopbits)
        self.settings.setValue("xonxoff", self.fcButton.isChecked())
        self.settings.endGroup()
        self.settings.setValue(
            "app/autoclear", self.autoclearButton.isChecked()
        )
        self.close()

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
        raise ValueError("Parity must be one of:"
                         + "even, odd, mark, space, or none")

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
        raise ValueError("Stopbits must be 1, 1.5, or 2."
                         + "We don't know what 1.5 means either.")
