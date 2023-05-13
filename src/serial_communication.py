import serial

class SerialCommunication:
    def __init__(self, baudrate: int=115200, port: str='COM5'):
        """Establishes serial communication with the Arduino.

        Args:
            baudrate (int, optional): Rate of communication. Defaults to 115200.
            port (str, optional): Port of communication. Defaults to 'COM5'.
        """
        self.ser = serial.Serial()
        self.ser.baudrate = baudrate
        self.ser.port = port
        self.ser.open()

    def set_mode(self, mode: int):
        """Takes LED light mode and sends corresponding value to the serial port.

        Args:
            mode (int): LED light mode.
            0: Off
            1: First bin
            2: Second bin
            3: Third bin
        """
        assert 0 <= mode <= 3, 'Invalid mode!'
        self.ser.write(bytes([mode]))

    def close(self):
        """Closes the serial port."""
        self.ser.close()

if __name__ == '__main__':
    """Used for testing purposes.
    """
    sc = SerialCommunication(port='COM8')
    sc.set_mode(1)
    sc.close()
