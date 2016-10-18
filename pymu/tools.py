from .client import Client
from .pmuConfigFrame import ConfigFrame 
from .pmuCommandFrame import CommandFrame
from .aggPhasor import *
from .pmuDataFrame import *

MAXFRAMESIZE = 65535

def turnDataOff(cli, idcode):
    cmdOff = CommandFrame("DATAOFF", idcode)
    cli.sendData(cmdOff.fullFrameBytes)

def turnDataOn(cli, idcode):
    cmdOn = CommandFrame("DATAON", idcode)
    cli.sendData(cmdOn.fullFrameBytes)

def requestConfigFrame2(cli, idcode):
    cmdConfig2 = CommandFrame("CONFIG2", idcode)
    cli.sendData(cmdConfig2.fullFrameBytes)

def readConfigFrame2(cli, debug=False):
    configFame = None

    s = cli.readSample(4)
    configFrame = ConfigFrame(bytesToHexStr(s), debug)
    expSize = configFrame.framesize
    s = cli.readSample(expSize - 4)
    configFrame.frame = configFrame.frame + bytesToHexStr(s).upper()
    configFrame.finishParsing()

    return configFrame

# Requests configframe2 from OpenPDC, creates/returns a configFrame instance
# for use later with data frames.  Provides default behavior if custom ports
# are desired
def startDataCapture(idcode, ip, port=4712, tcpUdp="TCP", debug=False):
    configFrame = None

    cli = Client(ip, port, tcpUdp)
    cli.setTimeout(5)
    
    while configFrame == None:
        #turnDataOff(cli, idcode)
        requestConfigFrame2(cli, idcode)
        configFrame = readConfigFrame2(cli, debug)

    turnDataOn(cli, idcode)
    cli.closeSocket()

    return configFrame

# Returns all station names from the config frame
def getStations(configFrame):
    stations = []
    for s in configFrame.stations:
        print("Station:", s.stn)
        stations.append(s)
    
    return stations

# Creates an array of aggregate phasors for data collection
def createAggPhasors(configFrame):
    pmus = []
    for s in getStations(configFrame):
        phasors = []
        print("Name:", s.stn)
        for p in range(0, s.phnmr):
            print("Phasor:", s.channels[p])
            theUnit = "VOLTS"
            if s.phunits[p].voltORcurr == "CURRENT":
                theUnit = "AMPS"
            phasors.append(AggPhasor(s.stn.strip() + "/" + s.channels[p].strip(), theUnit))

        pmus.append(phasors)
    
    return pmus

# Takes in an array of dataFrames and inserts the data into an array of 
# aggregate phasors
def parseSamples(data, configFrame, pmus):
    numOfSamples = len(data)
    for s in range(0, numOfSamples):
        for p in range(0, len(data[s].pmus)):
            for ph in range(0, len(data[s].pmus[p].phasors)):
                utcTimestamp = data[s].soc.utcSec + (data[s].fracsec / configFrame.time_base.baseDecStr) 
                pmus[p][ph].addSample(utcTimestamp, data[s].pmus[p].phasors[ph].mag, data[s].pmus[p].phasors[ph].rad)

    return pmus

