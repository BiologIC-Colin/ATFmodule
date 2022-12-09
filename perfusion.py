from chemyxcontroller import ChemyxController
from enum import Enum




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

    def __init__(self):
        self.syringe = Syringe('BD 20ml Plastic', 20.00, 'mL/min', 19.13)  # Load the default syringe
        self.volume = 3.0
        self.rate = 1.0
        self.delay = 0.0

pump1 = Pump()
pump2 = Pump()
perfusionRate = 5.0
perfusionPulseVolume = 0.0
atfFillVolume = 1.0

class Perfusion:



    def __init__(self):
        self._pump = ChemyxController()
        self._pump.openConnection()

        # Configure pump 1
        self._pump.changePump(1)
        self._pump.setUnits(pump1.syringe.units)
        self._pump.setDiameter(pump1.syringe.diameter)
        self._pump.setVolume(pump1.volume)
        self._pump.setRate(pump1.rate)
        self._pump.setDelay(pump1.delay)

        # Configure pump 2
        self._pump.changePump(2)
        self._pump.setUnits(pump2.syringe.units)
        self._pump.setDiameter(pump2.syringe.diameter)
        self._pump.setVolume(pump2.volume)
        self._pump.setRate(pump2.rate)
        self._pump.setDelay(pump2.delay)

    def _getPumpState(self):
        response = self._pump.getPumpStatus()
        return response

    async def _prime(self):
        print("Fill ATF")
        self._pump.changePump(1)
        self._pump.setVolume(atfFillVolume)
        self._pump.setRate(-perfusionRate)
        self._pump.startPump(mode=1)
        self._await_finish()
        self._pump.setRate(perfusionRate)
        self._pump.startPump(mode=1)
        self._await_finish()

    async def _withdraw(self):
        print("Withdraw ATF")
        self._pump.setVolume(atfFillVolume)
        self._pump.setRate(-perfusionRate)
        self._pump.startPump(mode=1)
        self._await_finish()

    async def _await_finish(self):
        while self._getPumpState() != '0':
            asyncio.sleep(1)


    async def doCommand(self, command):
        if self._getPumpState() == '0':
            if command == PerfusionCommand.PRIME:
                await _prime()
            elif command == PerfusionCommand.WITHDRAW:
                await _withdraw()




