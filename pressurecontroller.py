import asyncio
import logging

class PressureController:

    def __init__(self):
        self._pressure = 1
        self._name = __name__
        self._logger = logging.getLogger('ATF_Log')

    async def get_pressure(self):
        self._logger.debug("Pressure request from {}".format(self._name))
        await asyncio.sleep(1)
        return self._pressure

