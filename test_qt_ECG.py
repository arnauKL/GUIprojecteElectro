import sys
import matplotlib
import random
import serial                 # Per llegir del port serie
matplotlib.use('Qt5Agg')

#from PyQt5 import QtCore, QtWidgets
from PySide6 import QtCore, QtWidgets, QtGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    # Canvas de matplotlib
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class MainWindow(QtWidgets.QMainWindow):
    # Finestra ppal que conté tots els elements
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   # Crida al constructor de la classe mare (QtWidgets.QMainWindow)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.setCentralWidget(self.canvas)

        # Això segurament s'hauria de canviar de cares a fer el plot de l'ECG
        n_data = 1000
        self.xdata = list(range(n_data))
        self.ydata = [random.randint(-1, 1) for i in range(n_data)]

        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.
        self._plot_ref = None
        self.update_plot()

        self.show()

        # Setup a timer to trigger the redraw by calling update_plot.
        # Això segurament s'hauria de canviar de cares a fer el plot de l'ECG
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        # Drop off the first y element, append a new one.

        line = ser.readline().decode().strip()
        dada = float(line)
        # Casting per passar de string a float de les dades de les dues funcions x poder fer el plot
        self.ydata = self.ydata[1:] + [dada]

        # Note: we no longer need to clear the axis.
        if self._plot_ref is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refs = self.canvas.axes.plot(self.xdata, self.ydata, 'r')
            self._plot_ref = plot_refs[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_ref.set_ydata(self.ydata)

        # Trigger the canvas to update and redraw.
        self.canvas.draw()


ser = serial.Serial('COM3', 115200) # Iniciem el Serial amb paràmetres de la configuració de l'ESP
app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()