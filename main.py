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
        atf_controller.atf_start()
    elif inp == 'e':
        atf_controller.atf_stop()
    elif inp == 'q':
        isRunning = False


async def main():
    while isRunning: # Main program loop
        await check_pressures()
        await atf_controller.controllerloop()



if __name__ == '__main__':
    ktThread = KeyboardThread(command_received)
    atf_controller = AtfController()
    asyncio.run(main())
    ktThread.stopThread = True
    ktThread.join()


