import httplib, urllib
import time
import wiringpi2 as wiringpi
import os
import glob
import time
import datetime

KEY = ''    #please fill in the blank with your thingspeak key
headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
DEBUG = True
CURRENTSTATUE = 1
HIGHTEMP = 25
LOWTEMP = 24
TURNON = 1
TURNOFF = 0
temp = 25

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = base_dir + '28-0316a360b7ff'    #please fill the blank with your temperature sensor ID (18DS20)
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def control_heater(heater):
    global CURRENTSTATUE, TURNON, TURNOFF
    if(wiringpi.digitalRead(1) and heater):
        wiringpi.digitalWrite(0,1)
        CURRENTSTATUE=TURNON
    else:
        wiringpi.digitalWrite(0,0)
        CURRENTSTATUE=TURNOFF
    
def control_TEMP():
    global CURRENTSTATUE, HIGHTEMP, LOWTEMP, TURNON, TURNOFF, temp
    now = datetime.datetime.now()
    nowHour = int(now.strftime("%H"))
    if(CURRENTSTATUE==TURNON):
        if(temp > HIGHTEMP):
            control_heater(0)
        else :
            control_heater(1)
    elif(CURRENTSTATUE==TURNOFF):
        if(temp < LOWTEMP):
            control_heater(1)
        else :
            control_heater(0)
    if(nowHour >= 6):
        HIGHTEMP = 26
        LOWTEMP = 25
    elif(nowHour <6):
        HIGHTEMP = 25
        LOWTEMP = 24
        
wiringpi.wiringPiSetup()
wiringpi.pinMode(0,1)
wiringpi.pinMode(1,0)

while True:
    temp = read_temp()
    control_TEMP()
    params = urllib.urlencode({'field1': temp, 'field2': CURRENTSTATUE, 'key':KEY})
    conn = httplib.HTTPConnection("api.thingspeak.com:80")
    conn.request("POST", "/update", params, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    print response.status, response.reason
    print CURRENTSTATUE, temp
    time.sleep(60)