import sys
import os
import time
import datetime
import socket
import re
import signal

from pymu.server import Server
from pymu.pmuDataFrame import DataFrame
from pymu.pmuLib import *
import pymu.tools as tools

CSV_DIR = "./data"

RUNNING = True

def csvPrint(dFrame, csv_handle):

    strOut = ""
    for i in range(0, len(dFrame.pmus)):
        strOut += dFrame.soc.formatted + ","
        for j in range(0, len(dFrame.pmus[i].phasors)):
            #if re.search('[ABC]P[IV]', dFrame.pmus[i].phasors[j].name):
            strOut += str(dFrame.pmus[i].phasors[j].deg) + ","
        strOut += str(dFrame.pmus[i].freq) + ","
        strOut += str(dFrame.pmus[i].dfreq)
        if i != (len(dFrame.pmus) - 1):
            strOut += ","
    strOut += "\n"

    csv_handle.write(strOut)

def getNextIndex(originalPath):
    splitArr1 = originalPath.split('_')
    nextIndex = -1
    if len(splitArr1) == 2:
        nextIndex = 1
    elif len(splitArr1) > 2:
        splitArr2 = splitArr1[-1].split('.')
        nextIndex = int(splitArr2[0]) + 1

    if nextIndex <= 0:
        print("# Error creating next csv file from '{}'".format(originalPath))
        sys.exit()

    return nextIndex

def createCsvDir():
    global CSV_DIR

    if (not os.path.isdir(CSV_DIR)):
        os.mkdir(CSV_DIR)

def createCsvFile(confFrame):

    createCsvDir()

    stationName = confFrame.stations[0].stn
    prettyDate = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    csvFileName = "{}_{}.csv".format(prettyDate, stationName.rstrip())
    csv_path = "{}/{}".format(CSV_DIR, csvFileName)

    if (os.path.isfile(csv_path)):
        nextIndex = getNextIndex(csv_path)
        csvFileName = "{}_{}.csv".format(prettyDate, nextIndex)
        csv_path = "{}/{}".format(CSV_DIR, csvFileName)

    for x in confFrame.stations:
        print(x.channels)

    csv_handle = open(csv_path, 'w')
    csv_handle.write("Timestamp")
    for ch in confFrame.stations[0].channels:
        csv_handle.write(",{}".format(ch.rstrip()))
    csv_handle.write(",Freq")
    csv_handle.write(",ROCOF")
    csv_handle.write("\n")

    return csv_handle 

def runPmuToCsv(confFrameIp, confFramePort, dataFramePort, frameId, index=-1, printInfo = True):

    print("#{}# Creating Connection\n\t{:<10} {}\n\t{:<10} {}\n\t{:<10} {}\n\t{:<10} {}\n----- ----- -----".format(index, "IP:", confFrameIp, "CMD Port:", confFramePort, "Data Port:", dataFramePort, "ID Code:", frameId))
    try:
        print("#{}# Reading Config Frame...".format(index)) if printInfo else None
        confFrame = tools.startDataCapture(frameId, confFrameIp, confFramePort) # IP address of openPDC
    except Exception as e:
        print("#{}# Exception: {}".format(index, e))
        print("#{}# Config Frame not received...Exiting".format(index))
        sys.exit()

    if confFrame:
        print("#{}# Success!!".format(index)) if printInfo else None
    else:
        print("#{}# Failure!!".format(index)) if printInfo else None

    csv_handle = createCsvFile(confFrame)

    serv = Server(dataFramePort, "UDP", False) # Local port to receive data from openPDC
    serv.setTimeout(10)

    print("#{}# Starting data collection...\n".format(index))# if printInfo else None
    p = 0
    milliStart = int(round(time.time() * 1000))
    dataStarted = False
    while RUNNING:
        try:
            d = serv.readSample(64000)
            if d == '':
                break
            dFrame = DataFrame(bytesToHexStr(d), confFrame) # Create dataFrame
            csvPrint(dFrame, csv_handle)
            p += 1
        except KeyboardInterrupt:
            break
        except socket.timeout:
            print("#{}# Data not available right now...Exiting".format(index))
            break
        except Exception as e:
            print("#{}# Exception: {}".format(index, e.message))
            break
            
    # Print statistics about processing speed
    milliEnd = int(round(time.time() * 1000))
    if printInfo:
        print("")
        print("##### ##### #####")
        print("Python Stats")
        print("----- ----- -----")
        print("Duration:  ", (milliEnd - milliStart)/1000, "s")
        print("Total Pkts:", p);
        print("Pkts/Sec:  ", p/((milliEnd - milliStart)/1000))
        print("##### ##### #####")
    serv.stopServer()
    csv_handle.close()

if __name__ == "__main__":
    RUNNING = True
    if (len(sys.argv) != 5):
        print("Usage: python <configFrameIp> <configFramePort> <dataFramePort> <frameId>")
        sys.exit()

    confFrameIp = sys.argv[1]
    confFramePort = int(sys.argv[2])
    dataFramePort = int(sys.argv[3])
    frameId = int(sys.argv[4])

    runPmuToCsv(confFrameIp, confFramePort, dataFramePort, frameId, "")


