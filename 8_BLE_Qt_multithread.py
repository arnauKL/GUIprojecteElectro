import sys
import asyncio
import struct
from collections import deque

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QThread, Signal

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from bleak import BleakClient, BleakError

# BLE configs
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
ADDRESS = "D8:13:2A:73:1C:8A"   # ESP ARNAU

# =========================
# THREAD BLE
# =========================
class BLEThread(QThread):
    new_data = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)  # vincula el thread al parent (MainWindow) xq no salti error dient que s'ha perdut
        self._loop = None
        self._client = None
        self._running = True

    def run(self):
        asyncio.run(self._run_ble())  # Crea nou event loop per a aquest fil

    async def _run_ble(self):
        try:
            self._client = BleakClient(ADDRESS)
            await self._client.connect()
            print("Connectat al dispositiu BLE!")

            await self._client.start_notify(CHARACTERISTIC_UUID, self.notification_handler)

            while self._running:
                await asyncio.sleep(0.1)  # Manté el loop viu

            await self._client.stop_notify(CHARACTERISTIC_UUID)
            await self._client.disconnect()
            print("Desconnectat BLE.")

        except BleakError as e:
            print(f"Error BLE: {e}")

    def notification_handler(self, sender, data):
        try:
            [value] = struct.unpack('f', data)
            self.new_data.emit(value)
        except Exception as e:
            print(f"Error convertint la dada: {e}")

    def stop(self):
        self._running = False


# =========================
# CANVAS Matplotlib
# =========================
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


# =========================
# FINESTRA PRINCIPAL
# =========================
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Visualització ECG via BLE")

        # Dades
        self.buffer_size = 500
        self.xdata = list(range(self.buffer_size))
        self.ydata = deque([0.0]*self.buffer_size, maxlen=self.buffer_size) # Inicia buffer a zeros 

        # Canvas
        self.canvas = MplCanvas(self, width=6, height=4, dpi=100)
        self.setCentralWidget(self.canvas)
        self._plot_ref = self.canvas.axes.plot(self.xdata, self.ydata, 'r')[0]

        self.canvas.axes.set_ylim(-1, 1.5)
        self.canvas.axes.set_title("ECG BLE")
        self.canvas.axes.set_xlabel("Temps")
        self.canvas.axes.set_ylabel("Amplitud") # Inicia buffer a zeros 

        # Timer per actualitzar el plot
        self.plot_timer = QtCore.QTimer()
        self.plot_timer.setInterval(30)
        self.plot_timer.timeout.connect(self.update_plot)
        self.plot_timer.start()

        # BLE thread
        self.ble_thread = BLEThread(self)  # passa 'self' com a parent x mantenir viu el thread

        self.ble_thread.new_data.connect(self.receive_data)
        self.ble_thread.start()

        self.show()

    def receive_data(self, value):
        self.ydata.append(value)

    def update_plot(self):
        self._plot_ref.set_ydata(self.ydata)
        self.canvas.draw()

    def closeEvent(self, event):
        self.ble_thread.stop()
        self.ble_thread.wait()
        event.accept()


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec()