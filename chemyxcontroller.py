import time


class ChemyxController:
    delay = 0.1

    def __init__(self):
        pass

    def infuse(self):
        print('Infuse')
        time.sleep(self.delay)

    def withdraw(self):
        print('Withdraw')
        time.sleep(self.delay)
