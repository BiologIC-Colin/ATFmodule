import asyncio
from enum import Enum
from perfusion import Perfusion, PerfusionCommand
import logging

logger = logging.getLogger('ATF_Log')

class States(Enum):
    READY = 0
    PRIMING = 1
    RUN_WITHDRAW = 2
    RUN_INFUSE = 3
    STOPPING = 4
    ERROR = 5


class AtfController():

    def __init__(self):
        self.isRunning = True
        self._currentState = States.READY
        self._state = States.READY
        self._stateChanged = False
        self._stopRequest = False
        self._perfusion = Perfusion()
        self.atf_volume = 3.0  # ml
        self.atf_rate = 1.0  # ml/min
        self.cs_rate = 0.2  # ml/min


    async def controllerloop(self):

            if self._stopRequest:
                self._state = States.STOPPING
                self._stateChanged = True

            # print("State is {}".format(self._state))

            if self._state == States.READY:
                pass
            elif self._state == States.PRIMING:
                if self._stateChanged:  # Fire the transition
                    await self._prime()
            elif self._state == States.RUN_WITHDRAW:
                if self._stopRequest:
                    self._state == States.STOPPING
                elif self._stateChanged:
                    await self._withdraw()
            elif self._state == States.RUN_INFUSE:
                if self._stopRequest:
                    self._state == States.STOPPING
                elif self._stateChanged:
                    await self._infuse()
            elif self._state == States.STOPPING:
                if self._stateChanged:
                    print("Doing a stop")
                    await self._atf_stop()
                    self._state = States.READY
            elif self._state == States.ERROR:
                pass
            await asyncio.sleep(2)

    # State transitions
    async def _prime(self):
        print('In prime transition')
        self._perfusion.doCommand(PerfusionCommand.PRIME)
        await asyncio.sleep(1)
        self._state = States.RUN_WITHDRAW

    async def _infuse(self):
        print('In infuse transition')
        self._perfusion.doCommand(PerfusionCommand.INFUSE)
        await asyncio.sleep(1)
        self._state = States.RUN_WITHDRAW

    async def _withdraw(self):
        print('In withdraw transition')
        self._perfusion.doCommand(PerfusionCommand.WITHDRAW)
        await asyncio.sleep(1)
        self._state = States.RUN_INFUSE

    async def _atf_stop(self):
        print('In stop transition')
        self._perfusion.doCommand(PerfusionCommand.EMPTY)
        await asyncio.sleep(1)  # Do the transition
        self.stateChanged = False
        self._stopRequest = False
        self._state = States.READY

    # Perfusion commands
    def atf_start(self):
        if self._state == States.READY:
            self._stateChanged = True
            self._state = States.PRIMING
            print("atf_start")

    def atf_stop(self):
        self._stopRequest = True
        print("atf_Stop")

    def atf_state(self):
        return self._state
