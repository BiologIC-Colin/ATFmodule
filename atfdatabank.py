from pyModbusTCP.server import DataBank
import logging


logger = logging.getLogger('ATF_Log')

class AtfDataBank(DataBank):

    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        super(AtfDataBank, self).__init__(*args, **kwargs)


    def on_coils_change(self, address, from_value, to_value, srv_info):
        """Call by server when change occur on coils space."""
        msg = 'change in coil space [{0!r:^5} > {1!r:^5}] at @ 0x{2:04X} from ip: {3:<15}'
        msg = msg.format(from_value, to_value, address, srv_info.client.address)
        logger.info(msg)
        if self.callback:
            self.callback(address,from_value,to_value)



    def on_holding_registers_change(self, address, from_value, to_value, srv_info):
        """Call by server when change occur on holding registers space."""
        msg = 'change in hreg space [{0!r:^5} > {1!r:^5}] at @ 0x{2:04X} from ip: {3:<15}'
        msg = msg.format(from_value, to_value, address, srv_info.client.address)
        logger.info(msg)
