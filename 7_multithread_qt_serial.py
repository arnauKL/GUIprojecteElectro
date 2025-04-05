import sys
import serial
from collections import deque

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QThread, Signal

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# =========================
# THREAD: Lectura del port sèrie
# =========================
class SerialReaderThread(QThread):
    new_data = Signal(float)

    def __init__(self, port='COM3', baudrate=115200):
        super().__init__()
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.running = True

    def run(self):
        while self.running:
            try:
                line = self.ser.readline().decode().strip()
                if line:
                    value = float(line)
                    self.new_data.emit(value)
            except Exception as e:
                print(f"Error llegint del port sèrie: {e}")

    def stop(self):
        self.running = False
        self.ser.close()


# =========================
# CANVAS de matplotlib
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

        self.setWindowTitle("Visualització ECG en temps real")

        # ---------- Dades ----------
        self.buffer_size = 1000     # 1000 dadess
        self.xdata = list(range(self.buffer_size))
        self.ydata = deque([0.0]*self.buffer_size, maxlen=self.buffer_size)

        # ---------- Gràfic ----------
        self.canvas = MplCanvas(self, width=6, height=4, dpi=100)
        self.setCentralWidget(self.canvas)
        self._plot_ref = self.canvas.axes.plot(self.xdata, self.ydata, 'r')[0]

        self.canvas.axes.set_ylim(-1, 1.5)
        self.canvas.axes.set_title("ECG en temps real")
        self.canvas.axes.set_xlabel("Temps (samples)")
        self.canvas.axes.set_ylabel("Amplitud")

        # ---------- Timer per redibuixar ----------
        self.plot_timer = QtCore.QTimer()
        self.plot_timer.setInterval(30)  # 30 ms ≈ 33 FPS
        self.plot_timer.timeout.connect(self.update_plot)
        self.plot_timer.start()

        # ---------- Thread de lectura sèrie ----------
        self.reader_thread = SerialReaderThread(port='COM3', baudrate=115200)
        self.reader_thread.new_data.connect(self.receive_data)
        self.reader_thread.start()

        self.show()

    def receive_data(self, value):
        # Quan arriba una nova dada del fil, actualitza el buffer
        self.ydata.append(value)

    def update_plot(self):
        self._plot_ref.set_ydata(self.ydata)
        self.canvas.draw()

    def closeEvent(self, event):
        # Aturar el fil de lectura quan tanquem
        self.reader_thread.stop()
        self.reader_thread.wait()
        event.accept()


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec()