import threading
import time


class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk=None, name='keyboard-input-thread'):
        self.stopThread = False
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)


    def run(self):
        while not self.stopThread:
            self.input_cbk(input())  # waits to get input + Return
            time.sleep(1)
