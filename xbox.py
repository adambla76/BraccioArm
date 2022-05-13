#!/usr/bin/env python3

from evdev import InputDevice, ecodes, list_devices
from threading import Thread
from select import select
import time
import sys
import os
import pexpect
import signal 

class Xbox:
  def __init__(self):
    self.dev = self.xbox_detect()
    if self.dev is None:
      self.connected = False
    else:
      self.connected = True  

    self.ABS_X=[34788, 34788]
    self.ABS_Y=[-32250, -32250]
    self.ABS_Z=[35598, 35598]
    self.ABS_RZ=[-33898, -33898]
    self.ABS_GAS = [0,0]
    self.ABS_BRAKE = [0,0]
    self.ABS_HAT0X = 0
    self.ABS_HAT0Y = 0
    self.BTN_A = 0
    self.BTN_B = 0
    self.BTN_X = 0
    self.BTN_Y = 0
    self.BTN_W = 0
    self.BTN_Z = 0
    self.BTN_TL = 0
    self.BTN_TR = 0

    if self.connected:
      self.running = True
      self.t = Thread(target=self._wait_for_event, name="XBox")
      self.t.setDaemon(True)
      self.t.start()

    signal.signal(signal.SIGINT, self.keyboardInterruptHandler)

    
  def keyboardInterruptHandler(self,signal, frame):
    self.running = False
    sys.exit(0) 


  def xbox_detect(self):
    while(True):
      try:
        devices = [InputDevice(fn) for fn in list_devices()]
        d = None
        for dev in devices:
          if ('BTN_START',315) in dev.capabilities(verbose=True)['EV_KEY',1]:
            d = dev
            break
        
        if d is None:
          time.sleep(1)
        else:
          break
      except: 
        pass    
    
    print(d)
    return d    


  def getConnectedDevice(self):
    if self.connected:
      return self.dev.name  
    else:
      return None

  def setup(self):
    self.ABS_X =   [self.getInitState('ABS_X'),self.getInitState('ABS_X')]
    self.ABS_Y =   [self.getInitState('ABS_Y')*-1,self.getInitState('ABS_Y')*-1]
    self.ABS_Z =   [self.getInitState('ABS_Z'),self.getInitState('ABS_Z')]
    self.ABS_RZ =  [self.getInitState('ABS_RZ')*-1,self.getInitState('ABS_RZ')*-1]
    self.ABS_GAS = [self.getInitState('ABS_GAS'),0]
    self.ABS_BRAKE = [self.getInitState('ABS_BRAKE'),0]
    self.ABS_HAT0X = 0
    self.ABS_HAT0Y = 0
    self.BTN_A = 0
    self.BTN_B = 0
    self.BTN_X = 0
    self.BTN_Y = 0
    self.BTN_W = 0
    self.BTN_Z = 0
    self.BTN_TL = 0
    self.BTN_TR = 0


  def getInitState(self,_name):
    if self.connected:
      abs = self.dev.capabilities(verbose=True)['EV_ABS',3]
      
      for a in abs:
        if _name == a[0][0]:
          return a[1].value
          break
      else:
        return 0 
    else:
      return 0     

  def getAxis(self,name):
    d = getattr(self,name)[0] - getattr(self,name)[1]
    if name in ('ABS_GAS','ABS_BRAKE') :
      if abs(d) < 50:   # neutrum dla GAS i BRAKE 
        d = 0
    else:
      if abs(d) < 5000: # neutrum dla ABS_X, ABS_Y,ABS_Z,ABS_RZ 
        d = 0    
    
    return d  


  def getButton(self,_name):
    try:
      btn = getattr(self,_name) 
    except Exception as err:
      print("Button " + name + " not exist")
      btn = None
    return btn  

  def getAllaxis(self):
    return (self.getAxis('ABS_X'),self.getAxis('ABS_Y'),self.getAxis('ABS_Z'),self.getAxis('ABS_RZ'),self.getAxis('ABS_GAS'),self.getAxis('ABS_BRAKE'),self.ABS_HAT0X, self.ABS_HAT0Y)

  def getAllbuttons(self):
    return (self.getButton('BTN_X'),self.getButton("BTN_Y"),self.getButton("BTN_A"),self.getButton("BTN_B"),self.getButton("BTN_W"),self.getButton("BTN_Z"),self.getButton("BTN_TL"),self.getButton("BTN_TR"))

  def _wait_for_event(self):
    while self.running:
      if self.connected:
        try:
          select([self.dev], [], [])
      
          for event in self.dev.read():
            if event.type == ecodes.EV_ABS:
              if event.code == ecodes.ABS_X:
                  self.ABS_X[0] = event.value
              elif event.code == ecodes.ABS_Y:
                  self.ABS_Y[0] = event.value *-1
              elif event.code == ecodes.ABS_Z:
                  self.ABS_Z[0] = event.value 
              elif event.code == ecodes.ABS_RZ:
                  self.ABS_RZ[0] = event.value *-1
              elif event.code == ecodes.ABS_GAS:
                  self.ABS_GAS[0] = event.value 
              elif event.code == ecodes.ABS_BRAKE:
                  self.ABS_BRAKE[0] = event.value 
              elif event.code == ecodes.ABS_HAT0X:
                  self.ABS_HAT0X = event.value 
              elif event.code == ecodes.ABS_HAT0Y:
                  self.ABS_HAT0Y = event.value * -1
              
            if event.type == ecodes.EV_KEY:
              if event.code == ecodes.BTN_C:
                  self.BTN_X = event.value
              elif event.code == ecodes.BTN_EAST:
                  self.BTN_B = event.value
              elif event.code == ecodes.BTN_NORTH:
                  self.BTN_Y = event.value
              elif event.code == ecodes.BTN_SOUTH:
                  self.BTN_A = event.value
              elif event.code == ecodes.BTN_WEST:
                  self.BTN_W = event.value
              elif event.code == ecodes.BTN_Z:
                  self.BTN_Z = event.value
              elif event.code == ecodes.BTN_TL:
                  self.BTN_TL = event.value
              elif event.code == ecodes.BTN_TR:
                  self.BTN_TR = event.value
                    
        except OSError as e:
          print("Xbox gamepad disconnected!")
          self.connected = False 
          self.running = False 
      else:
        self.connected = False
        self.running = False 
        

if __name__ == '__main__':
  try:
    r = Xbox()
    time.sleep(1)
    if r.connected:
      r.setup()
      while r.running:
        print('AXES: ',r.getAllaxis(),'    BUTTONS: ',r.getAllbuttons())
        time.sleep(0.2)

  except:
    print("Xbox gamepad not found")
  
  
