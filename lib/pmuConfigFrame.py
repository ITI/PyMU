# # # # # #
# Class for creating a Config Frame
# based on C37.118-2011.  
# # # # # #

from lib.pmuFrame import PMUFrame
from lib.pmuEnum import *
from lib.pmuLib import *

class ConfigFrame(PMUFrame):

    def __init__(self, frameInHexStr, debug=False):
        super().__init__(frameInHexStr, debug)
        self.time_base = None
        self.num_pmu = None
        self.stations = None
        self.datarate = None
                
    def finishParsing(self):
        super().finishParsing()
        self.parseTIME_BASE()
        self.parseNUM_PMU()
        self.parseStations()
        self.parseDATARATE()
    
    def parseTIME_BASE(self):
        timebaseSize = 8
        self.time_base = TimeBase(self.frame[self.length:self.length+timebaseSize])
        self.updateLength(timebaseSize)
        print("TIME_BASE: ", self.time_base.baseDecStr, sep="") if self.dbg else None

    def parseNUM_PMU(self):
        numpmuSize = 4
        self.num_pmu = int(self.frame[self.length:self.length+numpmuSize], 16)
        self.updateLength(numpmuSize)
        print("NUM_PMU: ", self.num_pmu, sep="") if self.dbg else None

    def parseStations(self):
        self.stations = [None]*self.num_pmu
        for i in range(0, self.num_pmu):
            self.stations[i] = Station(self.frame[self.length:])
            self.updateLength(self.stations[i].length)
            print("***** Station ", (i+1), " *****", sep="") if self.dbg else None
 
    def parseDATARATE(self):
        datarateSize = 4
        self.datarate = int(self.frame[self.length:self.length+datarateSize],16)
        self.updateLength(datarateSize)
        print("DATARATE: ", self.datarate) if self.dbg else None

class TimeBase:

    def __init__(self, timeBaseHexStr, debug=False):
        self.dbg = debug
        self.timeBaseHex = timeBaseHexStr
        self.flagsBinStr = hexToBin(timeBaseHexStr, 32)[:8]
        self.baseDecStr = int(timeBaseHexStr[1:], 16)

class Station:

    def __init__(self, theStationHex, debug=False): 

        self.stn = None
        self.idcode_data = None
        self.fmt = None
        self.freqType = None
        self.anlgType = None
        self.phsrType = None
        self.phsrFmt = None
        self.phnmr = None
        self.annmr = None
        self.dgnmr = None
        self.channels = None
        self.numOfChns = 0
        self.phunits = None
        self.anunits = None
        self.digunits = None
        self.fnom = None
        self.cfgcnt = None
        self.length = 0
        
        self.dbg = debug
        self.stationFrame = theStationHex
        self.parseSTN()
        self.parseIDCODE_data()
        self.parseFORMAT()
        self.parsePHNMR()
        self.parseANNMR()
        self.parseDGNMR()
        self.parseCHNAME()
        self.parsePHUNIT()
        self.parseANUNIT()
        self.parseDIGUNIT()
        self.parseFNOM()
        self.parseCFGCNT()

    def updateLength(self, sizeToAdd):
        self.length = self.length + sizeToAdd

    def parseSTN(self):
        l = 32
        self.stn = bytes.fromhex(self.stationFrame[self.length:self.length+l]).decode('ascii')
        self.updateLength(l)
        print("STN: ", self.stn, sep="") if self.dbg else None

    def parseIDCODE_data(self):
        l = 4
        self.idcode_data = int(self.stationFrame[self.length:self.length+l], 16)
        self.updateLength(l)
        print("IDCODE_data: ", self.idcode_data) if self.dbg else None

    def parseFORMAT(self):
        l = 4
        fmts = hexToBin(self.stationFrame[self.length:self.length+l], 32)[-4:]

        self.freqType = NumType(int(fmts[0], 2)).name
        self.anlgType = NumType(int(fmts[1], 2)).name
        self.phsrType = NumType(int(fmts[2], 2)).name
        self.phsrFmt = PhsrFmt(int(fmts[3], 2)).name

        self.updateLength(l)

        print("FreqFmt: ", self.freqType) if self.dbg else None
        print("AnlgFmt: ", self.anlgType) if self.dbg else None
        print("PhsrFmt: ", self.phsrType) if self.dbg else None
        print("PhsrFmt: ", self.phsrFmt) if self.dbg else None

    def parsePHNMR(self):
        l = 4
        self.phnmr = int(self.stationFrame[self.length:self.length+l], 16)
        self.updateLength(l)
        print("PHNMR: ", self.phnmr, sep="") if self.dbg else None

    def parseANNMR(self):
        l = 4
        self.annmr = int(self.stationFrame[self.length:self.length+l], 16)
        self.updateLength(l)
        print("ANNMR: ", self.annmr, sep="") if self.dbg else None

    def parseDGNMR(self):
        l = 4
        self.dgnmr = int(self.stationFrame[self.length:self.length+l], 16)
        self.updateLength(l)
        print("DGNMR: ", self.dgnmr, sep="") if self.dbg else None

    def parseCHNAME(self):
        self.numOfChns = self.phnmr + self.annmr + (16 * self.dgnmr)
        self.channels = [None]*self.numOfChns
        l = 32
        for i in range(0, self.numOfChns):
            self.channels[i] = bytes.fromhex(self.stationFrame[self.length:self.length+l]).decode('ascii')
            self.updateLength(l)
            print(self.channels[i]) if self.dbg else None

    def parsePHUNIT(self):
        self.phunits = [None]*self.phnmr
        l = 8
        for i in range(0, self.phnmr):
            self.phunits[i] = Phunit(self.stationFrame[self.length:self.length+l])
            self.updateLength(l)

    def parseANUNIT(self):
        self.anunits = [None]*self.annmr
        l = 8
        for i in range(0, self.annmr):
            self.anunits[i] = Anunit(self.stationFrame[self.length:self.length+l])
            self.updateLength(l)

    def parseDIGUNIT(self):
        self.digunits = [None]*self.dgnmr
        l = 8
        for i in range(0, self.dgnmr):
            self.digunits[i] = Digunit(self.stationFrame[self.length:self.length+l])
            self.updateLength(l)

    def parseFNOM(self):
        l = 4
        hexDigit = self.stationFrame[self.length+4]
        hexDigitLSB = hexToBin(hexDigit, 8)[7]
        hexDigitDec = int(hexDigitLSB, 2)
        
        self.fnom = FundFreq(hexDigitDec).name
        self.updateLength(l)
        print("FNOM: ", self.fnom) if self.dbg else None

    def parseCFGCNT(self):
        l = 4
        self.cfgcnt = int(self.stationFrame[self.length:self.length+l], 16)
        self.updateLength(l)
        print("CFGCNT: ", self.cfgcnt) if self.dbg else None

class Phunit:

    def __init__(self, phunitHexStr, debug=False):
        self.voltORcurr = None
        self.value = None

        self.dbg = debug
        self.phunitHex = phunitHexStr
        self.parseVoltOrCurr()
        self.parseValue()
        print("PHUNIT: ", self.voltORcurr, " - ", self.value, sep="") if self.dbg else None

    def parseVoltOrCurr(self):
        self.voltORcurr = MeasurementType(int(self.phunitHex[0:2], 16)).name 

    def parseValue(self):
        self.value = int(self.phunitHex[2:], 16)

class Anunit:

    def __init__(self, anunitHexStr, debug=False):

        self.anlgMsrmnt = None
        self.userDefinedScale = None

        self.dbg = debug
        self.anunitHex = anunitHexStr
        self.parseAnlgMsrmnt()
        self.parseUserDefinedScale()
        print("ANUNIT: ", self.anlgMsrmnt, " - ", self.userDefinedScale, sep="") if self.dbg else None

    def parseAnlgMsrmnt(self):
        self.anlgMsrmnt = AnlgMsrmnt(int(self.anunitHex[0:2],16)).name

    def parseUserDefinedScale(self):
        self.userDefiend = self.anunitHex[1:]

class Digunit:

    def __init__(self, digunitHexStr, debug=False):
        self.dbg = debug
        self.digunitHex = digunitHexStr
        print("DIGUNIT: ", self.digunitHex) if self.dbg else None
