from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton
from PyQt5.QtWidgets import QGridLayout, QMessageBox, QCheckBox
from open640_class import Open640


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
