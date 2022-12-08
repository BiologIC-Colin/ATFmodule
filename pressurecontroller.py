import asyncio


class PressureController:

    def __init__(self, bus, address):
        self._bus = bus
        self._address = address

    async def get_pressure(self) -> int:
        result = 1
        await asyncio.sleep(1)
        return result
