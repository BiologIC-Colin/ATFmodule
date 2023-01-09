import asyncio
import logging
from periphery import SPI

class PressureController:

    def __init__(self):
        self._pressure = 1
        self._name = __name__
        self._logger = logging.getLogger('ATF_Log')
        self.spi = SPI("/dev/spidev0.0", 0, 200000)


    async def get_pressure(self):
        self._logger.debug("Pressure request from {}".format(self._name))
        # await asyncio.sleep(1)
        command = [0xAA, 0x00, 0x00]
        data = [0xFA, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        command = self.spi.transfer(command)
        await asyncio.sleep(0.01)
        data = self.spi.transfer(data)
        press_counts = data[3] + data[2] * 256 + data[1] * 65536 # calculate digital
        print("Pressure Counts: {}".format(press_counts))
        temp_counts = data[6] + data[5] * 256 + data[4] * 65536  # calculate
        print("Temp Counts: {}".format(temp_counts))
        temperature = (temp_counts * 200 / 16777215) - 50 # calculate
        print("Temperature: {}".format(temperature))
        percentage = (press_counts / 16777215) * 100 # calculate
        print("Pressure %: {}".format(percentage))
        #pressure = ((press_counts - outputmin) * (30)) / (outputmax - outputmin) + pmin;
        return percentage

