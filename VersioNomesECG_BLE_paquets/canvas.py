from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

#import matplotlib.pyplot as plt
#plt.style.use('dark_background')


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        COLOR_FONS_QT = '#1e1e1e'

        # Canviar colors del plot xq siguin iguals que el Qt
        self.axes.set_facecolor(COLOR_FONS_QT)  # Fons del plot
        self.fig.set_facecolor(COLOR_FONS_QT)  # Fons fora del plot (canvas)
        self.axes.tick_params(colors='white')  # Color dels ticks
        self.axes.spines['bottom'].set_color('white')
        self.axes.spines['top'].set_color('white')
        self.axes.spines['left'].set_color('white')
        self.axes.spines['right'].set_color('white')
        self.axes.yaxis.label.set_color('white')
        self.axes.xaxis.label.set_color('white')
        self.axes.title.set_color('white')
        super().__init__(self.fig)
