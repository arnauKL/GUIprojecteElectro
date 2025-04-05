import serial                 # Per llegir del port serie
import matplotlib.pyplot as plt     # Per mostrar el plot

print("Iniciant programa")
ser = serial.Serial('COM3', 115200) # Iniciem el Serial amb paràmetres de la configuració de l'ESP

# Iniciem vectors de dades buits
dadesSin = []

while True:
    # Llegim la línea que arriba per Serial
    line = ser.readline().decode().strip()

    try:
        # Casting per passar de string a float de les dades de les dues funcions x poder fer el plot
        dada = float(line)
        dadesSin.append(dada)

        # Plot del sinus
        plt.plot(dadesSin, color=(0.4, 0.5, 0.5))
        plt.xlabel('temps')
        plt.ylabel('OPAMPtud')
        plt.title('Funció sinus')
        bb = dict(boxstyle="round", ec=(0.3, 0.4, 0.4), fc=(0.4, 0.5, 0.5),)
        plt.text(0, -80, f"Amplitud: {dada}\nTemps d'actualització (ms): {dada}", fontsize=12, bbox=bb)


        plt.pause(0.01)  # Mostra el plot i pausa per 0.1 segons

        # un cop mostrat, esborrem el plot per evitar que apareixi diferents
        plt.clf()

        # Per mantenir una mida raonable de dades (menys de 100) i una finestra que llisca
        if (len(dadesSin) > 1000):
            dadesSin.pop(0)         # Eliminar el primer element (posició 0)

    except ValueError:
        break