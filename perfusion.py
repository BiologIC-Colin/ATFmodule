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

    def __init__(self, volume, rate, syringe):
        self.syringe = syringe
        self.volume = volume
        self.rate = rate
        self.delay = 0.0

atf_syringe = Syringe('BD 20ml Plastic', 20.00, 'mL/min', 19.13)  # Load the default syringe
atf_pump = Pump(3.0, 1.0, atf_syringe)
eflux_syringe = Syringe('BD 1ml Plastic', 1.00, 'uL/min', 4.78)
eflux_pump = Pump(1.0, 0.2, eflux_syringe)
eflux_pump.syringe.units = 'uL/min'  # set units to ul/min
REACTION_VOLUME = 10  # ml


class Perfusion:

    def __init__(self, atfVol, atfRate, csRate, csDensity):
        atf_pump.volume = atfVol
        atf_pump.rate = atfRate
        self.csRate = csRate
        self.csDensity = csDensity

        eflux_pump.rate = self._calculateCS(csRate, csDensity)

        self._pump = ChemyxController()
        self._pump.openConnection()
        time.sleep(1)
        self.configurePumps()
        self.isBusy = False
        self.settingsChanged = True

    def configurePumps(self):
        self._pump.changePump(1)
        self._pump.setUnits(atf_pump.syringe.units)
        self._pump.setDiameter(atf_pump.syringe.diameter)
        self._pump.setVolume(atf_pump.volume)
        self._pump.setRate(atf_pump.rate)
        self._pump.setDelay(atf_pump.delay)
        _time_required = atf_pump.volume / atf_pump.rate
        _cs_volume_required = eflux_pump.rate * _time_required
        eflux_pump.volume = _cs_volume_required
        logger.info(f'CS Volume required is {_cs_volume_required}')
        self._pump.changePump(2)
        self._pump.setUnits(eflux_pump.syringe.units)
        self._pump.setDiameter(eflux_pump.syringe.diameter)
        self._pump.setVolume(eflux_pump.volume)
        self._pump.setRate(-eflux_pump.rate)  # Negative because it always withdraws
        self._pump.setDelay(eflux_pump.delay)
        self.settingsChanged = False


    def getPumpState(self):
        response = self._pump.getPumpStatus()
        return response

    async def prime(self):
        self.isBusy = True
        if self.settingsChanged:
            self.configurePumps()
        logger.info('Pump prime command executed')
        self._pump.changePump(1)
        self._pump.setRate(-atf_pump.rate)
        self._pump.startPump(mode=1)
        await self.await_finish()
        self._pump.setRate(atf_pump.rate)
        self._pump.startPump(mode=1)
        await self.await_finish()
        self.isBusy = False


    async def withdraw(self):
        self.isBusy = True
        if self.settingsChanged:
            self.configurePumps()
        logger.info('Pump withdraw command executed')
        # Set pump 1
        self._pump.changePump(1)
        self._pump.setRate(-atf_pump.rate)
        # Set pump 2
        self._pump.startPump(mode=0)
        await self.await_finish()
        self._pump.changePump(1)
        logger.info(f'Cycle has withdrawn product: {self._pump.getDisplacedVolume()}')
        self.isBusy = False

    async def infuse(self):
        self.isBusy = True
        if self.settingsChanged:
            self.configurePumps()
        logger.info('Pump infuse command executed')
        self._pump.setRate(atf_pump.rate)
        self._pump.startPump(mode=1)
        await self.await_finish()
        self.isBusy = False

    async def empty(self):
        self.isBusy = True
        if self.settingsChanged:
            self.configurePumps()
        logger.info('Pump empty command executed')
        self._pump.stopPump()
        self._pump.changePump(1)
        logger.info(self._pump.getDisplacedVolume())
        # Need to think this through - is there an absolute position
        self.isBusy = False

    async def await_finish(self) -> object:
        while self.getPumpState() != '0':
            await asyncio.sleep(1)  # Ensures both pumps remain sychronised
        self._pump.stopPump()

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

    async def setATF(self, atf_volume, atf_rate, cs_rate, cs_density):
        atf_pump.rate = atf_rate
        atf_pump.volume = atf_volume
        eflux_pump.rate = self._calculateCS(cs_rate, cs_density)
        _timerequired = atf_pump.volume / atf_pump.rate
        _volumerequired = eflux_pump.rate * _timerequired
        eflux_pump.volume = round(_volumerequired, 3)
        logger.info(f'CS Volume required is {eflux_pump.volume}')


    def setEfluxRate(self, csrate):
        if not csrate == self.csRate:
            self.csRate = csrate
            eflux_pump.rate = self._calculateCS(self.csRate, self.csDensity)
            self.settingsChanged = True

    def setEfluxDensity(self, csdensity):
        if not csdensity == self.csDensity:
            self.csDensity = csdensity
            eflux_pump.rate = self._calculateCS(self.csRate, self.csDensity)
            self.settingsChanged = True


    def setAtfRate(self,atfrate):
        if not atfrate == atf_pump.rate:
            atf_pump.rate = atfrate
            self.settingsChanged = True

    def setAtfVolume(self, atfvolume):
        if not atfvolume == atf_pump.volume:
            atf_pump.volume = atfvolume
            self.settingsChanged = True

    def _calculateCS(self, rate, density):
        # Multiply the cell specific rate by the number of cells
        # rate in nl/cell/day
        # density in cells/ml - volume fixed at 10
        total_cells = density * REACTION_VOLUME
        rate_ul_min = ((total_cells * rate) / 1440) / 1000  # 1440 minutes in a day
        return round(rate_ul_min, 3)