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
        self.atf_volume = 0.5  # ml
        self.atf_rate = 2.0  # ml/min
        self.cs_rate = 0.2  # ml/min


    async def controllerloop(self):

            if self._stopRequest and not self._state == States.STOPPING:
                self._state = States.STOPPING
                self._stateChanged = True

            print("State is {}".format(self._state))
            print("State changed is {}".format(self._stateChanged))
            event_loop = asyncio.get_event_loop()
            if self._stateChanged:
                if self._state == States.READY:
                    self._stateChanged = False
                elif self._state == States.PRIMING:
                    prime_task = asyncio.create_task(self._prime())
                    asyncio.ensure_future(prime_task, loop=event_loop)
                elif self._state == States.RUN_WITHDRAW:
                    withdraw_task = asyncio.create_task(self._withdraw())
                    asyncio.ensure_future(withdraw_task, loop=event_loop)
                elif self._state == States.RUN_INFUSE:
                    infuse_task = asyncio.create_task(self._infuse())
                    asyncio.ensure_future(infuse_task, loop=event_loop)
                elif self._state == States.STOPPING:
                    print("Doing a stop")
                    await self._atf_stop()
                    self._state = States.READY
                elif self._state == States.ERROR:
                    pass
            await asyncio.sleep(1)

    # State transitions
    async def _prime(self):
        if not self._perfusion.isBusy:
            print('In prime transition')
            self._stateChanged = False
            await self._perfusion.doCommand(PerfusionCommand.PRIME)
            self._state = States.RUN_WITHDRAW
            self._stateChanged = True

    async def _withdraw(self):
        if not self._perfusion.isBusy:
            print('In withdraw transition')
            self._stateChanged = False
            await self._perfusion.doCommand(PerfusionCommand.WITHDRAW)
            self._state = States.RUN_INFUSE
            self._stateChanged = True

    async def _infuse(self):
        if not self._perfusion.isBusy:
            print('In infuse transition')
            self._stateChanged = False
            await self._perfusion.doCommand(PerfusionCommand.INFUSE)
            self._state = States.RUN_WITHDRAW
            self._stateChanged = True

    async def _atf_stop(self):
        if not self._perfusion.isBusy:
            print('In stop transition')
            self.stateChanged = False
            await self._perfusion.doCommand(PerfusionCommand.EMPTY)
            await asyncio.sleep(1)  # Do the transition
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

    def set_atf_rate(self, rate):
        self._perfusion.setAtfRate(rate)

    def set_atf_volume(self, volume):
        self._perfusion.setAtfVolume(volume)

    def set_cs_rate(self, rate):
        self._perfusion.setEflux(rate)