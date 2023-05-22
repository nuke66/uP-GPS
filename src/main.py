"""
main.py

Support setting switch to change program running on board


"""
import machine
#import utime as time

# set up button
Upbtn = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_DOWN)  
Downbtn = machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_DOWN)

if (Upbtn.value()):
    print("button pressed")
    import gps_d1
elif (Downbtn.value()):
    print ("button two pressed")
    import test
else:
    print("normal execution")
    import test_menu
