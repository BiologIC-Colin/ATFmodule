from atfcontroller import AtfController
import time


def main():
    input("This prompt")
    controller.start()
    time.sleep(60)
    controller.stop()


if __name__ == '__main__':
    controller = AtfController()
    main()
