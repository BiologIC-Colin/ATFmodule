from chemyxcontroller import ChemyxController
from enum import Enum
import time
import logging

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

_atf_pump = Pump(3.0, 1.0)
_eflux_pump = Pump(1.0, 0.2)


class Perfusion:

    def __init__(self):
        self._pump = ChemyxController()
        self._pump.openConnection()

        # Configure pump 1
        self._pump.changePump(1)
        self._pump.setUnits(_atf_pump.syringe.units)
        self._pump.setDiameter(_atf_pump.syringe.diameter)
        self._pump.setVolume(_atf_pump.volume)
        self._pump.setRate(_atf_pump.rate)
        self._pump.setDelay(_atf_pump.delay)

        # Configure pump 2
        self.setEflux(0.1)

    def _getPumpState(self):
        response = self._pump.getPumpStatus()
        return response

    def _prime(self):
        logger.info('Pump prime command executed')
        self._pump.changePump(1)
        self._pump.setRate(-_atf_pump.rate)
        self._pump.startPump(mode=1)
        self._await_finish()
        self._pump.setRate(_atf_pump.rate)
        self._pump.startPump(mode=1)
        self._await_finish()

    def _withdraw(self):
        logger.info('Pump withdraw command executed')
        # Set pump 1
        self._pump.changePump(1)
        self._pump.setRate(-_atf_pump.rate)
        # Set pump 2
        self._pump.startPump(mode=0)
        self._await_finish()
        self._pump.changePump(1)
        logger.info(f'Cycle has withdrawn product: {self._pump.getDisplacedVolume()}')

    def _infuse(self):
        logger.info('Pump infuse command executed')
        self._pump.setRate(_atf_pump.rate)
        self._pump.startPump(mode=1)
        self._await_finish()

    def _empty(self):
        logger.info('Pump empty command executed')
        self._pump.stopPump()
        self._pump.changePump(1)
        logger.info(self._pump.getDisplacedVolume())
        # Need to think this through - is there an absolute position

    def _await_finish(self):
        while self._getPumpState() != '0':
            time.sleep(1)


    def doCommand(self, command):
        if self._getPumpState() == '0':
            if command == PerfusionCommand.PRIME:
                self._prime()
            elif command == PerfusionCommand.WITHDRAW:
               self._withdraw()
            elif command == PerfusionCommand.INFUSE:
               self._infuse()
            elif command == PerfusionCommand.EMPTY:
                self._empty()

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
