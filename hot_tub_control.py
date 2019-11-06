# Hot Tub Controller
# Written by ToMaToGoD

import os
import time
import datetime
import subprocess
from elasticsearch import Elasticsearch

# set working directory
working_directory = "/home/pi/Applications/hot_tub_controller/"
log_output_folder = "/home/pi/Applications/hot_tub_controller/logs/"

# define sensor folders
sensor_1 = "/sys/bus/w1/devices/28-01144e89e7aa/w1_slave"  # Solar panel
sensor_2 = "/sys/bus/w1/devices/28-011452dc93aa/w1_slave"  # Hot Tub

# define Elasticsearch address
es=Elasticsearch([{'host':'localhost','port':9200}])

# get time
def the_time_is():
    time = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S,")
    return time

# get es time
def es_time():
    time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    return time

# start logger
the_date_is = datetime.datetime.now().strftime("%Y-%m-%d")
log_file = open(log_output_folder + the_date_is + "_hottub.log", "a-")
log_file.write("\n" + the_time_is() + " Program starting...")
log_file.close()

# collect sensor raw file 1
def raw_1():
    while os.path.isfile(sensor_1) is False:
        log_file = open(log_output_folder + the_date_is + "_hottub.log", "a-")
        log_file.write("\n" + the_time_is() + " Sensor 1 failed")
        log_file.close()
        time.sleep(120)
    else:
        f1 = open(sensor_1, 'r')
        lines = f1.readlines()
        f1.close()
        return lines

# read raw file 1 and format temperature to degrees celcius
def read_temp_1():
    lines = raw_1()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = raw_1()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

# collect sensor raw file 2
def raw_2():
    while os.path.isfile(sensor_1) is False:
        log_file = open(log_output_folder + the_date_is + "_hottub.log", "a-")
        log_file.write("\n" + the_time_is() + " Sensor 2 failed")
        log_file.close()
        time.sleep(120)
    else:
        f2 = open(sensor_2, 'r')
        lines = f2.readlines()
        f2.close()
        return lines

# read raw file 1 and format temperature to degrees celcius
def read_temp_2():
    lines = raw_2()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = raw_2()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

# compare time cheap electric time to see if heater should be on
def should_heater_be_on():
    t = datetime.datetime.now().strftime("%H:%M")
    if t >= ("00:30") and t < ("04:30"):
        return(1)
    else:
        return(0)

# call tplink script to toggle smart plug (pump should always be on when heater is)
def switch_on_heater():
    subprocess.call(working_directory + "tplink_smartplug.py -t hottubheater.tomatogod -c on", shell=True)

# call tplink script to toggle smart plug
def switch_off_heater():
    subprocess.call(working_directory + "tplink_smartplug.py -t hottubheater.tomatogod -c off", shell=True)

# call tplink script to toggle smart plug
def switch_on_pump():
    subprocess.call(working_directory + "tplink_smartplug.py -t hottubpump.tomatogod -c on", shell=True)

# call tplink script to toggle smart plug
def switch_off_pump():
    subprocess.call(working_directory + "tplink_smartplug.py -t hottubpump.tomatogod -c off", shell=True)

# set states to default off
new_pump_state = 0
current_pump_state = 0
new_heater_state = 0
current_heater_state = 0

# program loop
while True:

    # start to log
    log_file = open(log_output_folder + the_date_is +"_hottub.log", "a-")
    log_file.write("\n" + the_time_is())

    # get temperature readings from sensors
    temp1 = round(read_temp_1(), 1)
    temp2 = round(read_temp_2(), 1)

    # write temperture readings to log
    log_file.write(" Solar Panel: " + str(temp1) + "," + " Hot Tub: " + str(temp2) + ",")

    # determine if heater should be on
    if should_heater_be_on() == 1 and temp2 < 35.0:
        new_heater_state = 1
    else:
        new_heater_state = 0

    # determine if pump should be on
    
if temp1 > (temp2 + 15):
        new_pump_state = 1
    elif temp1 <= 5:
        new_pump_state = 1
    elif current_heater_state == 1:
        new_pump_state = 1
    elif new_heater_state == 1:
        new_pump_state = 1
    else:
        new_pump_state = 0

    # compare new pump state to current pump state
    if new_pump_state == 1 and current_pump_state == 0:
        log_file.write(" Switch pump: on,")
        switch_on_pump()
        pump_state = "True"
        current_pump_state = 1
    elif new_pump_state == 1 and current_pump_state == 1:
        log_file.write(" Pump: on,")
        switch_on_pump()
        pump_state = "True"
    elif new_pump_state == 0 and current_pump_state == 1:
        log_file.write(" Switch pump: off,")
        current_pump_state = 0
        pump_state = "False"
        switch_off_pump()
    else:
        log_file.write(" Pump: off,")
        switch_off_pump()
        pump_state = "False"

    # compare heater new state to heater current state
    if new_heater_state == 1 and current_heater_state == 0:
        log_file.write(" Switch heater: on,")
        time.sleep(60)
        switch_on_heater()
        current_heater_state = 1
    elif new_heater_state == 1 and current_heater_state == 1:
        log_file.write(" Heater: on,")
        switch_on_heater()
    elif new_heater_state == 0 and current_heater_state == 1:
        log_file.write(" Switch heater: off,")
        switch_off_heater()
        current_heater_state = 0
    else:
        log_file.write(" Heater: off,")
        switch_off_heater()

    # build elasticsearch payload
    es_payload={
        "Time":es_time(),
        "Solar Panel": temp1,
	"Hot Tub": temp2,
        "Pump": current_pump_state,
	"Heater": current_heater_state,
    }

    # send payload to elasticsearch
    res = es.index(index='temperatures',doc_type='readings',body=es_payload)

    # sleep for x seconds
    log_file.close()
    time.sleep(58)
