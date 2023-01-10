import asyncio
import logging
from periphery import SPI

class PressureController:

    def __init__(self, device):
        self._pressure = 1
        self._name = __name__
        self._logger = logging.getLogger('ATF_Log')
        self.spi0 = SPI("/dev/spidev1.0", 0, 200000)
        self.spi1 = SPI("/dev/spidev1.1", 0, 200000)

    async def get_pressure(self):
        #self._logger.debug("Pressure request from {}".format(self._name))
        # await asyncio.sleep(1)
        command = [0xAA, 0x00, 0x00]
        data = [0xFA, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        command_0 = self.spi0.transfer(command)
        command_1 = self.spi1.transfer(command)
        await asyncio.sleep(0.01)
        data_0 = self.spi0.transfer(data)
        data_1 = self.spi1.transfer(data)
        res0 = self.calcPress(data_0)
        res1 = self.calcPress(data_1)
        print("SPI1.0: {}".format(res0))
        print("SPI1.1: {}".format(res1))
        return 1

    def calcPress(self, data):
        press_counts = data[3] + data[2] * 256 + data[1] * 65536  # calculate digital
        # print("Pressure Counts: {}".format(press_counts))
        temp_counts = data[6] + data[5] * 256 + data[4] * 65536  # calculate
        # print("Temp Counts: {}".format(temp_counts))
        temperature = (temp_counts * 200 / 16777215) - 50  # calculate
        # print("Temperature: {}".format(temperature))
        percentage = (press_counts / 16777215) * 100  # calculate
        # print("Pressure %: {}".format(percentage))
        # pressure = ((press_counts - outputmin) * (30)) / (outputmax - outputmin) + pmin;
        return [temperature, percentage]