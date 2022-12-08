import sys
import time
from os.path import join, realpath, dirname
import logging
from transitions import Machine
from chemyxcontroller import ChemyxController

sys.path.append(join(dirname(realpath(__file__)), '..'))
logging.basicConfig(level=logging.INFO)


class AtfController(object):
    isRunning = False
    stopRequest = False
    delay = 0.0
    states = [
        {'name': 'ready'},
        {'name': 'priming', 'on_enter': 'do_prime'},
        {'name': 'running', 'on_enter': 'do_run'},
        {'name': 'stopping', 'on_enter': 'do_stop'}
    ]

    transitions = [
        {'trigger': 'start', 'source': 'ready', 'dest': 'priming'},
        {'trigger': 'run', 'source': 'priming', 'dest': 'running'},
        {'trigger': 'stop', 'source': 'running', 'dest': 'stopping'},
        {'trigger': 'reset', 'source': 'stopping', 'dest': 'ready'}
    ]

    def __init__(self):
        self.machine = Machine(model=self, states=AtfController.states, transitions=AtfController.transitions,
                               initial='ready', ignore_invalid_triggers=True,
                               auto_transitions=False)
        self._next_direction = 'infuse'
        self.cycle_count = 0
        self.pump = ChemyxController()

    def do_prime(self):
        print("In do_prime")
        time.sleep(AtfController.delay)
        self.isRunning = True
        self.run()

    def do_run(self):
        while self.isRunning:
            print("In do_run count {}".format(self.cycle_count))
            self.cycle_count = self.cycle_count + 1
            if self._next_direction == 'infuse':
                self._next_direction = 'withdraw'
                self.pump.infuse()
            else:
                self._next_direction = 'infuse'
                self.pump.withdraw()
        self.stop()

    def do_stop(self):
        print("In do_stop")
        time.sleep(AtfController.delay)

    def get_State(self) -> str:
        return self.state
