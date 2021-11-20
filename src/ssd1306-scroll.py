"""
  scrolling display showing GPS data

  Ublox neo-7m GPS unit

  Ublox   |  Pico 
  --------+------------
  Rx      |  UART0 TX (GP0) -> pin 1
  Tx      |  UART0 RX (GP1) -> pin 2


  SSD1306 I2C LED display (0.96 inch)

  SSD1306 |  Pico
  --------+-------------
  SDA     |  I2C0 SDA (GP4) -> pin 6
  SCL     |  I2C0 SCL (GP5) -> pin 7

"""
import machine
from ssd1306 import SSD1306_I2C
import utime

sda=machine.Pin(4) # GP4, Pin 6
scl=machine.Pin(5) # GP5, Pin 7
i2c=machine.I2C(0,sda=sda, scl=scl, freq=400000)
print("Device id: {0}".format(hex(i2c.scan()[0])))

oled = SSD1306_I2C(128, 64, i2c)

comm = machine.UART(0, 9600, parity=None, stop=1, bits=8,rx=machine.Pin(1), tx=machine.Pin(0))

# Clear display
oled.fill(0)
oled.show()

while True:
    # If data is present, read the whole sentence
    if comm.any() > 0:
        line=comm.readline()
        print("> {}".format(line))
        oled.scroll(0,10)
        oled.fill_rect(0,0,128,10,0)
        oled.text(line,0,0)
        oled.show()

