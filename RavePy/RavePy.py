import numpy as np
import threading
import time
import math
import pyaudio

import matplotlib.pyplot as plt


class RavePy:
    def __init__(self):
        self.channels = 1
        self.rate = 44100
        self.framesPerBuffer = 2048
        self.inputDeviceIndex = 0

        self.running = False
        
        self.sound = None
        self.listenThread = None

        self.beat = np.zeros((1, 512))
        self.beatFourierRange = None
        self.lastScan = 0

        self.beatTreshold = 20

        self.listenThread = None

    def start(self):
        self.running = True
        self.listenThread = threading.Thread(target=self.listen)
        self.listenThread.start()
        time.sleep(0.5)

    def stop(self):
        self.running = False
        self.listenThread.join()

    def calculateBPM(self):
        """
        Returns the frequency range and a 512 object array that contains the BPM for each frequency. 
        """
        beat = self.beat
        #print(beat)
        beat[beat != 0] = 4
        beat = np.sum(beat, axis=0)
        return self.beatFourierRange, beat

    def fourier(self, treshold, resolution):
        """
        treshold is the amount louder than average a frequency has to be registered.
        Resolution is the amount of downscaling (2 = divide by 2, 4 = divide by 4, etc)
        Returns the frequency range and the absolute value of the fourier transform.
        """
        fourierRange = np.fft.fftfreq(len(self.sound), 1.0/self.rate)
        fourierRange = fourierRange.reshape(-1, int(resolution / 2))
        fourierRange = fourierRange.sum(axis=1)
        fourierRange = fourierRange / (resolution / 2)
        fourierRange = np.array_split(fourierRange, 2)


        absolute = np.abs(np.fft.fft(self.sound)).reshape(-1, int(resolution / 2))
        absolute = absolute.sum(axis=1)
        absolute = absolute / (resolution / 2)
        absolute[absolute < np.average(absolute)*treshold] = 0
        absolute = np.array_split(absolute, 2)
        return fourierRange[0], absolute[0]

    def listen(self):
        p = pyaudio.PyAudio()
        framesPerBuffer = self.framesPerBuffer
        stream = p.open(format=pyaudio.paInt16, 
        channels=self.channels, 
        rate=self.rate, 
        input=True, 
        frames_per_buffer=self.framesPerBuffer,
        input_device_index=self.inputDeviceIndex)


        while self.running:
            data = stream.read(framesPerBuffer)
            sound = np.frombuffer(data, dtype=np.int16)
            self.sound = sound.astype(int)
            
            fourierRange, absolute = self.fourier(self.beatTreshold, 4)

            if(time.time() >= self.lastScan + 0.1):
                self.lastScan = time.time()
                self.beat = np.roll(self.beat, -1, axis=0)
                self.beat = np.vstack((self.beat, absolute))
                if(len(self.beat) > 150):
                    self.beat = np.delete(self.beat, 0, 0)
                self.beatFourierRange = fourierRange