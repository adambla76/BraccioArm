import os
import sys
import termios
import atexit
import time
from select import select
from threading import Thread


class Keyboard:
    def __init__(self):
        self.key = 0
        self.scan = 1
        self.t = None

        # Save the terminal settings
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)

        # New terminal setting unbuffered
        self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

        # Support normal-terminal reset at exit
        atexit.register(self.set_normal_term)
        self.t = Thread(target=self.watch_keys, name="kbd")
        self.t.setDaemon(True)
        self.t.start()
    
    def __del__(self):
        self.scan = 0
        self.set_normal_term()

    def watch_keys(self):
        while(self.scan):
            if self.kbhit(): #If a key is pressed:
                self.key = self.keycode()
                #termios.tcflush(sys.stdin, termios.TCIOFLUSH)
                termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)
            else:
                self.key = 0                
            time.sleep(0.1)



    def set_normal_term(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)


    def getch(self):
        return sys.stdin.read(1)


    def keycode(self):
        c = self.getch()
        return ord(c)


    def getarrow(self):
        ''' Returns an arrow-key code after kbhit() has been called. Codes are
        0 : up
        1 : right
        2 : down
        3 : left
        Should not be called in the same program as getch().
        '''
        c = sys.stdin.read(3)[2]
        vals = [65, 67, 66, 68]
        return vals.index(ord(c.decode('utf-8')))


    def kbhit(self):
        ''' Returns True if keyboard character was hit, False otherwise.
        '''
        dr,dw,de = select([sys.stdin], [], [], 0)
        return dr != []

    


