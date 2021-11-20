"""
test the micropyGPS package

"""
import machine
from ssd1306 import SSD1306_I2C
import utime
from micropyGPS import MicropyGPS
my_gps = MicropyGPS(local_offset=-14, location_formatting='dd')  # timezone for bris, lat/long in degrees decimal
sda=machine.Pin(4) # GP4, Pin 6
scl=machine.Pin(5) # GP5, Pin 7
i2c=machine.I2C(0,sda=sda, scl=scl, freq=400000)
print("Device id: {0}".format(hex(i2c.scan()[0])))

oled = SSD1306_I2C(128, 64, i2c)

comm = machine.UART(0, 9600, parity=None, stop=1, bits=8,rx=machine.Pin(1), tx=machine.Pin(0))

# Clear display
oled.fill(0)
oled.show()

count=0
fix = ["none", "2d", "3d"]
while True:
    # If data is present, read the whole sentence
    if comm.any() > 0:
        count += 1
        errorCount = 0
        
        if count > 1000:
            count = 0
        
        try:
            sentence=comm.readline().decode("utf-8")
        except:
            errorCount += 1
            continue
            
        # put in a try for decode to weed out any corrupt sentences
        
        print("> {}".format(sentence))
        for x in sentence:
            try:
                my_gps.update(x)
            except:
                errorCount += 1
                break
                
        deg = str(chr(176))
        print("Lat: {}".format(my_gps.latitude_string()))
        print("Lon: {}".format(my_gps.longitude_string()))
        print("Time:{}".format(my_gps.timestamp))
        print("Fix: {} Sats: {}".format(my_gps.fix_type,my_gps.satellites_in_use))
        oled.scroll(0,10)
        oled.fill(0)
        #oled.fill_rect(0,0,128,10,0)
        oled.text("Lat: {0} {1}".format(my_gps.latitude[0],my_gps.latitude[1]),0,0)
        oled.text("Lon: {0} {1}".format(my_gps.longitude[0],my_gps.longitude[1]),0,10)
        oled.text("Fix: {} Sats: {}".format(fix[my_gps.fix_type], my_gps.satellites_in_use),0,20)
        gpsTime = my_gps.timestamp
        oled.text("{0:02d}:{1:02d}:{2:02.0f}".format(gpsTime[0], gpsTime[1], gpsTime[2]),0,30)
        oled.text("Speed: {}".format(my_gps.speed_string('kph')),0,40)
        oled.text("{}".format(count),0,50)
        oled.show()



