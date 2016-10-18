# # # # # #
# Class for creating a Data Frame
# based on C37.118-2011.  
# # # # # #

import math
import struct
import codecs
from datetime import datetime
from .pmuLib import *
from .pmuFrame import PMUFrame
from .pmuEnum import *

class DataFrame(PMUFrame):

    def __init__(self, frameInHexStr, theConfigFrame, debug=False):

        self.stat = None
        self.pmus = None
        self.freq = None
        self.dfreq = None
        self.analog = None
        self.digital = None

        self.configFrame = theConfigFrame
        self.dbg = debug
        super().__init__(frameInHexStr, self.dbg)
        super().finishParsing()
        self.parsePmus()
        self.updateSOC()

    def parsePmus(self):
        print("***** PHASORS *****") if self.dbg else None

        nextPmuStartingPos = 28
        self.pmus = [None]*self.configFrame.num_pmu
        for i in range(0, len(self.pmus)):
            print("*** ", self.configFrame.stations[i].stn.strip(), " ***", sep="") if self.dbg else None
            self.pmus[i] = PMU(self.frame[nextPmuStartingPos:], self.configFrame.stations[i])
            print("Len =", self.pmus[i].length) if self.dbg else None
            print(self.frame[nextPmuStartingPos:(nextPmuStartingPos+self.pmus[i].length)]) if self.dbg else None
            nextPmuStartingPos = nextPmuStartingPos + self.pmus[i].length
    
    def updateSOC(self):
        self.soc.ff = self.fracsec / self.configFrame.time_base.baseDecStr
        self.soc.formatted = "{:0>4}/{:0>2}/{:0>2} {:0>2}:{:0>2}:{:0>2}{}".format(self.soc.yyyy, self.soc.mm, self.soc.dd, self.soc.hh, self.soc.mi, self.soc.ss, "{:f}".format(self.soc.ff).lstrip('0'))
        dt = datetime(self.soc.yyyy, self.soc.mm, self.soc.dd, self.soc.hh, self.soc.mi, self.soc.ss, int(self.soc.ff * 10 ** 6)) 
        self.soc.utcSec = (dt - datetime(1970, 1, 1)).total_seconds()
        
class PMU:

    def __init__(self, pmuHexStr, theStationFrame, debug=False):
    
        self.stat = None
        self.phasors = None
        self.freq = None
        self.dfreq = None
        self.analogs = None
        self.digitals = None
        self.length = 0

        self.dbg = debug
        self.stationFrame = theStationFrame
        self.numOfPhsrs = self.stationFrame.phnmr
        self.fmtOfPhsrs = self.stationFrame.phsrFmt
        self.typeOfPhsrs = self.stationFrame.phsrType
        self.numOfAnlg = self.stationFrame.annmr
        self.numOfDgtl = self.stationFrame.dgnmr
        print("DIG:", self.numOfDgtl) if self.dbg else None

        self.pmuHex = pmuHexStr
        print(pmuHexStr) if self.dbg else None
        self.parseStat()
        self.parsePhasors()
        self.parseFreq()
        self.parseDfreq()
        self.parseAnalog()
        self.parseDigital()

    def updateLength(self, sizeToAdd):
        self.length = self.length + sizeToAdd

    def parseStat(self):
        l = 4
        print("STAT:", self.pmuHex[self.length:self.length+l]) if self.dbg else None
        self.stat = Stat(self.pmuHex[self.length:self.length+l])
        self.updateLength(l)

    def parsePhasors(self):
        print("Phasors") if self.dbg else None
        self.phasors = [None]*self.numOfPhsrs
        print("NumOfPhsrs:", self.numOfPhsrs) if self.dbg else None
        for i in range(0, self.numOfPhsrs):
            self.phasors[i] = Phasor(self.pmuHex[self.length:], self.stationFrame,
                    self.stationFrame.channels[i])
            print("PHASOR:", self.pmuHex[self.length:self.length+self.phasors[i].length]) if self.dbg else None
            self.updateLength(self.phasors[i].length)

    def parseFreq(self):
        l = 4 if self.stationFrame.freqType == "INTEGER" else 8
        print("FREQ:", self.pmuHex[self.length:self.length+l]) if self.dbg else None
        unpackStr = '!h' if l == 4 else '!f'
        self.freq = struct.unpack(unpackStr, bytes.fromhex(self.pmuHex[self.length:self.length+l]))[0]
        self.updateLength(l)
        print("FREQ:", self.freq) if self.dbg else None

    def parseDfreq(self):
        l = 4 if self.stationFrame.freqType == "INTEGER" else 8
        print("DFREQ: ", self.pmuHex[self.length:self.length+l]) if self.dbg else None
        unpackStr = '!h' if l == 4 else '!f'
        self.dfreq = (struct.unpack(unpackStr, bytes.fromhex(self.pmuHex[self.length:self.length+l]))[0]) / 100
        self.updateLength(l)
        print("DFREQ:", self.dfreq) if self.dbg else None

    def parseAnalog(self):
        self.analogs = [None]*self.numOfAnlg
        l = 4 if self.stationFrame.anlgType == "INTEGER" else 8
        unpackStr = "!h" if l == 4 else "!f"
        for i in range(0, self.numOfAnlg):
            name = self.stationFrame.channels[self.numOfPhsrs+i].strip()
            print("ANALOG:", self.pmuHex[self.length:self.length+l]) if self.dbg else None
            val = struct.unpack(unpackStr, bytes.fromhex(self.pmuHex[self.length:self.length+l]))[0]
            print (name, "=", val) if self.dbg else None
            self.analogs[i] = (name, val)
            self.updateLength(l)

    def parseDigital(self):
        self.digitals = [None]*self.numOfDgtl
        l = 4
        totValBin = hexToBin(self.pmuHex[self.length:self.length+l], 16)
        for i in range(0, self.numOfDgtl):
            name = self.stationFrame.channels[self.numOfPhsrs+self.numOfAnlg+i].strip()
            print("DIGITAL:", self.pmuHex[self.length:self.length+l]) if self.dbg else None
            val = totValBin[i]
            print (name, "=", val) if self.dbg else None
            self.digitals[i] = (name, val)
            self.updateLength(l)

class Phasor:

    def __init__(self, thePhsrValHex, theStationFrame, theName, debug=False):
        
        self.phsrFmt = None
        self.phsrType = None
        self.real = None
        self.imag = None
        self.mag = None
        self.deg = None
        self.rad = None
        self.name = None
        self.length = 0

        self.dbg = debug
        self.phsrValHex = thePhsrValHex
        self.stationFrame = theStationFrame
        self.voltORCurr = self.stationFrame.phunits
        self.name = theName
        print("*", theName.strip(), "*") if self.dbg else None
        self.parseFmt()
        self.parseVal()

    def parseFmt(self):
        self.phsrFmt = self.stationFrame.phsrFmt
        self.phsrType = self.stationFrame.phsrType
        self.length = 8 if self.phsrType == "INTEGER" else 16

    def parseVal(self):
        if self.phsrFmt == "RECT":
           self.toRect(self.phsrValHex[:self.length])
        else:
            self.toPolar(self.phsrValHex[:self.length])
 
    def toRect(self, hexVal):
        hex1 = hexVal[:int(self.length/2)]
        hex2 = hexVal[int(self.length/2):]
        unpackStr = "!h" if self.phsrType == "INTEGER" else "!f"
        self.real = struct.unpack(unpackStr, bytes.fromhex(hex1))[0]
        self.imag = struct.unpack(unpackStr, bytes.fromhex(hex2))[0]
        self.mag = math.hypot(self.real, self.imag)
        self.rad = math.atan2(self.imag, self.real)
        self.deg = math.degrees(self.rad)
        print("Real:", hex1, "=", self.real) if self.dbg else None
        print("Imag:", hex2, "=", self.imag) if self.dbg else None
        print("Mag:", "=", self.mag) if self.dbg else None
        print("Rad:", "=", self.rad) if self.dbg else None
        print("Deg:", "=", self.deg) if self.dbg else None

    def toPolar(self, hexVal):
        hex1 = hexVal[:int(self.length/2)]
        hex2 = hexVal[int(self.length/2):]
        unpackStr = "!h" if self.phsrType == "INTEGER" else "!f"
        self.mag = struct.unpack(unpackStr, bytes.fromhex(hex1))[0]
        self.rad = struct.unpack(unpackStr, bytes.fromhex(hex2))[0]
        if unpackStr == '!h':
            self.rad = self.rad / 10000
        self.deg = math.degrees(self.rad)
        self.real = self.mag * math.cos(self.deg)
        self.imag = self.mag * math.sin(self.deg)
        print("Real:", hex1, "=", self.real) if self.dbg else None
        print("Imag:", hex2, "=", self.imag) if self.dbg else None
        print("Mag:", "=", self.mag) if self.dbg else None
        print("Rad:", "=", self.rad) if self.dbg else None
        print("Deg:", "=", self.deg) if self.dbg else None

class Stat:

    def __init__(self, statHexStr, debug=False):

        self.dataError = None
        self.pmuSync = None
        self.sorting = None
        self.pmuTrigger = None
        self.configChange = None
        self.dataModified = None
        self.timeQuality = None
        self.unlockedTime = None
        self.triggerReason = None

        self.dbg = debug
        self.statHex = statHexStr
        print(statHexStr) if self.dbg else None
        self.parseDataError()
        self.parsePmuSync()
        self.parseSorting()
        self.parsePmuTrigger()
        self.parseConfigChange()
        self.parseDataModified()
        self.parseTimeQuality()
        self.parseUnlockTime()
        self.parseTriggerReason()

    def parseDataError(self):
        self.dataError = DataError(int(hexToBin(self.statHex[0], 4)[:2], 2)).name 
        print("STAT: ", self.dataError) if self.dbg else None

    def parsePmuSync(self):
        self.pmuSync = PmuSync(int(hexToBin(self.statHex[0], 4)[2], 2)).name
        print("PMUSYNC: ", self.pmuSync) if self.dbg else None

    def parseSorting(self):
        self.sorting = Sorting(int(hexToBin(self.statHex[0], 4)[3], 2)).name
        print("SORTING: ", self.sorting) if self.dbg else None

    def parsePmuTrigger(self):
        self.pmuTrigger = Trigger(int(hexToBin(self.statHex[1], 4)[0], 2)).name
        print("PMUTrigger: ", self.pmuTrigger) if self.dbg else None

    def parseConfigChange(self):
        self.configChange = ConfigChange(int(hexToBin(self.statHex[1], 4)[1], 2)).name
        print("ConfigChange: ", self.configChange) if self.dbg else None

    def parseDataModified(self):
        self.dataModified = DataModified(int(hexToBin(self.statHex[1], 4)[2], 2)).name
        print("DataModified: ", self.dataModified) if self.dbg else None

    def parseTimeQuality(self):
        self.unlockedTime = TimeQuality(int(hexToBin(self.statHex[1:3], 8)[3:6], 2)).name
        print("TimeQuality: ", self.unlockedTime) if self.dbg else None

    def parseUnlockTime(self):
        self.unlockedTime = UnlockedTime(int(hexToBin(self.statHex[2], 4)[2:], 2)).name
        print("UnlockTime: ", self.unlockedTime) if self.dbg else None

    def parseTriggerReason(self):
        self.triggerReason = TriggerReason(int(hexToBin(self.statHex[3], 4), 2)).name
        print("TriggerReason: ", self.triggerReason) if self.dbg else None

