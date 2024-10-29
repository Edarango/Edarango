import serial

class COMHandler:
    def __init__(self, com_port=0, baud_rate=9600, data_bits=8, stop_bits=1, parity=0):
        try:
            self.ser = serial.Serial(
                port=f'COM{com_port}',
                baudrate=baud_rate,
                bytesize=data_bits,
                stopbits=stop_bits,
                parity=serial.PARITY_NONE if parity == 0 else serial.PARITY_ODD if parity == 1 else serial.PARITY_EVEN,
                timeout=1
            )
        except serial.SerialException as e:
            print(f"Error initializing COM port: {e}")
            self.ser = None

    def read_from_com(self):
        try:
            if self.ser and self.ser.is_open:
                return self.ser.readline().decode('utf-8').strip()
        except Exception as e:
            print(f"Error reading from COM port: {e}")
        return None

    def close_com(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("COM port closed.")
