import time

from chemyxcontroller import ChemyxController
from enum import Enum
import logging
import asyncio

logger = logging.getLogger('ATF_Log')




class PerfusionCommand(Enum):
    PRIME = 0
    INFUSE = 1
    WITHDRAW = 2
    EMPTY = 3


class Syringe:

    def __init__(self, description, volume_ml, units, diameter):
        self.description = description
        self.volume = volume_ml
        self.units = units
        self.diameter = diameter


class Pump:

    def __init__(self, volume, rate):
        self.syringe = Syringe('BD 20ml Plastic', 20.00, 'mL/min', 19.13)  # Load the default syringe
        self.volume = volume
        self.rate = rate
        self.delay = 0.0

_atf_pump = Pump(0.5, 2.0)
_eflux_pump = Pump(1.0, 0.2)


class Perfusion:

    def __init__(self):
        self._pump = ChemyxController()
        self._pump.openConnection()
        time.sleep(1)
        # Configure pump 1
        self._pump.changePump(1)
        self._pump.setUnits(_atf_pump.syringe.units)
        self._pump.setDiameter(_atf_pump.syringe.diameter)
        self._pump.setVolume(_atf_pump.volume)
        self._pump.setRate(_atf_pump.rate)
        self._pump.setDelay(_atf_pump.delay)

        # Configure pump 2
        self.setEflux(0.1)
        self.isBusy = False

    def getPumpState(self):
        response = self._pump.getPumpStatus()
        return response

    async def prime(self):
        self.isBusy = True
        logger.info('Pump prime command executed')
        self._pump.changePump(1)
        self._pump.setRate(-_atf_pump.rate)
        self._pump.startPump(mode=1)
        await self.await_finish()
        self._pump.setRate(_atf_pump.rate)
        self._pump.startPump(mode=1)
        await self.await_finish()
        self.isBusy = False


    async def withdraw(self):
        self.isBusy = True
        logger.info('Pump withdraw command executed')
        # Set pump 1
        self._pump.changePump(1)
        self._pump.setRate(-_atf_pump.rate)
        # Set pump 2
        self._pump.startPump(mode=0)
        await self.await_finish()
        self._pump.changePump(1)
        logger.info(f'Cycle has withdrawn product: {self._pump.getDisplacedVolume()}')
        self.isBusy = False

    async def infuse(self):
        self.isBusy = True
        logger.info('Pump infuse command executed')
        self._pump.setRate(_atf_pump.rate)
        self._pump.startPump(mode=1)
        await self.await_finish()
        self.isBusy = False

    async def empty(self):
        self.isBusy = True
        logger.info('Pump empty command executed')
        self._pump.stopPump()
        self._pump.changePump(1)
        logger.info(self._pump.getDisplacedVolume())
        # Need to think this through - is there an absolute position
        self.isBusy = False

    async def await_finish(self) -> object:
        while self.getPumpState() != '0':
            await asyncio.sleep(1)  # Ensures both pumps remain sychronised


    async def doCommand(self, command):
        if not self.isBusy:
            if command == PerfusionCommand.PRIME:
                await self.prime()
            elif command == PerfusionCommand.WITHDRAW:
               await self.withdraw()
            elif command == PerfusionCommand.INFUSE:
               await self.infuse()
            elif command == PerfusionCommand.EMPTY:
                await self.empty()
        return 0

    def setEflux(self, csrate):
        _csrate = csrate
        _timerequired = _atf_pump.volume / _atf_pump.rate
        _volumerequired = _csrate * _timerequired
        _eflux_pump.rate = _csrate
        _eflux_pump.volume = _volumerequired
        logger.info(f'CS Volume required is {_volumerequired}')
        self._pump.changePump(2)
        self._pump.setUnits(_eflux_pump.syringe.units)
        self._pump.setDiameter(_eflux_pump.syringe.diameter)
        self._pump.setVolume(_eflux_pump.volume)
        self._pump.setRate(-_eflux_pump.rate)  # Negative because it always withdraws
        self._pump.setDelay(_eflux_pump.delay)

    def setAtfRate(self,atfrate):
        _atf_pump.rate = atfrate
        self._pump.changePump(1)
        self._pump.setUnits(_atf_pump.syringe.units)
        self._pump.setDiameter(_atf_pump.syringe.diameter)
        self._pump.setVolume(_atf_pump.volume)
        self._pump.setRate(_atf_pump.rate)
        self._pump.setDelay(_atf_pump.delay)
        self.setEflux(_eflux_pump.rate)  # Recalculate the cell specific rate
