import struct
import asyncio
from PySide6.QtCore import QThread, Signal
from bleak import BleakClient, BleakError
from config import ADDRESS, CHARACTERISTIC_UUID

class BLEThread(QThread):
    new_data = Signal(float)
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
        [value] = struct.unpack('f', data)
        self.new_data.emit(value)

    def stop(self):
        self._running = False