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


perfusion_atf_volume = 3.0  # ml
perfusion_atf_rate = 1.0  # ml/min
perfusion_cs_rate = 0.05  # nl/cell/day
perfusion_cs_density = 1000000  # cells/ml

async def check_pressures():
    get_p1 = asyncio.create_task(p1.get_pressure())
    get_p2 = asyncio.create_task(p2.get_pressure())
    await asyncio.gather(get_p1, get_p2)

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


async def main():
    while isRunning: # Main program loop
        databank.set_discrete_inputs(2000,[1])
        print("Main_Loop")
        await poll_Modbus()
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
    # Holding Registers
    atf_volume_holding_register = list(bytearray(struct.pack("f",atf_controller.atf_volume)))
    databank.set_holding_registers(5000,atf_volume_holding_register)
    atf_rate_holding_register = list(bytearray(struct.pack("f",atf_controller.atf_rate)))
    databank.set_holding_registers(5100,atf_rate_holding_register)
    cs_rate_holding_register = list(bytearray(struct.pack("f",atf_controller.cs_rate)))
    databank.set_holding_registers(5200,cs_rate_holding_register)
    cs_density_holding_register = list(bytearray(struct.pack("f",atf_controller.cs_density)))
    databank.set_holding_registers(5300,cs_density_holding_register)

    global server
    server = ModbusServer(host='0.0.0.0', port=1080, data_bank=databank, no_block=True)

async def poll_Modbus():
    global perfusion_atf_volume
    perfusion_atf_volume = struct.unpack("f", bytearray(databank.get_holding_registers(5000, 4)))[0]
    atf_controller.set_atf_volume(perfusion_atf_volume)
    global perfusion_atf_rate
    perfusion_atf_rate = struct.unpack("f", bytearray(databank.get_holding_registers(5100, 4)))[0]
    atf_controller.set_atf_rate(perfusion_atf_rate)
    global perfusion_cs_rate
    perfusion_cs_rate = struct.unpack("f", bytearray(databank.get_holding_registers(5200, 4)))[0]
    atf_controller.set_cs_rate(perfusion_cs_rate)
    global perfusion_cs_density
    perfusion_cs_density = struct.unpack("f", bytearray(databank.get_holding_registers(5300, 4)))[0]


if __name__ == '__main__':
    atf_controller = AtfController(perfusion_atf_volume, perfusion_atf_rate, perfusion_cs_rate, perfusion_cs_density)  # These are the system defaults
    init_Modbus()
    server.start()
    asyncio.run(main())



