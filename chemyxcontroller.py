import time
import serial
import logging



logger = logging.getLogger('ATF_Log')
class ChemyxController:
    def __init__(self):
        self.ser = None
        self.port = "/dev/ttyUSB0"
        self.baudrate = 9600
        self.multipump = True
        self.verbose = True

        self.currentPump = 1

    def openConnection(self):
        try:
            self.ser = serial.Serial()
            self.ser.baudrate = self.baudrate
            self.ser.port = self.port
            self.ser.timeout = 0
            self.ser.open()
            if self.ser.isOpen():
                if self.verbose:
                    print("Opened port")
                    print(self.ser)
                    self.ser.flushInput()
                    self.ser.flushOutput()
        except Exception as e:
            if self.verbose:
                print("Failed to connect to pump")
                logger.error('Failed to connect to pump')
                print(e)
            pass

    def closeConnection(self):
        self.ser.close()
        if self.verbose:
            logger.info('Closed connection to pump')

    def sendCommand(self, command):

        if self.multipump and command[:3] == 'set':
            # The command is a multipump set command
            command = self.addPump(command)
        #print(command)
        try:
            arg = bytes(str(command), 'utf8') + b'\r'
            #print(arg)
            self.ser.write(arg)  # writes the command
            time.sleep(0.2)
            response = self.getResponse()
            return response
        except TypeError as e:
            if self.verbose:
                print(e)
            self.ser.close()

    def getResponse(self):
        try:
            response_list = []
            while True:
                response = self.ser.readlines()
                for line in response:
                    line = line.strip(b'\n').decode('utf8')
                    # Remove preceeding close bracket
                    if line[0] == '>':
                        if len(line) == 1:
                            break
                        line = line[1:]
                    line = line.strip('\r')
                    if line[0].isdigit():
                        # Find the \r
                        index = line.find('\r')
                        # Target pump
                        response_list.append(line[0])
                        # Command
                        response_list.append(line[2:index])
                        # State
                        response_list.append(line[index:].strip('\r'))
                    else:
                        response_list.append(line)
                break
                #print(response_list)
            return response_list
        except TypeError as e:
            if self.verbose:
                print(e)
            self.closeConnection()
        except Exception as f:
            if self.verbose:
                print(f)
            self.closeConnection()

    def startPump(self, mode=0, multistep=False):
        """
        Start run of pump.

        Parameters
        ----------
        mode : int
            Mode that pump should start running.
            For single-channel pumps this value should not change.
            Dual-channel pumps have more control over run state.

            0: Default, runs all channels available.
            1: For dual channel pumps, runs just pump 1.
            2: For dual channel pumps, runs just pump 2.
            3: Run in cycle mode.
        multistep : bool
            Determine if pump should start in multistep mode
        """
        command = 'start '
        if self.multipump and mode > 0:
            command = f'{mode} {command}'
        if multistep:
            command = f'{command} {int(multistep)}'
        response = self.sendCommand(command)
        return response

    def stopPump(self, mode=0):
        """
        Stop run of pump.

        Parameters
        ----------
        mode : int
            Mode that pump should stop running.
            For single-channel pumps this value should not change.
            Dual-channel pumps have more control over run state.

            0: Default, stops all channels available.
            1: For dual channel pumps, stops just pump 1.
            2: For dual channel pumps, stops just pump 2.
            3: Stop cycle mode.
        """
        command = 'stop '
        if self.multipump and mode > 0:
            command = f'{mode} {command}'
        response = self.sendCommand(command)
        return response

    def pausePump(self, mode=0):
        """
        Pauses run of pump.

        Parameters
        ----------
        mode : int
            Mode that pump should pause current run.
            For single-channel pumps this value should not change.
            Dual-channel pumps have more control over run state.

            0: Default, pauses all channels available.
            1: For dual channel pumps, pauses just pump 1.
            2: For dual channel pumps, pauses just pump 2.
            3: Pause cycle mode.
        """
        command = 'pause '
        if self.multipump and mode > 0:
            command = f'{mode} {command}'
        response = self.sendCommand(command)
        return response

    def restartPump(self):
        command = '1 restart '
        response = self.sendCommand(command)
        return response

    def setUnits(self, units):
        units_dict = {'mL/min': '0', 'mL/hr': '1', 'uL/min': '2', 'uL/hr': '3'}
        command = 'set units ' + units_dict[units]
        response = self.sendCommand(command)
        return response

    def setDiameter(self, diameter):
        command = 'set diameter ' + str(diameter)
        response = self.sendCommand(command)
        return response

    def setRate(self, rate):
        if isinstance(rate, list):
            # if list of volumes entered, use multi-step command
            command = 'set rate ' + ','.join([str(x) for x in rate])
        else:
            command = 'set rate ' + str(rate)
        response = self.sendCommand(command)
        return response

    def setVolume(self, volume):
        if isinstance(volume, list):
            # if list of volumes entered, use multi-step command
            command = 'set volume ' + ','.join([str(x) for x in volume])
        else:
            command = 'set volume ' + str(volume)
        response = self.sendCommand(command)
        return response

    def setDelay(self, delay):
        if isinstance(delay, list):
            # if list of volumes entered, use multi-step command
            command = 'set delay ' + ','.join([str(x) for x in delay])
        else:
            command = 'set delay ' + str(delay)
        response = self.sendCommand(command)
        return response

    def setTime(self, timer):
        command = 'set time ' + str(timer)
        response = self.sendCommand(command)
        return response

    def getParameterLimits(self):
        command = 'read limit parameter'
        response = self.sendCommand(command)
        return response

    def getParameters(self):
        command = 'view parameter'
        response = self.sendCommand(command)
        return response

    def getDisplacedVolume(self):
        command = str(self.currentPump) + ' dispensed volume'
        response = self.sendCommand(command)
        return response

    def getElapsedTime(self):
        command = 'elapsed time'
        response = self.sendCommand(command)
        return response

    def getPumpStatus(self):
        command = str(self.currentPump)+ ' status'
        response = self.sendCommand(command)
        # print(response)
        return response[2]

    def changePump(self, pump):
        if self.multipump:
            self.currentPump = pump

    def addPump(self, command):
        """
        Prepend pump number to command. Used for 'set' commands.

        Parameters
        ----------
        command : string
        """
        if self.multipump:
            return f'{self.currentPump} {command}'
        else:
            return command