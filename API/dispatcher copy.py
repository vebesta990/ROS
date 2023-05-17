import tkinter as tk
import time
from acclerometerClass import *
from gyroscopeClass import *
from magnitometrClass import *
from DatasetClass import *
from lidarClass import *
from PointClass import *
from dataHandler import *
from cameraClass import *
import subprocess
from smbus import SMBus
import math
import os
from threading import Thread
import re

class Dispatcher():
    #SensorMass = []
    def __init__(self):
        self.Dataset = Dataset([], 0, 0, 0)
        self.AcclMass = []
        self.GyroMass = []
        self.MagnMass = []
        self.LidarMass = []
        self.CameraMass = []
        self.SensorMass = []
        self.SensorMass.append(("Accelerometer_pin", '53'))
        self.SensorMass.append(("Magnitometer_pin", '1e'))
        self.SensorMass.append(("Gyroscope_pin", '68'))
        self.SensorMass.append(("Lidar_usb", '15d1:0000'))
        self.SensorMass.append(("Camera_usb", '0c45:6340'))
        
    def AddAccelerometer(self, register:int, rate:float):
        accelerometer = Accelerometer(register)
        accelerometer.SetMeasurementRate(rate)
        self.AcclMass.append(accelerometer)

    def AddGyro(self, register:int, rate:float):
        Gyro = Gyroscope(register)
        Gyro.SetMeasurementRate(rate)
        self.GyroMass.append(Gyro)

    def AddMagnitometer(self, register:int, rate:float):
        magnitometer = Magnitometr(register)
        magnitometer.SetMeasurementRate(rate)
        self.MagnMass.append(magnitometer)

    def AddLidar(self, port:str, speed:int, rate:float):
        lidar = Lidar(port, speed)
        lidar.SetMeasurementRate(rate)
        self.LidarMass.append(lidar)

    def AddCamera(self, port:int):
        camera = Camera(port)
        self.CameraMass.append(camera)
        pass


    def StartThreads(self):
        def Accl(accl):
            while True:
                time.sleep(1/accl.measurement_rate)
                xAccl, yAccl, zAccl = accl.GetMeasurementData()
                #print(xAccl, yAccl, zAccl)
                roll = DataHandler.GetRoll(yAccl, zAccl)
                pitch = DataHandler.GetPitch(xAccl, yAccl, zAccl)
                #yaw = DataHandler.TestYaw(xAccl, yAccl, zAccl)
                #print(yaw)
                #print('Roll pitch',roll, pitch)
                self.Dataset.Roll = roll
                self.Dataset.Pitch = pitch

        def Gyro(gyro):
            while True:
                time.sleep(1/gyro.measurement_rate)
                xGyro, yGyro, zGyro = gyro.GetMeasurementData()
                #print('Gyro', xGyro, yGyro, zGyro)
                
        def Magn(magn):
            while True:
                time.sleep(1/magn.measurement_rate+1)
                xMagn, yMagn, zMagn = magn.GetMeasurementData()
                yaw = DataHandler.GetYaw(xMagn, yMagn)
                yaw = DataHandler.TestYaw2(xMagn, yMagn, zMagn, self.Dataset.Roll, self.Dataset.Pitch)
                #print('Magnitometer', xMagn, yMagn, zMagn, yaw)
                self.Dataset.Yaw = yaw

        def Lidar(lidar):
            while True:
                time.sleep(1/lidar.measurement_rate)
                lidar_arr = lidar.GetMeasurementData()
                points_arr = []
                for i in lidar_arr:
                    angle = i[0]
                    distance = i[1]
                    x, y = DataHandler.GetCoordinates(distance, angle)
                    point = Point(x, y, distance, angle)
                    #print(angle, distance, x, y)
                    points_arr.append(point)
                self.Dataset.Points = points_arr
                
        def Camera(camera):
            camera.StartStreaming()
            
        
        self.Threads = []
        for i in self.AcclMass:
            thread = Thread(target = Accl, args=(i,)) 
            self.Threads.append(thread)
        self.AcclMass = []
        for i in self.GyroMass:
            thread = Thread(target = Gyro, args=(i,))
            self.Threads.append(thread)
        self.GyroMass = []
        for i in self.MagnMass:
            thread = Thread(target = Magn, args=(i,))
            self.Threads.append(thread)
        self.MagnMass = []
        for i in self.LidarMass:
            thread = Thread(target = Lidar, args=(i,))
            self.Threads.append(thread)
        self.LidarMass = []
        for i in self.CameraMass:
            thread = Thread(target = Camera, args=(i,))
            self.Threads.append(thread)
        self.CameraMass = []

        for i in self.Threads:
            i.start()
   
dispatcher = Dispatcher()
#dispatcher.GetSensors()
#dispatcher.CheckSensor("Accelerometer_pin", "Lidar_usb")
#dispatcher.AddSensor("camera2_usb", "046d:082d")
#dispatcher.CheckSensor("camera2_usb")
#dispatcher.RemoveSensor("camera2_usb")

#dispatcher.AddCamera(0)
dispatcher.AddAccelerometer(0x53, 1)
#dispatcher.AddAccelerometer(0x53, 0.2)
#dispatcher.AddGyro(0x68, 1)
dispatcher.AddMagnitometer(0x1e, 1)
#dispatcher.AddLidar('/dev/ttyACM0', 19200, 10)
dispatcher.StartThreads()
#exit()    

