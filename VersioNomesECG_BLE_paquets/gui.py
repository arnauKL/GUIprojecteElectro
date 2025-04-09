from PySide6 import QtCore, QtWidgets
from canvas import MplCanvas
from BLE import BLEThread
from config import N_DADES_PLT, N_MOSTRES_ECG, N_MOSTRES_RES
from collections import deque


class MainWindow(QtWidgets.QMainWindow):
# Classe que guarda la finestra

    def __init__(self):
        super().__init__()

        # UI de matplotlib (per ara només 1 per l'ECG)
        self.canvas_ecg = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvas_res = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvas_barplot = MplCanvas(self, width=4, height=3, dpi=100)

        # Dades (faltarà posar les de respiració i activació de simpàtic/parasimpàtic)
        self.xdata = list(range(N_DADES_PLT))
        self.ydata_ecg = deque([0.0]*N_DADES_PLT, maxlen=N_DADES_PLT)
        self.ydata_res = deque([3.0]*N_DADES_PLT, maxlen=N_DADES_PLT)

        self._plot_ecg_ref = None
        self._plot_res_ref = None
        self.stress_value = 0.0
        self.SNS_value = 0.0
        self.PNS_value = 0.0
        self.ble_thread = None

        # Etiquetes amb informació (faltarà posar nivell de stress)
        self.label_dades = QtWidgets.QLabel(f"Dades del pacient.\nSNS:\t--\nPNS:\t--\nEstrés:\t--")
        self.label_connexio = QtWidgets.QLabel("Connexió: --")
        self.boto_connectar = QtWidgets.QPushButton("Connectar")

        self.label_dades.setStyleSheet("font-size: 14px")
        self.label_connexio.setStyleSheet("font-size: 14px")
        self.boto_connectar.clicked.connect(self.iniciar_connexio)

        # Layout per mostrar-ho tot. És un grid
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.canvas_ecg, 0, 0)     # Plot per ECG adalt esquerra
        layout.addWidget(self.canvas_res, 0, 1)     # Plot per Respiració adalt dreta
        layout.addWidget(self.canvas_barplot, 1, 0) # Barplot

        # Per mostrar varis labels fem un sublayout que mostrarà un sota l'altre
        layoutInfo = QtWidgets.QVBoxLayout()
        layoutInfo.addWidget(self.label_dades)
        layoutInfo.addWidget(self.label_connexio)
        layoutInfo.addWidget(self.boto_connectar)
        
        layout.addLayout(layoutInfo, 1, 1)


        central = QtWidgets.QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.setWindowTitle("Projecte d'Electrònica - Bouzas Deprez")

        # Actualització del plot
        self.timer = QtCore.QTimer()
        self.timer.setInterval(30)
        self.timer.timeout.connect(self.update_plots)
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

    def receive_data(self, values):
        # Aquí s'haurien de parsejar les dades que arriben de Signal
        self.ydata_ecg.extend(values[0:N_MOSTRES_ECG])           # dades de 0 fins N_MOSTRES_ECG_REBUDES són d'ECG
        self.ydata_res.extend(values[N_MOSTRES_ECG:(N_MOSTRES_RES+N_MOSTRES_ECG)])         # dades de N_MOSTRES_ECG_REBUDES fins N_MOSTRES_RES_REBUDES són de respiració
        
        # Darrers 3 valors: sns, pns i estrés
        self.SNS_value = values[N_MOSTRES_RES+N_MOSTRES_ECG]
        self.PNS_value = values[N_MOSTRES_RES+N_MOSTRES_ECG+1]
        self.stress_value = values[N_MOSTRES_RES+N_MOSTRES_ECG+2]

    def on_connected(self):
        self.label_connexio.setText("Connexió: Connectat")
        self.label_connexio.setStyleSheet("font-size: 14px; color: green")

    def on_error(self, msg):
        self.label_connexio.setText(f"Connexió: Error\n{msg}")
        self.label_connexio.setStyleSheet("font-size: 14px; color: red")
        self.ble_thread = None

    def update_plots(self):
        # Primer mirem pel plot de l'ECG
        if self._plot_ecg_ref is None:
            plot_refs = self.canvas_ecg.axes.plot(self.xdata, self.ydata_ecg, 'y')
            self._plot_ecg_ref = plot_refs[0]
        else:
            self._plot_ecg_ref.set_ydata(self.ydata_ecg)
        
        self.canvas_ecg.axes.set_ylim(-1, 1.5)
        self.canvas_ecg.draw()

        # Ara pel plot de la respiració
        if self._plot_res_ref is None:
            plot_refs = self.canvas_res.axes.plot(self.xdata, self.ydata_res, 'g')
            self._plot_res_ref = plot_refs[0]
        else:
            self._plot_res_ref.set_ydata(self.ydata_res)

        self.canvas_res.axes.set_ylim(2, 4)
        self.canvas_res.draw()

        # Ara els 3 valors calculats:
        #if self.stress_value != 0:
        self.label_dades.setText(f"Dades del pacient.\nSNS:\t{self.SNS_value}\nPNS:\t{self.PNS_value}\nEstrés:\t{self.stress_value}")
        self.canvas_barplot.axes.bar(['SNS', 'PNS'], [self.SNS_value, self.PNS_value], color=['tab:red', 'tab:blue'])
        self.canvas_barplot.axes.set_ylim(0, 100)
        self.canvas_barplot.draw()


    def closeEvent(self, event):
        if self.ble_thread:
            self.ble_thread.stop()
            self.ble_thread.quit()
            self.ble_thread.wait()
        event.accept()