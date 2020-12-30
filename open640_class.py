import serial
import sys
from PyQt5.QtCore import QSettings


class Open640:
    def __init__(self):
        # Only write a new settings file if one does not exist. In this case,
        # checking for a particular setting is equivalent to checking for the
        # file itself.
        orgName = None
        if sys.platform.startswith('darwin'):
            orgName = "boskoviclab.ku.edu"
        else:
            orgName = "BoskovicGroup"
        settings = QSettings(orgName, "Open640")
        if not settings.contains("serial/xonxoff"):
            self.registerDefaultSettings()

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
