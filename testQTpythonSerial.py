import sys
import serial
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QThread, pyqtSignal

# Serial Reader Thread
class SerialThread(QThread):
    data_received = pyqtSignal(float)

    def run(self):
        ser = serial.Serial('COM3', 115200)
        while True:
            try:
                line = ser.readline().decode().strip()
                value = float(line)
                self.data_received.emit(value)
            except ValueError:
                continue

# Main Window
class SerialPlotter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ESP32 Serial Data")
        self.setGeometry(100, 100, 800, 600)

        # Widgets
        self.plot_widget1 = pg.PlotWidget()
        self.plot_widget2 = pg.PlotWidget()
        self.label = QLabel("Waiting for data...")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget1)
        layout.addWidget(self.plot_widget2)
        layout.addWidget(self.label)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Data Storage
        self.data1 = []
        self.data2 = []
        self.max_points = 100

        # Start Serial Thread
        self.thread = SerialThread()
        self.thread.data_received.connect(self.update_plot)
        self.thread.start()

    def update_plot(self, value):
        # Update data lists
        self.data1.append(value)
        self.data2.append(value * 0.5)  # Example: Second plot with transformed data
        if len(self.data1) > self.max_points:
            self.data1.pop(0)
            self.data2.pop(0)

        # Update plots
        self.plot_widget1.plot(self.data1, clear=True, pen='r')
        self.plot_widget2.plot(self.data2, clear=True, pen='b')

        # Update label
        self.label.setText(f"Latest Value: {value:.2f}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SerialPlotter()
    window.show()
    sys.exit(app.exec())
