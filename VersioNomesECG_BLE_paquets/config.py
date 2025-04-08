SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
ADDRESS = "D8:13:2A:73:1C:8A"       # ESP ARNAU
#ADDRESS = "" # ESP GUILLEM
N_DADES_PLT = 1000

# Això hem de procurar que es mantengui a la par amb s codi de l'ESP
N_MOSTRES_ECG_REBUDES = 30
N_MOSTRES_RES_REBUDES = 30

# Càlcul de dades totals rebudes
MIDA_FLOAT_BYTES = 4
N_FLOATS_REBUTS = (N_MOSTRES_ECG_REBUDES + N_MOSTRES_RES_REBUDES + 3) # 3 floats per: SNS, PNS i estrés