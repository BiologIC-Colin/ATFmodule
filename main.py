from atfcontroller import AtfController
from pressurecontroller import PressureController
from keyboardthread import KeyboardThread
import asyncio
import logging


# Create and configure logger
logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

# Creating an object
logger = logging.getLogger('ATF_Log')
console = logging.StreamHandler()
logging.getLogger('').addHandler(console)
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

p1 = PressureController()
p2 = PressureController()
isRunning = True


async def check_pressures():
    get_p1 = asyncio.create_task(p1.get_pressure())
    get_p2 = asyncio.create_task(p2.get_pressure())
    await asyncio.gather(get_p1, get_p2)
    # print(get_p1.result())
    # print(get_p2.result())


def command_received(inp):
    global isRunning
    logger.debug(f'Keyboard Callback: Command received: {inp}')
    if inp == 's':
        atfThread.atf_start()
    elif inp == 'e':
        atfThread.atf_stop()
    elif inp == 'q':
        isRunning = False


async def main():
    while isRunning:
        await check_pressures()
        await asyncio.sleep(1)


if __name__ == '__main__':
    ktThread = KeyboardThread(command_received)
    atfThread = AtfController()
    asyncio.run(main())
    ktThread.stopThread = True
    atfThread.stopThread = True
    atfThread.join()
    ktThread.join()


