""" 
write new screen layout

"""

import ssd1306
import machine
import time
import uos

SSD1306scl = machine.Pin('X12', machine.Pin.OUT_PP)
SSD1306sda = machine.Pin('X11', machine.Pin.OUT_PP)
i2c = machine.SoftI2C(scl=SSD1306scl,sda=SSD1306sda)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

flist = set()
new_flist = set()
fmod = []

def convert_fsize(fsize):
    KB = 1024
    MB = 1048576
    GB = 1073741824
    if fsize < MB:
        # less than 1Mb
        rc = fsize / KB
        unit = 'Kb'
    elif fsize < GB:
        # less than 1Gb
        rc = fsize / MB
        unit = 'MB'
    else:
        rc = fsize / GB
        unit = 'GB'
    return (rc, unit)


def display_title():
    oled.hline(2, 4, 20, 1)
    oled.hline(106, 4, 20, 1)
    oled.text("Survey.TV",28,0)
    oled.show()
    
def display_stats(storage ='/sd'):
    #clear last data
    oled.fill_rect(0,10,128,20,0)
    oled.show()
    flash = uos.statvfs(storage)
    #flash_size = flash[0] * flash[2]
    #flash_free = flash[0] * flash[3]
    flash_free = convert_fsize(flash[0] * flash[3])
    fspace = 'Free: {0:.4f} {1}'.format(flash_free[0],flash_free[1])
    fnum = 'Files: {}'.format(len(uos.listdir(storage)))
    oled.text(fspace,0,10)
    oled.text(fnum, 0,20)
    oled.show()

def display_last_activity():
    global fmod
    if len(fmod) > 0:
        #clear last data
        oled.fill_rect(0,35,128,20,0)
        oled.show()
        
        fdeets = fmod[0]
        txt = "[{}] {}".format(fdeets[1], fdeets[0])
        oled.text(txt, 0,35)
        fname = "" + fdeets[0]
        print(fname)
        print(type(fname))
        
        try:
            print(uos.stat(fname))
            fsize = convert_fsize(uos.stat(fname)[6])
            txt = " size: {:.1f} {}".format(fsize[0],fsize[1])
            #txt = " size: {} {}".format(uos.stat(fname)[6],'kb')
            oled.text(txt, 0,45)
        except:
            pass
        oled.show()
    
def get_new_flist():
    global new_flist
    new_flist.clear()
    
    for f in uos.ilistdir():
        fname=""
        if f[1] == 16384:
            fname = "/" + f[0]
        else:
            fname = f[0]
        new_flist.add(fname)

    
# * * * main code * * * 
oled.fill(0)
oled.show()

display_title()
display_stats()
#display_last_activity()

# set up current list of file names
for f in uos.ilistdir():
    fname=""
    if f[1] == 16384:
        fname = "/" + f[0]
    else:
        fname = f[0]
    flist.add(fname)
    
print("starting....")
print("Flist:\n{}".format(flist))
time.sleep(5)

count=0
while True:
    display_title()
    display_stats()
    
    count += 1
    print('\n\nnext loop {}:'.format(count))
    #get new flist
    get_new_flist()
    print("new_filelist:\n{}".format(new_flist))
    
    fmod.clear()
    # removed files
    for r in (flist - new_flist):
        fmod.append((r,'-'))
    
    # added files
    for r in (new_flist - flist):
        fmod.append(((r,'+')))
    
    if len(fmod)>0:
        flist = new_flist.copy()
        
        print("\n\n* * * * File activity * * * * *")
        for x in fmod:
            print('{1} {0}'.format(x[0], x[1]))
        print("\n* * * * * * * * * * * *\n\n")
        
        display_title()
        display_stats()
        display_last_activity()
        
        
    
    time.sleep(1)

"""
Outline of the lost work to monitor file size changes


1) Create new sets to track file size

new_flist_size = set()
flist_size = set()

2) Update get_new_flist() to populate fname and size tuple into new_flist_size set
   make the same updates for the initial population of flist_size
   File size is found from uos.stat(<fname>)[6]
   
   new_flist_size.add((<fname>,<size>))
   flist_size.add((<fname>,<size>))

3) Add new test in main code

    # check for modified files (via filesize)
    for r in (flist_size - new_flist_size):  # shouldn't matter which way around
		# check that file has been modified, hasn't just been added/removed
		if r[0] in flist     # do we need to check it is in flist and new_flist? =>  if r[0] in flist and r[0] in new_flist
			fmod.append(((r,'M')))  # 'M' for modify

4) Wherever we update flist to be a copy of new_flist, then add 

	flist_size = new_flist_size.copy()


5) change display_last_activity() to populate file size using the convert_fsize() function
"""