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
        self.isRunning = True
        self._stateChanged = False
        self._transitionComplete = False
        self.stopThread = False
        self.state = States.READY
        self.start()
        self.atf_volume = 3.0  # ml
        self.atf_rate = 1.0  # ml/min
        self.cs_rate = 0.2  # ml/min

    def run(self):
        asyncio.run(self._controller())

    async def _controller(self):
        while self.isRunning:
            if self.stopThread:
                self.isRunning = False
                break
            if self._transitionComplete:
                print("State is {}".format(self.state))
                if self._stateChanged:
                    if self.state == States.READY:
                        print("State changed to {}".format(self.state))
                    elif self.state == States.PRIMING:
                        print("State changed to {}".format(self.state))
                        await self._prime()
                    elif self.state == States.RUN_WITHDRAW:
                        print("State changed to {}".format(self.state))
                        await self._withdraw()
                    elif self.state == States.RUN_INFUSE:
                        print("State changed to {}".format(self.state))
                        await self._infuse()
                    elif self.state == States.STOPPING:
                        print("State changed to {}".format(self.state))
                    elif self.state == States.ERROR:
                        print("State changed to {}".format(self.state))
                        # will need to handle pump stalling
            await asyncio.sleep(2)

    # State transitions
    async def _prime(self):
        self.state = States.PRIMING
        self.stateChanged = False
        print('In prime transition')
        self.isRunning = True
        await asyncio.sleep(5)


    async def _infuse(self):
        self.state = States.RUN_INFUSE
        self.stateChanged = False
        print('In infuse transition')
        await asyncio.sleep(5)

    async def _withdraw(self):
        self.state = States.RUN_WITHDRAW
        self.stateChanged = False
        print('In Withdraw transition')
        await asyncio.sleep(5)

    async def _atf_stop(self):
        self.state = States.STOPPING
        self.stateChanged = False
        print('In atf stop transition')
        await asyncio.sleep(5)

    # Perfusion commands
    def atf_start(self):
        if self.state == States.READY:
            self.state = 1
            self._stateChanged = True
