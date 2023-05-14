from detection import Detection
from serial_communication import SerialCommunication

if __name__ == "__main__":
    args = Detection.parse_args()
    det = Detection(
        args, serial_communication=SerialCommunication(port='COM9'))
    det.run()
