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
        self.isRunning = False
        self.stopThread = False
        self.state = States.READY
        self.start()

    def run(self):
        asyncio.run(self._controller())

    async def _controller(self):
        await self._prime()
        while self.isRunning:
            if self.stopThread:
                self.isRunning = False
                break

            await asyncio.sleep(2)
            print("beep")

    async def _prime(self):
        self.state = States.PRIMING
        print('In prime')
        self.isRunning = True
        await asyncio.sleep(5)

    async def _infuse(self):
        self.state = States.RUN_INFUSE
        print('In infuse')
        await asyncio.sleep(5)

    async def _withdraw(self):
        self.state = States.RUN_WITHDRAW
        print('In Withdraw')
        await asyncio.sleep(5)

    async def _atf_stop(self):
        self.state = States.STOPPING
        print('In atf stop')
        await asyncio.sleep(5)
