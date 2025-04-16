# Per saber com funcionen els índexs en arrays en python


import random

# Generate a list of 10 random floats between 10 and 20
floats = [random.uniform(3, 4) for _ in range(10)]
floats = [i for i in range(13)]
print(len(floats))

print(floats[0:5])  # Accedeix als 5 primers elements
print(floats[5:10]) # Accedeix als 5 darrers elements
print(floats[10])
print(floats[11])
print(floats[12])

import sys

print(sys.getsizeof(float()))