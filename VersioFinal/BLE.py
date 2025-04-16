import struct
import asyncio
from PySide6.QtCore import QThread, Signal
from bleak import BleakClient, BleakError
from config import ADDRESS, CHARACTERISTIC_UUID, N_FLOATS_REBUTS, MIDA_FLOATS

class BLEThread(QThread):
    new_data = Signal(tuple)
    connected = Signal()
    error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True

    def run(self):
        asyncio.run(self.ble_loop())

    async def ble_loop(self):
        try:
            async with BleakClient(ADDRESS) as client:
                await client.start_notify(CHARACTERISTIC_UUID, self.notification_handler)
                self.connected.emit()

                while self._running:
                    await asyncio.sleep(0.1)
        except BleakError as e:
            self.error.emit(str(e))

    def notification_handler(self, sender, data):
        # Desempaqueta les dades (N floats)
        if (len(data) == N_FLOATS_REBUTS*MIDA_FLOATS):
            values = struct.unpack(f'{N_FLOATS_REBUTS}f', data)
            self.new_data.emit(values) # 'envia' les dades a Qt perquè la mostri
        else:
            print(f"Nombre de dades inesperat rebudes per BLE: {len(data)}. S'esperen {N_FLOATS_REBUTS*MIDA_FLOATS}")

    def stop(self):
        self._running = False