from atfcontroller import AtfController
from pressurecontroller import PressureController
from keyboardthread import KeyboardThread
import asyncio


p1 = PressureController()
p2 = PressureController()
isRunning = True


async def check_pressures():
    get_p1 = asyncio.create_task(p1.get_pressure())
    get_p2 = asyncio.create_task(p2.get_pressure())
    await asyncio.gather(get_p1, get_p2)
    print(get_p1.result())
    print(get_p2.result())


def command_received(inp):
    global isRunning
    print("callback")
    if inp == 's':
        atfThread.atf_start()
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


