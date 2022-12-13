import asyncio
import struct

from atfcontroller import AtfController
from pressurecontroller import PressureController
from pyModbusTCP.server import ModbusServer, DataHandler
from atfdatabank import AtfDataBank
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

databank = AtfDataBank(0)
server = ModbusServer()

async def check_pressures():
    get_p1 = asyncio.create_task(p1.get_pressure())
    get_p2 = asyncio.create_task(p2.get_pressure())
    await asyncio.gather(get_p1, get_p2)
    # print(get_p1.result())
    # print(get_p2.result())

def modbus_change(address, from_value, to_value):
    print("Modbus change fired: {} {} {}".format(address, from_value, to_value))
    if address == 1000:
        if to_value:
            print("Starting...")
            databank.set_coils(1000,[0])
            atf_controller.atf_start()
    elif address == 1001:
        if to_value:
            print("Stopping...")
            databank.set_coils(1001, [0])
            atf_controller.atf_stop()
    elif address == 5000:
        print("Setting atf Volume")
        atf_controller.set_atf_volume(to_value)
    elif address == 5100:
        print("Setting atf rate")
        atf_controller.set_atf_volume(to_value)
    elif address == 5200:
        print("Setting cs rate")
        atf_controller.set_atf_volume(to_value)



async def main():
    while isRunning: # Main program loop
        databank.set_discrete_inputs(2000,[1])
        await check_pressures()
        await atf_controller.controllerloop()


def init_Modbus():
    global databank
    databank.callback = modbus_change
    databank = AtfDataBank(modbus_change)
    # Coils
    coil_list = [0, 0]  # [Start, Stop]
    databank.set_coils(1000, coil_list)
    # Discrete Coils
    discrete_coil_list = [0] # [Is Running]
    databank.set_discrete_inputs(2000, discrete_coil_list)
    # IsRunning
    # Input Registers
    # Pressure 1
    # Pressure 2
    # System State
    # Holding Registers
    atf_volume_holding_register = list(bytearray(struct.pack("f",atf_controller.atf_volume)))
    databank.set_holding_registers(5000,atf_volume_holding_register)
    atf_rate_holding_register = list(bytearray(struct.pack("f",atf_controller.atf_rate)))
    databank.set_holding_registers(5100,atf_rate_holding_register)
    cs_rate_holding_register = list(bytearray(struct.pack("f",atf_controller.cs_rate)))
    databank.set_holding_registers(5200,cs_rate_holding_register)


    global server
    server = ModbusServer(host='0.0.0.0', port=1080, data_bank=databank, no_block=True)

if __name__ == '__main__':
    atf_controller = AtfController()
    init_Modbus()
    server.start()
    asyncio.run(main())



