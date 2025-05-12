SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

#ADDRESS = "D8:13:2A:73:1C:8A"       # ESP ARNAU
ADDRESS = "D8:13:2A:73:74:A6" # ESP GUILLEM
N_DADES_PLT = 1000

# Això hem de procurar que es mantengui a la par amb s codi de l'ESP
N_MOSTRES_ECG = 20
N_MOSTRES_RES = 20

DELAY_FRAMES = 40   # (en ms --> 1000/60ms = 17 fps ), sempre es pot baixar per major framerate

MIDA_FLOATS = 4

# Càlcul de dades totals rebudes
N_FLOATS_REBUTS = (N_MOSTRES_ECG + N_MOSTRES_RES + 3) # 3 floats per: SNS, PNS i estrés
