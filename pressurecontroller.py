import asyncio


class PressureController:

    def __init__(self):
        self._pressure = 1

    async def get_pressure(self):
        await asyncio.sleep(1)
        return self._pressure
