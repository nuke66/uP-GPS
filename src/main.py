"""
main.py

Support setting switch to change program running on board


"""
import machine
#import utime as time

# set up button
Upbtn = machine.Pin(8, machine.Pin.IN, machine.Pin.PULL_DOWN)  #TODO update pin number

print("button value:{}".format(Upbtn.value())) #debug
if (Upbtn.value()):
    print("button pressed")
    import gps_d1
else:
    print("normal execution")
    import test_menu