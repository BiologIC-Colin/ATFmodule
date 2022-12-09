import asyncio
import threading
from enum import Enum


class States(Enum):
    READY = 0
    PRIMING = 1
    RUN_WITHDRAW = 2
    RUN_INFUSE = 3
    STOPPING = 4
    ERROR = 5


class AtfController(threading.Thread):

    def __init__(self):
        super(AtfController, self).__init__()
        self.start()
        self.isRunning = True
        self.stopThread = False

        self._currentState = States.READY
        self._state = States.READY
        self._stateChanged = False

        self._stopRequest = False

        self.atf_volume = 3.0  # ml
        self.atf_rate = 1.0  # ml/min
        self.cs_rate = 0.2  # ml/min

    def run(self):
        asyncio.run(self._controller())

    async def _controller(self):
        while self.isRunning:
            self._currentState = self._state  # Store the current state

            # print("In _Controller")
            if self.stopThread:
                self.isRunning = False
                break
            if self._stopRequest:
                self._state = States.STOPPING
                self._stateChanged = True

            print("State is {}".format(self._state))

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
        await asyncio.sleep(5)  # Do the transition
        # self.stateChanged = False
        # Prime is complete so we push to run
        self._state = States.RUN_WITHDRAW

    async def _infuse(self):
        print('In infuse transition')
        await asyncio.sleep(5)  # Do the transition
        # self.stateChanged = False
        # Infuse is complete change to Withdraw.
        self._state = States.RUN_WITHDRAW

    async def _withdraw(self):
        print('In withdraw transition')
        await asyncio.sleep(5)  # Do the transition
        # self.stateChanged = False
        # Withdraw is complete change to infuse.
        self._state = States.RUN_INFUSE

    async def _atf_stop(self):
        print('In stop transition')
        await asyncio.sleep(5)  # Do the transition
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