#!/usr/bin/env python3
#
#           Braccio Arm v2.13
#
#        (c) AdamBla76@gmail.com
#
#       werja dla Raspberry Pi 3B+ 
#


from PCA9685 import *
from threading import Timer 
from xbox import Xbox
#from keyboard import *
import signal 
import time 
import pexpect
import sys
import os
import tty, termios
import socket 
import glob 
import pickle 
import select
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi,noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, SINCLAIR_FONT, LCD_FONT

SPEED  = 1
DELAY  = 0.5
PARAMS = [SPEED,DELAY,0,0,0,0]
HOME = [100,75,90,90,0,32]
JOINT = {'base': 0, 'shoulder': 1, 'elbow': 2, 'wrist': 3, 'rotation': 4, 'gripper': 5}
debug = 0

bannerL0  = " \x1b[0;1;35;95m_\x1b[0;1;31;91m__\x1b[0m                     \x1b[0;1;35;95m_\x1b[0m         \x1b[0;1;34;94m_\x1b[0m"   
bannerL1  = "\x1b[0;1;31;91m|\x1b[0m \x1b[0;1;33;93m_\x1b[0m \x1b[0;1;32;92m"
bannerL1 += ")\x1b[0m \x1b[0;1;36;96m_\x1b[0m \x1b[0;1;34;94m_\x1b[0m  \x1b[0;1;35;95m_\x1b[0;1;31;91m_\x1b[0m \x1b[0;1;"
bannerL1 += "33;93m_\x1b[0m  \x1b[0;1;32;92m_\x1b[0;1;36;96m_\x1b[0m  \x1b[0;1;34;94m_\x1b[0;1;35;95m_\x1b[0m \x1b[0;"
bannerL1 += "1;31;91m(_\x1b[0;1;33;93m)\x1b[0m \x1b[0;1;32;92m__\x1b[0;1;36;96m_\x1b[0m   \x1b[0;1;35;95m/_\x1b[0;"
bannerL1 += "1;31;91m\\\x1b[0m   \x1b[0;1;32;92m_\x1b[0m \x1b[0;1;36;96m_\x1b[0m  \x1b[0;1;34;94m_\x1b[0m \x1b[0;1;35;"
bannerL1 += "95m_\x1b[0;1;31;91m_\x1b[0m"
bannerL2  = "\x1b[0;1;33;93m|\x1b[0m \x1b[0;1;32;92m_\x1b[0m \x1b[0;1;36;96m\\|\x1b[0m \x1b"
bannerL2 += "[0;1;34;94m'\x1b[0;1;35;95m_|\x1b[0;1;31;91m/\x1b[0m \x1b[0;1;33;93m_`\x1b[0m \x1b[0;1;32;92m|\x1b[0;"
bannerL2 += "1;36;96m/\x1b[0m \x1b[0;1;34;94m_|\x1b[0;1;35;95m/\x1b[0m \x1b[0;1;31;91m_|\x1b[0;1;33;93m|\x1b[0m \x1b["
bannerL2 += "0;1;32;92m|/\x1b[0m \x1b[0;1;36;96m_\x1b[0m \x1b[0;1;34;94m\\\x1b[0m \x1b[0;1;35;95m/\x1b[0m \x1b[0;1;31;"
bannerL2 += "91m_\x1b[0m \x1b[0;1;33;93m\\\x1b[0m \x1b[0;1;32;92m|\x1b[0m \x1b[0;1;36;96m'\x1b[0;1;34;94m_|\x1b[0;1;35"
bannerL2 += ";95m|\x1b[0m \x1b[0;1;31;91m'\x1b[0m  \x1b[0;1;33;93m\\\x1b[0m"
bannerL3  = "\x1b[0;1;32;92m|_\x1b[0;1;36;96m__\x1b[0;"
bannerL3 += "1;34;94m/|\x1b[0;1;35;95m_|\x1b[0m  \x1b[0;1;33;93m\\_\x1b[0;1;32;92m_,\x1b[0;1;36;96m_|\x1b[0;1;34"
bannerL3 += ";94m\\_\x1b[0;1;35;95m_|\x1b[0;1;31;91m\\_\x1b[0;1;33;93m_|\x1b[0;1;32;92m|_\x1b[0;1;36;96m|\\\x1b[0;"
bannerL3 += "1;34;94m__\x1b[0;1;35;95m_/\x1b[0;1;31;91m/_\x1b[0;1;33;93m/\x1b[0m \x1b[0;1;32;92m\\_\x1b[0;1;36;9"
bannerL3 += "6m\\|\x1b[0;1;34;94m_|\x1b[0m  \x1b[0;1;31;91m|_\x1b[0;1;33;93m|_\x1b[0;1;32;92m|_\x1b[0;1;36;96m|\x1b"
bannerL3 += "[0m"

class Motor():
    def __init__(self, _pwm, _id,_pos, _ax=2000, _bx=500,_minpos = 0, _maxpos=180):
        self.pwm = _pwm 
        self.id = _id
        self.maxpos = _maxpos
        self.minpos = _minpos
        self.currpos = _pos
        self.destpos = _pos
        self.ax = _ax
        self.bx = _bx
        self.dir = 1
        self.moving = False
        self.pwm.setServoPulse(self.id,self.getduty(self.currpos))
    
    def getduty(self,pos):
        return round(self.ax*pos/180 + self.bx,0)    
            
    def setpos(self,_pos,_inv=False):
        if self.currpos != _pos:
            if _inv:
                _pos*=-1

            if _pos > self.currpos:
                self.dir = 1
            else:
                self.dir = -1

            if _pos > self.maxpos:
                self.destpos = self.maxpos
            elif _pos < self.minpos:
                self.destpos = self.minpos
            else:    
                self.destpos = _pos
            self.moving = True
        else:
            self.moving = False
        
    def changepos(self,delta,_inv=False):
        if _inv:
            delta*=-1     
        self.setpos(self.destpos+delta)

    def run(self):
        if self.moving:
            if self.dir == 1 and self.currpos < self.destpos:
                self.currpos += 1
                if self.currpos > self.destpos:
                    self.currpos = self.destpos
            elif self.dir == -1 and self.currpos > self.destpos:
                self.currpos -= 1     
                if self.currpos < self.destpos:
                    self.currpos = self.destpos       
            else:
                self.currpos = self.destpos
                self.moving = False

            self.pwm.setServoPulse(self.id,self.getduty(self.currpos))
            
            if debug:
                txt = "motor=%s ang=%s duty=%s" % (self.id, self.currpos, self.getduty(self.currpos))
                print(txt)
            

class Braccio():
    def __init__(self):
        self.state = 'run'
        self.speed = 0.02  # interwal czasu sterowania serwo-motorami
        self.inverse = False
        self.pwm = PCA9685()
        self.pwm.setPWMFreq(50)
        self.motors = [None,None,None,None,None,None]
        self.motors[0] = Motor(self.pwm,0,100)
        self.motors[1] = Motor(self.pwm,1,75,2010,640)
        self.motors[2] = Motor(self.pwm,2,90,2000,460) 
        self.motors[3] = Motor(self.pwm,3,90)
        self.motors[4] = Motor(self.pwm,4,0)
        self.motors[5] = Motor(self.pwm,5,32,_minpos=32, _maxpos=85) 
        signal.signal(signal.SIGINT, self.keyboardInterruptHandler)

        print("Robot Braccio just has been born!")
        self.motorcontrol()

    def keyboardInterruptHandler(self,signal, frame):
        r.state='stop'
        r.gohome()
        LCD_ShowText("Bye !!",3)
        time.sleep(2)
        exit(0)

    def gohome(self):
        #print("Robot Braccio just comming back home!")
        self.motors[JOINT['base']].setpos(HOME[JOINT['base']])
        self.motors[JOINT['shoulder']].setpos(HOME[JOINT['shoulder']])
        self.motors[JOINT['elbow']].setpos(HOME[JOINT['elbow']])
        self.motors[JOINT['wrist']].setpos(HOME[JOINT['wrist']])
        self.motors[JOINT['rotation']].setpos(HOME[JOINT['rotation']])
        self.motors[JOINT['gripper']].setpos(HOME[JOINT['gripper']])
        time.sleep(0.5)
        while(self.movedone() != True): # czekam na zakończenie ruchu robota
            pass

    def readGamepad(self):
        keycode = 0        
        abs_x = g.getAxis('ABS_X') 
        
        if  abs_x > 15000:
            keycode = ord('Q') 
        elif  abs_x > 5000:
            keycode = ord('q') 
        elif abs_x < -15000:
            keycode = ord('A')
        elif abs_x < -5000:
            keycode = ord('a')

        abs_z = g.getAxis('ABS_Z')             
        if  abs_z > 25000:
            keycode = ord('T')
        elif  abs_z > 10000:
            keycode = ord('t')  
        elif abs_z < -25000:
            keycode = ord('G')
        elif abs_z < -10000:
            keycode = ord('g')

        abs_rz = g.getAxis('ABS_RZ')             
        if  abs_rz > 25000:
            keycode = ord('Y')
        elif  abs_rz > 10000:
            keycode = ord('y')  
        elif abs_rz < -25000:
            keycode = ord('H')
        elif abs_rz < -10000:
            keycode = ord('h')

        abs_y = g.getAxis('ABS_Y')
        abs_gas = g.getAxis('ABS_GAS') 
        abs_brake = g.getAxis('ABS_BRAKE') 
        
        if abs_gas == 0 and abs_brake == 0:
            if  abs_y > 25000:
                keycode = ord('W') 
            elif  abs_y > 10000:
                keycode = ord('w') 
            elif abs_y < -25000:
                keycode = ord('S') 
            elif abs_y < -10000:
                keycode = ord('s') 
        elif abs_gas == 0 and abs_brake > 500:
            if  abs_y > 25000:
                keycode = ord('E') 
            elif  abs_y > 10000:
                keycode = ord('e') 
            elif abs_y < -25000:
                keycode = ord('D') 
            elif abs_y < -10000:
                keycode = ord('d') 
        elif abs_gas > 500:
            if  abs_y > 25000:
                keycode = ord('R') 
            elif  abs_y > 10000:
                keycode = ord('r') 
            elif abs_y < -25000:
                keycode = ord('F') 
            elif abs_y < -10000:
                keycode = ord('f') 
    
        if g.getButton('BTN_Y'):
            keycode = ord('m')    # gohome
   
        if g.getButton('BTN_A'):
            keycode = 32          # save position in seq 
   
        if g.getButton('BTN_TL'):
            keycode = ord('b')          # clear seq & gohome 

        if g.getButton('BTN_TR'):
            keycode = ord('i')          # change inverse motors 

        if g.getButton('BTN_B'):
            keycode = ord('p')          # clear seq & gohome 

        if g.ABS_HAT0Y == 1:
            keycode = ord('z')          # first step in seq 

        if g.ABS_HAT0Y == -1:
            keycode = ord('v')          # last step in seq 

        if g.ABS_HAT0X == 1:
            keycode = ord('c')          # next step in seq 

        if g.ABS_HAT0X == -1:
            keycode = ord('x')          # prev step in seq 

        return keycode


    def getposition(self):
        p = [self.motors[id].destpos for id in range(6)]
        return p

    def setposition(self,pos,force=False):
            
        if force==False:
            while(self.movedone() != True): # czekam na zakończenie poprzedniego ruchu
                pass
        if len(pos)==6:
            for id in range(6):
                self.motors[id].setpos(pos[id])
        else:
            print("setposition: args error!")

    def motorcontrol(self):
        if self.movedone() and self.state != 'run':
            self.state = 'shutdown'
        else:    
            self.timer = Timer(self.speed,self.motorcontrol).start()
            for m in self.motors:
                m.run()

    def movedone(self):
        if self.motors[0].moving or self.motors[1].moving or self.motors[2].moving or self.motors[3].moving or self.motors[4].moving or self.motors[5].moving:
            return False
        else:
            return True  

class Sequencer():
    def __init__(self,_robot):
        self.filename = 'unnamed.seq'
        self.positionId = 0
        self.positions = []
        self.robot = _robot
        self.clear()
        
    def add(self,pos):
        self.positions.append(pos) 

    def insert(self,pos):
        self.positions.insert(s.positionId, pos) 

    def clear(self):
        self.positions = []
        self.positions.append(PARAMS)
        self.positions.append(HOME)        
        self.positions.append(HOME)        
        self.positionId = 2

    def change(self,id,pos):
        if id>=1:
            self.positions[id] = pos 

    def getlist(self):
        lst = ""
        for id in range(len(self.positions)):
            lst += "%s: %s\n" % (id, self.positions[id])
        if len(lst)==0:
            print("empty")
        else:
            print(lst)

    def set(self,id):
        if id <= len(self.positions):
            self.robot.setposition(self.positions[id])

    def play(self):
        if len(self.positions) > 2:
            delay = self.positions[0][1]
            s.positionId = 1
            for pos in self.positions[1:]:
                ShowInfo()
                t = str(s.positionId)
                if len(t)==1:
                    t='0'+t
                LCD_ShowText(t,10)
                s.positionId+=1
                self.robot.setposition(pos)
                time.sleep(delay)
            s.positionId-=1

    def savetofile(self):
        printxy(10,22, "                                                                  ")
        gotoxy(10,22)
        SetColor(15)
        s.filename = input("file name [%s]: " % (s.filename)) or s.filename 
        if os.path.splitext(s.filename)[1] != '.seq':
            s.filename += '.seq'
        with open(s.filename,"wb") as fp:
            pickle.dump(s.positions,fp)
        printxy(10,22, "File " + s.filename + " has been saved!          ")

    def loadfile(self):
        filelist = glob.glob('*.seq')
        filelist.sort()
        if len(filelist) > 0:
            id = 0
            while True:
                printxy(10,22, "file to load: " + filelist[id]+ "           ")
                sys.stdout.write("\r")
                keycode = k.keycode()
                if (keycode == 68 or keycode == 65) and id > 0:                 # arrow left / up
                    id-=1 
                elif (keycode == 67 or keycode == 66) and id < len(filelist)-1: # arrow right / down
                    id+=1                
                elif keycode == 10:                                             # key ENTER           
                    with open(filelist[id],"rb") as fp:
                        s.positions = pickle.load(fp)
                        printxy(10,22, "File " + filelist[id]+ " has been loaded!          ")
                    break
                elif keycode == 113:                                            # key q
                    printxy(10,22, "                                                          ")
                    break    
         


def get_lock(process_name):
    get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        get_lock._lock_socket.bind('\0' + process_name)
    except socket.error:
        print('BraccioArm is busy! Come back later!')
        sys.exit()



def printxy(x, y, text):
     sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (y, x, text))
     sys.stdout.flush()

def gotoxy(x, y):
    sys.stdout.write("\x1b[%d;%dH" % (y,x))
    sys.stdout.flush()

def clearscr():
    sys.stderr.write("\x1b[2J\x1b[H")
    sys.stderr.flush()


def getch_old():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def SetColor(colorID):
    sys.stderr.write("\x1b[38;5;" + str(colorID) + "m")
    sys.stderr.flush()

def ShowMenu():
    clearscr()
#   sys.stdout.write(banner)
#   sys.stdout.flush()

#   SetColor(10)
    printxy(15,2, bannerL0)
    printxy(15,3, bannerL1)
    printxy(15,4, bannerL2)
    printxy(15,5, bannerL3)
    
    SetColor(11)    
    printxy(10,8, "POS    BASE   SHOULDER   ELBOW    WRIST    ROTATOR    GRIPPER")
    SetColor(15); printxy(10,12, "rotate base"); SetColor(10); printxy(33,12,"[q/a]") 
    SetColor(15); printxy(10,13, "rotate shoulder"); SetColor(10); printxy(33,13,"[w/s]") 
    SetColor(15); printxy(10,14, "rotate elbow"); SetColor(10); printxy(33,14,"[e/d]") 
    SetColor(15); printxy(10,15, "rotate wrist"); SetColor(10); printxy(33,15,"[r/f]") 
    SetColor(15); printxy(10,16, "rotate rotator"); SetColor(10); printxy(33,16,"[t/g]") 
    SetColor(15); printxy(10,17, "change gripper"); SetColor(10); printxy(33,17,"[y/h]")     
    SetColor(15); printxy(10,18, "next/prev  position"); SetColor(10); printxy(33,18,"[x/c]") 
    SetColor(15); printxy(10,19, "first/last position"); SetColor(10); printxy(33,19,"[z/v]")
    SetColor(15); printxy(10,20, "save position"); SetColor(10); printxy(32,20,"[space]")
    SetColor(15); printxy(45,12, "inverse mode"); SetColor(10); printxy(68,12,"[i]")
    SetColor(15); printxy(45,13, "clear scene"); SetColor(10); printxy(68,13,"[b]")
    SetColor(15); printxy(45,14, "play scene"); SetColor(10); printxy(68,14,"[p]")
    SetColor(15); printxy(45,15, "arm go home"); SetColor(10); printxy(68,15,"[m]")
    SetColor(15); printxy(45,16, "load scene from file"); SetColor(10); printxy(68,16,"[L]")
    SetColor(15); printxy(45,17, "save scene to file"); SetColor(10); printxy(68,17,"[K]")
    
def ShowInfo():
    SetColor(15)
    printxy(10,9,  str(s.positionId)+ "/" + str(len(s.positions)-1) + "    ")
    printxy(18,9,  str(r.motors[0].destpos) + "    ")
    printxy(27,9,  str(r.motors[1].destpos) + "    ")
    printxy(36,9,  str(r.motors[2].destpos) + "    ")
    printxy(45,9,  str(r.motors[3].destpos) + "    ")
    printxy(56,9,  str(r.motors[4].destpos) + "    ")
    printxy(67,9,  str(r.motors[5].destpos) + "    ")
    if g.connected:
        SetColor(2); printxy(45,20,"   Gamepad Connected!                     ")
    else:
        SetColor(5); printxy(45,20," Gamepad Disconnected!                  ")
    if s.robot.inverse:
        SetColor(2); printxy(45,19,"    Inverse Movement                     ")
    else:
        SetColor(2); printxy(45,19,"                        ")

def RunCommand():
    ShowMenu()
    ShowInfo()

    while True:
        kc1 = 0 #k.key
        keycode = kc1
        if g.connected:
            kc2 = s.robot.readGamepad()
        else:
            kc2 = 0
        if kc1>0:
            keycode = kc1
        elif kc2>0:
            keycode = kc2

        SetColor(0);
        printxy(1,1,"                                                                                 ")
        sys.stdout.write("\r")                    
        SetColor(15);
        if keycode == ord('Q'):       # key Q
            #LCD_ShowText('BS: R',2)
            r.motors[0].changepos(2,r.inverse)
        elif keycode == ord('q'):       # key q
            #LCD_ShowText('BS: R',2)
            r.motors[0].changepos(1,r.inverse)
        elif keycode == ord('A'):     # key A
            #LCD_ShowText('BS: L',2)
            r.motors[0].changepos(-2,r.inverse)
        elif keycode == ord('a'):     # key A
            #LCD_ShowText('BS: L',2)
            r.motors[0].changepos(-1,r.inverse)
        elif keycode == ord('W'):     # key w
            #LCD_ShowText('SH: D',2)
            r.motors[1].changepos(2,r.inverse)    
        elif keycode == ord('w'):     # key w
            #LCD_ShowText('SH: D',2)
            r.motors[1].changepos(1,r.inverse)
        elif keycode == ord('S'):     # key s
            #LCD_ShowText('SH: U',2)
            r.motors[1].changepos(-2,r.inverse)
        elif keycode == ord('s'):     # key s
            #LCD_ShowText('SH: U',2)
            r.motors[1].changepos(-1,r.inverse)
        elif keycode == ord('E'):     # key E
            #LCD_ShowText('EB: D',2)
            r.motors[2].changepos(2,r.inverse)   
        elif keycode == ord('e'):     # key e
            #LCD_ShowText('EB: D',2)
            r.motors[2].changepos(1,r.inverse)
        elif keycode == ord('D'):     # key D
            #LCD_ShowText('EB: U',2)
            r.motors[2].changepos(-2,r.inverse)
        elif keycode == ord('d'):     # key d
            #LCD_ShowText('EB: U',2)
            r.motors[2].changepos(-1,r.inverse)
        elif keycode == ord('R'):     # key R
            #LCD_ShowText('WR: D',2)
            r.motors[3].changepos(2,r.inverse)
        elif keycode == ord('r'):     # key r
            #LCD_ShowText('WR: D',2)
            r.motors[3].changepos(1,r.inverse)
        elif keycode == ord('F'):     # key F
            #LCD_ShowText('WR: U',2)
            r.motors[3].changepos(-2,r.inverse) 
        elif keycode == ord('f'):     # key f
            #LCD_ShowText('WR: U',2)
            r.motors[3].changepos(-1,r.inverse)
        elif keycode == ord('T'):     # key T
            #LCD_ShowText('RT: R',2)
            r.motors[4].changepos(-2,r.inverse)   
        elif keycode == ord('t'):     # key t
            #LCD_ShowText('RT: R',2)
            r.motors[4].changepos(-1,r.inverse)
        elif keycode == ord('G'):     # key G
            #LCD_ShowText('RT: L',2)
            r.motors[4].changepos(2,r.inverse)
        elif keycode == ord('g'):     # key g
            #LCD_ShowText('RT: L',2)
            r.motors[4].changepos(1)
        elif keycode == ord('Y'):     # key Y
            #LCD_ShowText('GR: C',2)
            r.motors[5].changepos(2)
        elif keycode == ord('y'):     # key y
            #LCD_ShowText('GR: C',2)
            r.motors[5].changepos(1)
        elif keycode == ord('H'):     # key H
            #LCD_ShowText('GR: O',2)
            r.motors[5].changepos(-2)       
        elif keycode == ord('h'):     # key h
            #LCD_ShowText('GR: O',2)
            r.motors[5].changepos(-1)
        elif keycode == ord('p'):     # key p
            LCD_ShowText('PLAY',2)
            time.sleep(1)
            s.play()
            LCD_ShowText('STOP',2)
        elif keycode == ord('L'):     # key L
            s.loadfile()        
        elif keycode == ord('x'):     # key x
            if s.positionId>1:
                s.positionId -= 1
                t = str(s.positionId)
                if len(t)==1:
                    t='0'+t
                LCD_ShowText(t,10)
                s.robot.setposition(s.positions[s.positionId])
                time.sleep(0.5)
        elif keycode == ord('c'):     # key c
            if s.positionId<len(s.positions)-1:
                s.positionId += 1
                t = str(s.positionId)
                if len(t)==1:
                    t='0'+t
                LCD_ShowText(t,10)
                s.robot.setposition(s.positions[s.positionId])
                time.sleep(0.5)
        elif keycode == ord('z'):     # key z
            s.positionId = 1
            t = str(s.positionId)
            if len(t)==1:
                t='0'+t
            LCD_ShowText(t,10)
            s.robot.setposition(s.positions[s.positionId])
        elif keycode == ord('v'):     # key v
            s.positionId = len(s.positions)-1
            t = str(s.positionId)
            if len(t)==1:
                t='0'+t
            LCD_ShowText(t,10)
            s.robot.setposition(s.positions[s.positionId])
        elif keycode == 32:           # key space
            if s.positions[s.positionId-1] != s.positions[s.positionId]:
                if s.positionId == len(s.positions)-1:
                    s.add(s.positions[s.positionId])
                else:
                    s.insert(s.positions[s.positionId])
                s.positionId+=1
                t = str(s.positionId)
                if len(t)==1:
                    t='0'+t
                LCD_ShowText('SAVE',2)
                time.sleep(0.5)
                LCD_ShowText(t,10)
        elif keycode == ord('b'):     # key b
            s.clear() 
            s.robot.gohome()       
            LCD_ShowText('Clear',2)    
        elif keycode == ord('m'):     # key m
            s.robot.gohome() 
        elif keycode == ord('i'):     # key i
            s.robot.inverse = not s.robot.inverse
            if s.robot.inverse:
                LCD_ShowText('Invert',0)
            else:
                LCD_ShowText('Normal',0)    
            time.sleep(1) 
        elif keycode == ord('K'):     # key K
            s.savetofile() 
        elif keycode == 3:            # CTRL-C
            break
        else:
            pass
            #printxy(1,44,"KEYCODE: "+ str(keycode) + "  ")

        if s.positionId <= len(s.positions)-1:
            s.positions[s.positionId] = s.robot.getposition()
            ShowInfo()
        
        time.sleep(0.05)

def LCD_ShowMessage(txt):
    show_message(device, txt, fill="white", font=proportional(SINCLAIR_FONT), scroll_delay=0.08)        


def LCD_ShowText(txt,ofs=0):
    with canvas(device) as draw:
        text(draw, (ofs, 0), txt, fill="white", font=proportional(SINCLAIR_FONT))

#get_lock('BraccioArm')
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=4, block_orientation=-90)

if __name__=='__main__':
    try:
        LCD_ShowText("wait...") 
        g = Xbox()
        LCD_ShowMessage(" >> BraccioArm << ") 
        r = Braccio()
        s = Sequencer(r)
        LCD_ShowText("Ready",1)
        RunCommand()    
    finally:
        #r.state='stop'
        #r.gohome()
        clearscr()
        print("BYE BYE!!!")
