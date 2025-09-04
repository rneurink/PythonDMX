import serial
import time
import numpy as np

class DMX512:
    def __init__(self, port, channels = 4):
        """
        Creates and instance of the DMX controller
        Port:
            DMX512(4)               # Windows
            DMX512('/dev/ttyUSB0')  # Linux
        Channels: The amount of channels to use
        """
        self.channels = channels
        
        # Initialize serial port
        try:
            self.serial = serial.Serial(port, baudrate=250000, bytesize=8, stopbits=2)
        except:
            print("Could not open %s. Quitting application", port)
            exit(0)

        print("Opened port %s", port)

        # Init data array
        self.data = np.zeros([self.channels+1], dtype='uint8')
        self.data[0] = 0 #Startcode
        
        # DMX params (!Note these parameters are expressed differently due to the OS limitations)
        self.breakus = 100.0 # Break reset (new DMX packet) LO 88us-1s
        self.MABus = 20.0 # Mark after break HI 8us-1s
        self.MTBPus = 50000.0 # Mark time between packets HI up to 1s

    def __del__(self):
        self.close()

    def close(self):
        """
        Closes the serial connection
        """
        if (self.serial is not None):
            self.serial.flush()
            self.serial.close()

    def set_channel(self, channel, value, autosend = False):
        """
        Sets the value of a single channel
        """
        if (channel > self.channels):
            raise IndexError("Channel %i does not excist. Numer of channels: %i", channel, self.channels)
        
        # Clamp value and set data
        value = max(0, min(value, 255))
        self.data[channel] = value

        if (autosend):
            self.send()

    def clear(self, autosend = False):
        """
        Clears the data
        """
        self.data = [0] * self.channels
        
        if (autosend):
            self.send()

    def send(self):
        """
        Send the DMX packet
        """
        # Send a break LO 88us - 1s
        self.serial.break_condition = True
        time.sleep(self.breakus / 1.0e6)

        # Send the Mark after Break (MAB) HI 8us - 1s
        self.serial.break_condition = False
        time.sleep(self.MABus / 1.0e6)

        # Send Start Code (implemented in the data array)
        # Send the Data
        self.serial.write(bytearray(self.data))

        # Mark time Between Packets (MTBP) HI up to 1s
        time.sleep(self.MTBPus / 1.0e6)

    
