import struct
import asyncio
from PySide6.QtCore import QThread, Signal
from bleak import BleakClient, BleakError
from config import ADDRESS, CHARACTERISTIC_UUID

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

        # Si les dades són exactament 80 bytes (20 floats)
        if len(data) == 80:
            # Desempaqueta les dades (20 floats)
            values = struct.unpack('20f', data)
            self.new_data.emit(values) # 'envia' la dada a Qt perquè la mostri
        else:
            # Si la mida no és la correcta, pots gestionar-ho d'una altra manera
            print(f"Error: la mida del buffer no és la correcta. Mida rebuda: {len(data)}")
        
        #values = struct.unpack('20f', data) # 20 floats rebuts en teoria
        #self.new_data.emit(values) # 'envia' la dada a Qt perquè la mostri

    def stop(self):
        self._running = False