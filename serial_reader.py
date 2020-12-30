import serial
import time
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot


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
        self.LiveUpdateTest()
        self.success_state.emit(None)
        print("Thread end.")

    def LiveUpdateTest(self):
        for character in "This is the test string for the live updating data feature.":
            self.data_live.emit(character)
            time.sleep(0.05)

    def collectData(self):
        try:
            print("Entered collection method.")
            # For the purposes of testing multithreading,
            # these are fixed in place.
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
            self.ser.close()
        self.threadactive = False
        self.wait()
