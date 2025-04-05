import sys
import struct
import asyncio
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QThread, Signal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from bleak import BleakClient, BleakError

# BLE
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
ADDRESS = "D8:13:2A:73:1C:8A"   # ESP ARNAU
N_DADES = 1000

# ──────────────────────────────── Canvas de matplotlib ────────────────────────────────
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


# ──────────────────────────────── Thread per BLE ────────────────────────────────
class BLEThread(QThread):
    new_data = Signal(float)
    connected = Signal()
    error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True

    def run(self):
        asyncio.run(self.ble_loop())

    async def ble_loop(self):
        try:
            async with BleakClient(ADDRESS) as client:
                await client.start_notify(CHARACTERISTIC_UUID, self.notification_handler)
                self.connected.emit()

                while self._running:
                    await asyncio.sleep(0.1)
        except BleakError as e:
            self.error.emit(str(e))

    def notification_handler(self, sender, data):
        [value] = struct.unpack('f', data)
        self.new_data.emit(value)

    def stop(self):
        self._running = False


# ──────────────────────────────── Finestra principal ────────────────────────────────
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)

        # Dades
        self.xdata = list(range(N_DADES))
        self.ydata = [0] * N_DADES
        self._plot_ref = None
        self.latest_value = 0.0
        self.ble_thread = None  # Inicialitzem com None

        # Labels i botó
        self.label_dada = QtWidgets.QLabel("Última dada: --")
        self.label_connexio = QtWidgets.QLabel("Connexió: --")
        self.boto_connectar = QtWidgets.QPushButton("Connectar")

        self.label_dada.setStyleSheet("font-size: 14px")
        self.label_connexio.setStyleSheet("font-size: 14px")
        self.boto_connectar.clicked.connect(self.iniciar_connexio)

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.label_dada)
        layout.addWidget(self.label_connexio)
        layout.addWidget(self.boto_connectar)

        central = QtWidgets.QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.setWindowTitle("Monitor ECG via BLE")

        # Timer per refrescar el gràfic
        self.timer = QtCore.QTimer()
        self.timer.setInterval(30)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def iniciar_connexio(self):
        # Evita múltiples connexions simultànies
        if self.ble_thread and self.ble_thread.isRunning():
            self.label_connexio.setText("Ja connectat o en procés...")
            return

        self.label_connexio.setText("Intentant connectar...")
        self.label_connexio.setStyleSheet("font-size: 14px; color: white")

        self.ble_thread = BLEThread(self)
        self.ble_thread.new_data.connect(self.receive_data)
        self.ble_thread.connected.connect(self.on_connected)
        self.ble_thread.error.connect(self.on_error)
        self.ble_thread.start()

    def receive_data(self, value):
        self.latest_value = value
        self.label_dada.setText(f"Última dada: {value:.2f}")
        self.ydata = self.ydata[1:] + [value]

    def on_connected(self):
        self.label_connexio.setText("Connexió: Connectat")
        self.label_connexio.setStyleSheet("font-size: 14px; color: green")

    def on_error(self, msg):
        self.label_connexio.setText(f"Connexió: Error\n{msg}")
        self.label_connexio.setStyleSheet("font-size: 14px; color: red")
        self.ble_thread = None  # x permetre nous intents

    def update_plot(self):
        if self._plot_ref is None:
            plot_refs = self.canvas.axes.plot(self.xdata, self.ydata, 'r')
            self._plot_ref = plot_refs[0]
        else:
            self._plot_ref.set_ydata(self.ydata)
        self.canvas.axes.set_ylim(-1, 1.5)
        self.canvas.draw()

    def closeEvent(self, event):
        if self.ble_thread:
            self.ble_thread.stop()
            self.ble_thread.quit()
            self.ble_thread.wait()
        event.accept()

# ──────────────────────────────── Execució ────────────────────────────────
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())