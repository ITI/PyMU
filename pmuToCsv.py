import sys
import os
import time
import datetime
import socket
import re
import signal

sys.path.append("PyMU")
from lib.server import Server
from lib.pmuDataFrame import DataFrame
from lib.pmuLib import *
import pdcTools

CSV_DIR = "./data"

RUNNING = True

def csvPrint(dFrame, csv_handle, applyscaling):

    strOut = ""
    for i in range(0, len(dFrame.pmus)):
        strOut += dFrame.soc.formatted + ","
        for j in range(0, len(dFrame.pmus[i].phasors)):
            if re.search('[ABC]P[IV]', dFrame.pmus[i].phasors[j].name):
                if applyscaling:
                    if re.search('[ABC]PV', dFrame.pmus[i].phasors[j].name):
                        strOut += str(float(dFrame.pmus[i].phasors[j].mag)/1000.0) + ","
                    if re.search('[ABC]PI', dFrame.pmus[i].phasors[j].name):
                        strOut += str(float(dFrame.pmus[i].phasors[j].mag)/100.0) + ","
                else:
                    strOut += str(float(dFrame.pmus[i].phasors[j].mag)) + ","
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

def createCsvFile(stationName):

    createCsvDir()

    prettyDate = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    csvFileName = "{}_{}.csv".format(prettyDate, stationName.rstrip())
    csv_path = "{}/{}".format(CSV_DIR, csvFileName)

    applyscaling = False
    if stationName.rstrip() == "RELAYA":
        applyscaling = True;

    if (os.path.isfile(csv_path)):
        nextIndex = getNextIndex(csv_path)
        csvFileName = "{}_{}.csv".format(prettyDate, nextIndex)
        csv_path = "{}/{}".format(CSV_DIR, csvFileName)

    csv_handle = open(csv_path, 'w')
    csv_handle.write("Timestamp,Va_Mag,Va_Deg,Vb_Mag,Vb_Deg,Vc_Mag,Vc_Deg,Ia_Mag,Ia_Deg,Ib_Mag,Ib_Deg,Ic_Mag,Ic_Deg,Freq,ROCOF\n")

    return csv_handle, applyscaling

def runPmuToCsv(confFrameIp, confFramePort, dataFramePort, frameId, index=-1, printInfo = True):

    applyscaling = False

    print("#{}# Creating Connection\n\t{:<10} {}\n\t{:<10} {}\n\t{:<10} {}\n\t{:<10} {}\n----- ----- -----".format(index, "IP:", confFrameIp, "CMD Port:", confFramePort, "Data Port:", dataFramePort, "ID Code:", frameId))
    try:
        print("#{}# Reading Config Frame...".format(index)) if printInfo else None
        confFrame = pdcTools.startDataCapture(frameId, confFrameIp, confFramePort) # IP address of openPDC
    except Exception as e:
        print("#{}# Exception: {}".format(index, e))
        print("#{}# Config Frame not received...Exiting".format(index))
        sys.exit()

    if confFrame:
        print("#{}# Success!!".format(index)) if printInfo else None
    else:
        print("#{}# Failure!!".format(index)) if printInfo else None

    csv_handle, applyscaling = createCsvFile(confFrame.stations[0].stn)

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
            csvPrint(dFrame, csv_handle, applyscaling)
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
        print("Usage: python <fileName> <configFrameIp> <configFramePort> <dataFramePort> <frameId>")
        sys.exit()

    confFrameIp = sys.argv[1]
    confFramePort = int(sys.argv[2])
    dataFramePort = int(sys.argv[3])
    frameId = int(sys.argv[4])

    runPmuToCsv(confFrameIp, confFramePort, dataFramePort, frameId)


