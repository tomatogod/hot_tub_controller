# Hot Tub Controller
# Written by ToMaToGoD

Version = 0.1

import os
import time
import datetime
import subprocess
from elasticsearch import Elasticsearch
import statistics

# load probe modules
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# set working directory
working_directory = "/home/pi/apps/hot_tub_controller/"
log_output_folder = "/home/pi/apps/hot_tub_controller/logs/"

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
log_file = open(log_output_folder + the_date_is + "_hottub.log", "a+")
log_file.write("\n" + "\n" + "\n" + the_time_is() + " Program starting..." + " \n")
log_file.write(the_time_is() + " Version : " + str(Version) + " \n")

# define sensor folders
subprocess.call("ls /sys/bus/w1/devices/", shell=True)
sensor_1 = "/sys/bus/w1/devices/28-011452e79daa/w1_slave"  # Solar panel
sensor_2 = "/sys/bus/w1/devices/28-011452dc93aa/w1_slave"  # Intake
sensor_3 = "/sys/bus/w1/devices/28-011452c161aa/w1_slave"  # Outlet


# define Elasticsearch address
es=Elasticsearch([{'host':'homeassistant.tomatogod','port':9200}])

# Check point
log_file.write(the_time_is() + " Working Directory is: " + working_directory + "\n")
log_file.write(the_time_is() + " Log Directory is: " + log_output_folder + "\n")
log_file.write(the_time_is() + " Sensor 1 is : " + sensor_1 + "\n")
log_file.write(the_time_is() + " Sensor 2 is : " + sensor_2 + "\n")
log_file.write(the_time_is() + " Sensor 3 is : " + sensor_3 + "\n")

# collect sensor raw file 1
def raw_1():
    while os.path.isfile(sensor_1) is False:
        log_file.write("\n" + the_time_is() + " Sensor 1 failed")
        time.sleep(1)
    else:
        f1 = open(sensor_1, 'r')
        lines = f1.readlines()
        f1.close()
        return lines

# read raw file 1 and format temperature to degrees celcius
def read_temp_1():
    lines = raw_1()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(1)
        lines = raw_1()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

log_file.write(the_time_is() + " Sensor 1 reading is : " + str(read_temp_1()) + " \n")

# collect sensor raw file 2
def raw_2():
    while os.path.isfile(sensor_1) is False:
        log_file.write("\n" + the_time_is() + " Sensor 2 failed")
        time.sleep(1)
    else:
        f2 = open(sensor_2, 'r')
        lines = f2.readlines()
        f2.close()
        return lines

# read raw file 2 and format temperature to degrees celcius
def read_temp_2():
    lines = raw_2()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(1)
        lines = raw_2()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

log_file.write(the_time_is() + " Sensor 2 reading is : " + str(read_temp_2()) + " \n")

# collect sensor raw file 3
def raw_3():
    while os.path.isfile(sensor_3) is False:
        log_file.write("\n" + the_time_is() + " Sensor 3 failed")
        time.sleep(1)
    else:
        f3 = open(sensor_3, 'r')
        lines = f3.readlines()
        f3.close()
        return lines

# read raw file 3 and format temperature to degrees celcius
def read_temp_3():
    lines = raw_3()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = raw_3()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

log_file.write(the_time_is() + " Sensor 3 reading is : " + str(read_temp_3()) + " \n")

# compare time cheap electric time to see if heater should be on
def should_heater_be_on():
    t = datetime.datetime.now().strftime("%H:%M")
    if t >= ("02:30") and t < ("06:30"):
        return(1)
    else:
        return(0)

log_file.write(the_time_is() + " Should heater be on : " + str(should_heater_be_on()) + " \n")

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
intake_max = 35
intake_min = 10

log_file.write(the_time_is() + " new_pump_state : " + str(new_pump_state) + " \n")
log_file.write(the_time_is() + " current_pump_state : " + str(current_pump_state) + " \n")
log_file.write(the_time_is() + " new_heater_state : " + str(new_heater_state) + " \n")
log_file.write(the_time_is() + " current_heater_state : " + str(current_heater_state) + " \n")
log_file.write(the_time_is() + " Starting logic loop... " + "\n")
log_file.close()

# program loop
while True:
    log_file = open(log_output_folder + the_date_is + "_hottub.log", "a+")

    temp1 = round(read_temp_1(), 1)
    temp2 = round(read_temp_2(), 1)
    temp3 = round(read_temp_3(), 1)
    buffer = 5.6
    gain = round(temp3 - temp2, 1)

    # write temperture readings to log
    log_file.write("\n" + the_time_is() + " Panel: " + str(temp1) + "," + " Intake: " + str(temp2) + "," + " Outlet: " + str(temp3) + "," + " Gain: " + str(gain) + ",")

    # set intake max of session
    if intake_max < temp2:
        intake_max = temp2
        log_file.write(" Intake Max: " + str(intake_max) + ",")
    else:
        log_file.write(" Intake Max: " + str(intake_max) + ",")

    # set intake max of session
    if intake_min > temp2:
        intake_min = temp2
        log_file.write(" Intake Min: " + str(intake_min) + ",")
    else:
        log_file.write(" Intake Min: " + str(intake_min) + ",")

    # determine if heater should be on
    if should_heater_be_on() == 1 and temp3 < 36:
        intake_max = temp3
        intake_min = temp3
        new_heater_state = 1
    else:
        new_heater_state = 0

    # determine if pump should be on
    if temp1 > (intake_max + buffer):
        new_pump_state = 1
    elif temp1 < 1 or temp2 < 1 or temp3 < 1: #frost protection
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
        pump_state = "True"
    elif new_pump_state == 0 and current_pump_state == 1:
        log_file.write(" Switch pump: off,")
        current_pump_state = 0
        pump_state = "False"
        switch_off_pump()
    else:
        log_file.write(" Pump: off,")
        pump_state = "False"

    # compare heater new state to heater current state
    if new_heater_state == 1 and current_heater_state == 0:
        log_file.write(" Switch heater: on,")
        switch_on_heater()
        current_heater_state = 1
    elif new_heater_state == 1 and current_heater_state == 1:
        log_file.write(" Heater: on,")
    elif new_heater_state == 0 and current_heater_state == 1:
        log_file.write(" Switch heater: off,")
        switch_off_heater()
        current_heater_state = 0
    else:
        log_file.write(" Heater: off,")

    # build elasticsearch payload
    es_payload={
        "Time":es_time(),
        "Solar Panel": temp1,
        "Intake": temp2,
        "Outlet": temp3,
        "Pump": current_pump_state,
        "Heater": current_heater_state,
        "Max": intake_max,
        "Min": intake_min,
        "Gain": gain,
      }

    # send payload to elasticsearch
    try:
        res = es.index(index='temperatures',doc_type='_doc',body=es_payload)
    except:
        log_file.write(" Error Sending to ElasticSearch, ignoring...")

    # send payload to static document
    try:
        res = es.index(index='temperatures', doc_type='_doc', id='CSdmU3AB5mZWiXGYthJE', body=es_payload)
    except:
        log_file.write(" Error Sending to ElasticSearch, ignoring...")

    log_file.close()
