from PySide6 import QtCore, QtWidgets
from canvas import MplCanvas
from BLE import BLEThread
from config import N_DADES

class MainWindow(QtWidgets.QMainWindow):
# Classe que guarda la finestra

    def __init__(self):
        super().__init__()

        # UI de matplotlib (per ara només 1 per l'ECG)
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)

        # Dades (faltarà posar les de respiració i activació de simpàtic/parasimpàtic)
        self.xdata = list(range(N_DADES))
        self.ydata = [0] * N_DADES
        self._plot_ref = None
        self.latest_value = 0.0
        self.ble_thread = None

        # Etiquetes amb informació (faltarà posar nivell de stress)
        self.label_dada = QtWidgets.QLabel("Última dada: --")
        self.label_connexio = QtWidgets.QLabel("Connexió: --")
        self.boto_connectar = QtWidgets.QPushButton("Connectar")

        self.label_dada.setStyleSheet("font-size: 14px")
        self.label_connexio.setStyleSheet("font-size: 14px")
        self.boto_connectar.clicked.connect(self.iniciar_connexio)

        # Layout per mostrar-ho tot. Per ara tot es mostra verticalment, un element sota l'anterior
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.label_dada)
        layout.addWidget(self.label_connexio)
        layout.addWidget(self.boto_connectar)

        central = QtWidgets.QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.setWindowTitle("Monitor ECG via BLE")

        # Actualització del plot
        self.timer = QtCore.QTimer()
        self.timer.setInterval(30)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def iniciar_connexio(self):
        # Comprovem si ja està iniciat x evitar tornar a connectar o reiniciar el procés 
        if self.ble_thread and self.ble_thread.isRunning():
            self.label_connexio.setText("Ja connectat o en procés...")
            return

        # Info de BLE
        self.label_connexio.setText("Intentant connectar...")
        self.label_connexio.setStyleSheet("font-size: 14px; color: white")

        # Fil per manejar l'interacció per bluetooth amb l'ESP.
        self.ble_thread = BLEThread(self)
        self.ble_thread.new_data.connect(self.receive_data)   # Reb la priemra dada 
        self.ble_thread.connected.connect(self.on_connected)  # Informa de que s'ha connectat
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
        self.ble_thread = None

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