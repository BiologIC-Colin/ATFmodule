import asyncio
from enum import Enum
from perfusion import Perfusion, PerfusionCommand
from atfdatabank import AtfDataBank
import logging


logger = logging.getLogger('ATF_Log')


class States(Enum):
    READY = 0
    PRIMING = 1
    RUN_WITHDRAW = 2
    RUN_INFUSE = 3
    STOPPING = 4
    ERROR = 5


class AtfController:

    def __init__(self, atf_volume, atf_rate, cs_rate, cs_density):
        self.isRunning = True
        self._currentState = States.READY
        self._state = States.READY
        self._stateChanged = False
        self._stopRequest = False
        self.atf_volume = atf_volume
        self.atf_rate = atf_rate  # ml/min
        self.cs_rate = cs_rate  # nl/cell/day
        self.cs_density = cs_density # cells/ml
        self._perfusion = Perfusion(self.atf_volume, self.atf_rate, self.cs_rate, self.cs_density)


    async def controllerloop(self):

            if self._stopRequest and not self._state == States.STOPPING:
                self._state = States.STOPPING
                self._stateChanged = True

            # print("State is {}".format(self._state))
            # print("State changed is {}".format(self._stateChanged))
            event_loop = asyncio.get_event_loop()
            if self._stateChanged:
                logger.debug("State has changed to {}".format(self._state))
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
                    stop_task = asyncio.create_task(self._atf_stop())
                    asyncio.ensure_future(stop_task, loop=event_loop)
                elif self._state == States.ERROR:
                    pass
            await asyncio.sleep(0.2)

    # State transitions
    async def _prime(self):
        if not self._perfusion.isBusy:
            logger.info("Transitioning to Prime")
            self._stateChanged = False
            await self._perfusion.doCommand(PerfusionCommand.PRIME)
            self._state = States.RUN_WITHDRAW
            self._stateChanged = True

    async def _withdraw(self):
        if not self._perfusion.isBusy:
            logger.info("Transitioning to Withdraw")
            self._stateChanged = False
            await self._perfusion.doCommand(PerfusionCommand.WITHDRAW)
            self._state = States.RUN_INFUSE
            self._stateChanged = True

    async def _infuse(self):
        if not self._perfusion.isBusy:
            logger.info("Transitioning to Infuse")
            self._stateChanged = False
            await self._perfusion.doCommand(PerfusionCommand.INFUSE)
            self._state = States.RUN_WITHDRAW
            self._stateChanged = True

    async def _atf_stop(self):
        if not self._perfusion.isBusy:
            logger.info("Transitioning to Stop")
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
            logger.info("Start command received")
            # print("atf_start")

    def atf_stop(self):
        self._stopRequest = True
        logger.info("Stop command received")
        # print("atf_Stop")

    def atf_state(self):
        return self._state

    def set_atf_rate(self, rate):
        self._perfusion.setAtfRate(rate)

    def set_atf_volume(self, volume):
        self._perfusion.setAtfVolume(volume)

    def set_cs_rate(self, rate):
        self._perfusion.setEfluxRate(rate)

    def set_cs_density(self, density):
        self._perfusion.setEfluxDensity(density)