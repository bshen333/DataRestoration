import csv
import numpy as np
import pandas as pd
from datetime import datetime as dt
import datetime
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from dateutil import tz
from dateutil import parser
from random import random
import os
import math

# recursive function to check for valid file pathing


def checkFile(file,count):
    if os.path.isfile(file):
        count +=1
        midSection = "_000" + str(count)
        newFile = file[:16] + midSection + file[-4:]
        return checkFile(newFile,count)
    else:
        return file
# create function to make idle signals

# create function to call each variable into function to produce the result


def createData(row):
    machineID = row[1]
    machineTag = row[7]
    machineStart = dt.fromisoformat(str(row[2]))
    # in hours convert to minute
    uptime = float(row[5])*60
    setup = float(row[10])*60
    idle = float(row[4])*60
    # total would be total production divide by cycle factor equals raw signal
    total = float(row[6])/float(row[9])
    # units per hour divide to get per minute then per second then times 10 to get signal per 10 seconds
    signalRate = float(total/uptime/60*10)
    threshold = math.ceil(signalRate)-signalRate
    # Setup MachineID folder
    currentDir = os.getcwd()
    # windows need to escape \ and directory is based on \ instead of / as in linux or bash
    folder = currentDir + "\\" + str(machineID)
    # if folder exists dont create it again
    if os.path.exists(folder):
        os.chdir(folder)
    else:
        os.mkdir(folder)
        os.chdir(folder)
    # setup file
    date = machineStart.strftime('%Y%m%d')
    file = "OpcCore_"+date+".xml"
    file = checkFile(file,0)
    # make file path to write our data into
    output_file = open(file, 'wb')
    # setup count
    count = 0
    # setup time variable
    x = machineStart
    # if there is setup, we need to add all setup as idle signals
    while setup > 0:
        x += datetime.timedelta(minutes=1)
        setup -= 1
        S = Element('S', Name='SLX.Ping', Time3=x.isoformat(), Rec=str(count))
        count += 1
        output_file.write(ElementTree.tostring(S)+b'\n')
    # add signal count
    cumulativeCounter = 0
    while total > 0:
        randomThreshold = random()
        add = math.ceil(signalRate) if randomThreshold > threshold else math.floor(signalRate)
        if cumulativeCounter > 65535:
            cumulativeCounter = 0
        S = Element('S', Name=machineTag,
                    Time3=x.isoformat(), Value=str(cumulativeCounter), Rec=str(count))
        x += datetime.timedelta(seconds=10)
        count += 1
        total -= add
        cumulativeCounter += add
        output_file.write(ElementTree.tostring(S)+b'\n')
    # add idle times
    while idle > 0:
        x += datetime.timedelta(minutes=1)
        idle -= 1
        S = Element('S', Name='SLX.Ping', Time3=x.isoformat(), Rec=str(count))
        count += 1
        output_file.write(ElementTree.tostring(S)+b'\n')
    output_file.close()
    os.chdir('..')


# need to import the csv as an object we will loop through
df = pd.read_csv(r'Data Restore_CS-10076.csv')

for x in df.iterrows():
    createData(x[1])
'''
3 dimension object, x is calling row, then 0 is the index, and 1 is the row object static, then next dimension is column iterated
we need to push the x[1]
(0, 
0 - Machine Name                                           NEU-PR-230
1 - Machine ID                   99A29003-6DA7-811C-8563-B2BF1F3D03B0
2 - Start Time                              2021-03-21T15:14:33+02:00
3 - End Time                                2021-03-21T15:31:33+02:00
4 - Idle Time                                                     NaN
5 - Uptime                                                       0.28
6 - Total Production                                           2812.0
7 - Signal Tag          Coveris-Neuwied-ADAM132.192-168-200-132.Port2
8 - TimeZone                                                      NaN
9 - Cycle Factor
10 - Setup Time
Name: 0, dtype: object)
'''
