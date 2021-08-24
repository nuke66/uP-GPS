"""
 Test for making a settings menu 14Mar21
 
 4 buttons, up/down/enter/exit
 
 now displays options
 and selected value
 
 todo:
   highlight the current value in the setting values screen
   scroll setting/values
   save custom settings (JSON files)
   

 * * ** * * * * * ** * * * * * * * * * 
"""
import machine
import utime as time
from collections import namedtuple


# set up SSD1306 screen
sda=machine.Pin(4) # GP4, Pin 6
scl=machine.Pin(5) # GP5, Pin 7

i2c=machine.I2C(0,sda=sda, scl=scl, freq=400000)
#print("Device id: {0}".format(hex(i2c.scan())))
from ssd1306 import SSD1306_I2C
oled = SSD1306_I2C(128, 64, i2c)

# setup menu settings
Options = namedtuple('Options','OptId Description Value Default')

DisplayLines = ["LOC","SPU","TestA","TestB"]

Settings = {
    "LOC": {
        "desc":"Location",
        "value": "DD",
        "options": [
            Options(100,"Deg. mins", "DMS", False),
            Options(102,"Deg. dec", "DD", True),
            Options(103,"UTM", "UTM", False)
            ]
        },
    "SPU": {
        "desc":"Speed",
        "value": "kph",
        "options": [
            Options(100,"KM/H", "kph", True),
            Options(102,"Mile/H", "mph", False)
            ]
        },
    "TestA": {
        "desc":"Test A",
        "value": "1",
        "options": [
            Options(100,"One", "1", True),
            Options(102,"Two", "2", False),
            Options(103,"Three", "3", False),
            Options(104,"Four", "4", False)
            ]
        },
    "TestB": {
        "desc":"Test B",
        "value": "B",
        "options": [
            Options(100,"Letter A", "A", True),
            Options(102,"Letter B", "B", False)
            ]
        }
    }



# set up buttons
Upbtn = machine.Pin(8, machine.Pin.IN, machine.Pin.PULL_DOWN)
Downbtn = machine.Pin(9, machine.Pin.IN, machine.Pin.PULL_DOWN)
Enterbtn = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_DOWN)
Exitbtn = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_DOWN)
lastIntTime = time.ticks_ms()

startLine = 1 # the line settings display from (starting from line zero)
selectedSetting = 0 # current highlighted setting
selectedSettingValue = 0 # current highlighted setting value
buttonPressed = 0 # pin no of clicked button

# set up interrupt function
def int_handler(pin):
    pin.irq(handler=None)
    global buttonPressed
    global lastIntTime

    # software switch debounce, wait 200ms before actioning another interrupt
    currTime = time.ticks_ms()
    if time.ticks_diff(time.ticks_ms(),lastIntTime) > 300:
        lastIntTime = currTime
        buttonPressed=pin
    pin.irq(handler=int_handler)
   
# bind interrupt to pin
Upbtn.irq(trigger=machine.Pin.IRQ_RISING, handler=int_handler)
Downbtn.irq(trigger=machine.Pin.IRQ_RISING, handler=int_handler)
Enterbtn.irq(trigger=machine.Pin.IRQ_RISING, handler=int_handler)
Exitbtn.irq(trigger=machine.Pin.IRQ_RISING, handler=int_handler)

# display heading for page
def displayHeading(heading="MAIN"):
    oled.fill(0)
    oled.show()

    oled.fill_rect(0,0,128,9,0)
    oled.text("  === {} ===".format(heading),0,0)
    oled.show()

# display setting and options in a new page
def displaySettings(startLine=1):
    global selectedSettingValue
    selectedSettingValue = 0
    lineNo = startLine
    
    
    displayHeading()
    
    for line in DisplayLines:
        setting=Settings[line]
        print("{}:".format(setting['desc']))
        oled.text(setting['desc'],0,lineNo*10)
        oled.show()
        lineNo += 1
        
# display setting and options in a new page
def displaySettingValues(options, currValue, startLine=1):
    global DisplayLines
    global Settings
    lineNo = startLine
    
    print("displaySettingValues()")
    
    for option in options:
        setChar =" "
        if option.Value == currValue:
            setChar = ">"
        
        print("{}:".format(option))
        oled.text("{} {}".format(setChar,option.Description),0,lineNo*10)
        oled.show()
        lineNo += 1

# set the value for the setting to the new selected setting value
def setSettingValue(targetSetting, targetSettingValue):
    global DisplayLines
    global Settings
    global selectedSettingValue
    global oled
    
    print("setSettingValue")
    print("selectedSettingValue {}".format(selectedSettingValue))
    print("targetSettingValue {}".format(targetSettingValue))
    setting=Settings[DisplayLines[targetSetting]]
    options=setting['options']
    
    setting['value']=options[targetSettingValue].Value  # update value for setting
    selectedSettingValue = targetSettingValue
    
    oled.fill(0)
    oled.show()
    displayHeading(DisplayLines[targetSetting])
    displaySettingValues(options, setting['value'], startLine=1)
    highlightSettingValue(options[selectedSettingValue], selectedSettingValue, setting['value'], True) # update new selection
    #highlightSettingValue(options[selectedSettingValue], selectedSettingValue, setting['value'], False) # update old selection


def displaySettingOptionsScreen(targetSetting):
    global Settings
    global selectedSetting
    global buttonPressed
    global selectedSettingValue
    global DisplayLines
    selectSettingValue=0
    setting=Settings[DisplayLines[targetSetting]]
    options = setting['options']
    
    print("displaySettingOptionsScreen()")
    
    displayHeading(DisplayLines[targetSetting])
    
    # display options
    displaySettingValues(setting['options'], setting['value'], 1)
    highlightSettingValue(options[selectedSettingValue], selectedSettingValue, setting['value'], True)
        
    while (buttonPressed is not Exitbtn):
        if buttonPressed != 0:
            if buttonPressed is Upbtn:
                buttonPressed = 0
                print("Up ***************")
                changeSettingValue("UP")
            elif buttonPressed is Downbtn:
                buttonPressed = 0
                print("Down *************")
                changeSettingValue("DOWN")
            elif buttonPressed is Enterbtn:
                buttonPressed = 0
                print("Enter ************")
                setSettingValue(selectedSetting, selectedSettingValue)
            elif buttonPressed is Exitbtn:
                print("Exit *************")
                pass
            else:
                buttonPressed = 0
    # we've finished, go back to main screen
    displaySettings()
    highlightSetting(selectedSetting)
    
# set text and background color
def highlightSetting(targetSetting, isInverted=True):
    global startLine
    global DisplayLines
    global Settings
    
    textColour=0
    bgColour=1
    
    if isInverted:
        textColour=1
        bgColour=0
    
    oled.fill_rect(0,((targetSetting+startLine)*10)-1,128,9,textColour)
    setting=Settings[DisplayLines[targetSetting]]
    oled.text(setting['desc'],0,(targetSetting+startLine)*10,bgColour)
    oled.show()

# set text and background color for setting value
def highlightSettingValue(option, targetSettingValue, currValue, isInverted=True):
    global startLine
    global DisplayLines
    global Settings
    
    print("highlightSettingValue()")
    
    textColour=0
    bgColour=1
    
    if isInverted:
        textColour=1
        bgColour=0
    
    setChar =" "
    if option.Value == currValue:
        setChar = ">"
        
    print("{}:".format(option))
    oled.fill_rect(0,((targetSettingValue+startLine)*10)-1,128,9,textColour)
    oled.text("{} {}".format(setChar,option.Description),0,(targetSettingValue+startLine)*10,bgColour)
    oled.show()

def changeSetting(dir):
    global selectedSetting
    rc = 0
    
    highlightSetting(selectedSetting, False) # unhighlight current setting

    if (dir=="DOWN"):
        selectedSetting += 1
        if selectedSetting >= len(DisplayLines):
            selectedSetting=0
    elif (dir=="UP"):
        print("selectedSetting {}".format(selectedSetting))
        selectedSetting -= 1
        if selectedSetting < 0:
            selectedSetting=len(DisplayLines)-1
    else:
        print("Error - invalid dir in changeSelection()")
        rc=1
    
    if rc==0:
        print("goDown, selectedSetting now {}".format(selectedSetting))
        highlightSetting(selectedSetting) # highlight new setting
    
def changeSettingValue(dir):
    global selectedSetting
    global selectedSettingValue
    global Settings
    rc = 1
    
    print("changeSettingValue()")
    
    setting=Settings[DisplayLines[selectedSetting]]
    options = setting['options']
    
    
    highlightSettingValue(options[selectedSettingValue], selectedSettingValue, setting['value'], False) # unhighlight current setting

    if (dir=="DOWN"):
        selectedSettingValue += 1
        if selectedSettingValue >= len(options):
            selectedSettingValue=0
    elif (dir=="UP"):
        print("selectedSettingValue {}".format(selectedSettingValue))
        selectedSettingValue -= 1
        if selectedSettingValue < 0:
            selectedSettingValue=len(options)-1
    else:
        print("Error - invalid dir in changeSettingValue()")
        rc=0
    
    if rc==1:
        print("goDown, selectedSettingValue now {}".format(selectedSettingValue))
        highlightSettingValue(options[selectedSettingValue], selectedSettingValue, setting['value'], True) # highlight new setting value   
    
    


# * * * * * main code * * * * * * *

#set up display and highlight first setting
displaySettings()
highlightSetting(selectedSetting)

while True:
    if buttonPressed != 0:
        if buttonPressed is Upbtn:
            buttonPressed = 0
            print("Up ***************")
            changeSetting("UP")
        elif buttonPressed is Downbtn:
            buttonPressed = 0
            print("Down *************")
            changeSetting("DOWN")
        elif buttonPressed is Enterbtn:
            buttonPressed = 0
            print("Enter ************")
            displaySettingOptionsScreen(selectedSetting)
        elif buttonPressed is Exitbtn:
            buttonPressed = 0
            print("Exit *************")
        else:
            buttonPressed = 0

