#!/usr/bin/env python3
from gpiozero import Button
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text,show_message
from luma.led_matrix.device import max7219
from luma.core.legacy.font import proportional, SINCLAIR_FONT, LCD_FONT
from evdev import InputDevice, ecodes, list_devices
from signal import pause
import subprocess
import time
import os
import sys
import pexpect



def msg(txt):
        with canvas(device) as draw:
                text(draw, (0,0), txt, fill="white", font=proportional(SINCLAIR_FONT))
    
def rpi_shutdown():
    print("Shutdown now!")
    stop_braccioarm()    
    msg(" Bye !!")
    subprocess.call("sudo shutdown -h now", shell=True) 

def xbox_checkdevice():
    try:
        devices = [InputDevice(fn) for fn in list_devices()]
        d = None
        for dev in devices:
            if ('BTN_START',315) in dev.capabilities(verbose=True)['EV_KEY',1]:
                d = True
                break
        
        if d is None:
            return False
        else:
            return True
    except:
        return False


def xbox_pair_and_connect():
    stop_braccioarm() 
    pat = "Device.(.{17}).Xbox."
    msg("pair...")
    print("XBox pairing started...")
    c = pexpect.spawnu('bluetoothctl')
    c.expect("#",3)
    c.sendline("agent on")
    c.expect("#",3)
    c.sendline("default-agent")
    c.expect("#",3)
    try:
            c.sendline("devices")
            c.expect(pat,3)
            mac=c.match.group(1)
            c.sendline("remove "+mac)
            c.expect("removed",3)
    except:
            pass 

    while(True):
        try:
                print("XBox scaning...")
                c.sendline("scan on")
                c.expect(pat,30)
                mac=c.match.group(1)
                c.sendline("pair "+mac)
                c.expect("Pairing successful",10)
                print("XBox paired...")
                c.sendline("trust "+mac)
                c.expect("trust succeeded",10)
                print("XBox connecting..")
                c.sendline("connect "+mac)
                c.expect("Connection successful",10)
                print("XBox successfully connected!")
                break
        except:
                print("ones again...")



    c.sendline("quit")    
    c.kill(1)
    if xbox_checkdevice():
        msg("done !")
        time.sleep(2)
        restart_braccioarm()
    else:
        msg("error!")
        time.sleep(2)
        xbox_pair_and_connect()
    

def restart_braccioarm():
    print("restart BraccioArm")
    cmd = "sudo systemctl restart braccioarm"
    subprocess.call([cmd], shell=True)
    time.sleep(1)

def stop_braccioarm():
    print("stop BraccioArm")
    cmd = "sudo systemctl stop braccioarm"
    subprocess.call([cmd], shell=True)
    time.sleep(1)

def push_button():
    start_time=time.time()
    diff=0
    hold_time=6

    while btn.is_active and (diff <hold_time) :
        now_time=time.time()
        diff=-start_time+now_time
        #print(diff)

    if diff > hold_time:  # very long press
        rpi_shutdown()
    elif diff > (hold_time/2):  # long press
        xbox_pair_and_connect()    
    elif diff > 0.1:      # short press
        restart_braccioarm()
        time.sleep(1)


serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=4, block_orientation=-90)
device.clear()
device.contrast(128)
btn = Button(12, hold_time=0.2 ,pull_up=False)
btn.when_pressed  = push_button
restart_braccioarm()

pause()    
        