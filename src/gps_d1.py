"""
 Support switching pages on a screen using a button and interrupt

 3 pages
 
 - added nmea scrolling output
 - added splash screen with i2c id's


 * * ** * * * * * ** * * * * * * * * * 
"""
import machine
import utime as time

# set up SSD1306 screen
sda=machine.Pin(4) # GP4, Pin 6
scl=machine.Pin(5) # GP5, Pin 7

i2c=machine.I2C(0,sda=sda, scl=scl, freq=400000)
#print("Device id: {0}".format(hex(i2c.scan())))
from ssd1306 import SSD1306_I2C
oled = SSD1306_I2C(128, 64, i2c)


# set up UART for GPS
comm = machine.UART(0, 9600, parity=None, stop=1, bits=8,rx=machine.Pin(1), tx=machine.Pin(0))

pageNo = 1 # page number to display
currPageNo = 3 # current page number
# set up button
btn = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
lastIntTime = time.ticks_ms()

# set up interrupt function
def int_handler(pin):
    btn.irq(handler=None)
    global pageNo
    global lastIntTime

    # software switch debounce, wait 200ms before actioning another interrupt
    currTime = time.ticks_ms()
    print(time.ticks_diff(currTime,lastIntTime))
    if time.ticks_diff(time.ticks_ms(),lastIntTime) < 300:
        print("nope, still within 300ms")
    else:
        #do stuff here
        print("interrupt fired")
        lastIntTime = time.ticks_ms()
        pageNo = pageNo + 1
        if pageNo > 3:
            pageNo = 1
    
    btn.irq(handler=int_handler)
   
# bind interrupt to pin
btn.irq(trigger=machine.Pin.IRQ_RISING, handler=int_handler)

# set up display
oled.fill(0)
oled.text("Page {}".format(pageNo),0,0)
oled.show()


# help function if page number has changed
def pageChanged():
    global currPageNo
    global pageNo
    
    rc = False
    if (currPageNo != pageNo):
        rc = True
    return rc 

# Main page
def pageOne():
    print("pageOne()")
    oled.fill(0)
    oled.text("  === MAIN ===",0,0)
    oled.show()
    count = 0
    while (pageChanged() == False):
        #print("count")
        oled.fill_rect(0,10,128,20,0)
        oled.text(str(count),0,10)
        oled.show()
        count += 10
        if count > 10000:
            count = 0
        
# NMEA sentences
def pageTwo():
    print("pageTwo()")
    oled.fill(0)
    oled.show()
    while (pageChanged() == False):
        #print("count")
        if comm.any() > 0:
            oled.scroll(0,10)
            oled.fill_rect(0,0,128,20,0)
            oled.text("  === NMEA ===",0,0)
            oled.text(comm.readline(),0,10)
            oled.show()

# Satellite tracking
def pageThree():
    print("pageThree()")
    oled.fill(0)
    oled.text("  === EXTRA ===",0,0)
    oled.show()
    count = 0
    while (pageChanged() == False):
        #print("count")
        oled.fill_rect(0,10,128,20,0)
        oled.text(str(count),0,10)
        oled.show()
        count += 50
        if count > 10000:
            count = 0

# * * * * * main code * * * * *

#splash screen
oled.fill(0)
oled.text("GPS 0.1",0,0)
print("I2C id:")
oled.text("I2C id:",0,20)
devices = i2c.scan()
for n, id in enumerate(devices):
  print("{0}".format(hex(id)))
  oled.text(" {0}".format(hex(id)),0,30+(n*10))
oled.show()
time.sleep(5)

while True:
    # has page changed
    if (pageChanged()):
        print("Page has changed to page {}".format(pageNo))
        
        # action page change
        if pageNo == 1:
            currPageNo = pageNo
            pageOne()
        elif pageNo == 2:
            currPageNo = pageNo
            pageTwo()
        elif pageNo == 3:
            currPageNo = pageNo
            pageThree()
        else:
            # pageNo value is invalid
            print("Error: pageNo={}".format(pageNo))
            pageNo = 0
        
        

