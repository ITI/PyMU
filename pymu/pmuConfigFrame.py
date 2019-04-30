"""
Class for parsing Config Frame 1 or 2
"""

from .pmuFrame import PMUFrame
from .pmuEnum import *
from .pmuLib import *

class ConfigFrame(PMUFrame):
    """Parses Config Frame (1 or 2)

    :param frameInHexStr: Config frame as byte array in hex str format
    :type frameInHexStr: str
    :param debug: Print debug statements
    :type debug: bool
    """

    def __init__(self, frameInHexStr, debug=False):
        super().__init__(frameInHexStr, debug) # Parse words common to all frames first
                
    def finishParsing(self):
        """After first 4 bytes are received, the client reads the remaining config frame bytes.  This function parses those remaining bytes"""
        super().finishParsing()
        self.parseTIME_BASE()
        self.parseNUM_PMU()
        self.parseStations()
        self.parseDATARATE()
    
    def parseTIME_BASE(self):
        """Parses resolution of FRACSEC"""
        timebaseSize = 8
        self.time_base = TimeBase(self.frame[self.length:self.length+timebaseSize])
        self.updateLength(timebaseSize)
        print("TIME_BASE: ", self.time_base.baseDecStr, sep="") if self.dbg else None

    def parseNUM_PMU(self):
        """Parse number of PMUs sending data"""
        numpmuSize = 4
        self.num_pmu = int(self.frame[self.length:self.length+numpmuSize], 16)
        self.updateLength(numpmuSize)
        print("NUM_PMU: ", self.num_pmu, sep="") if self.dbg else None

    def parseStations(self):
        """Parse station names for each PMU"""
        self.stations = [None]*self.num_pmu
        for i in range(0, self.num_pmu):
            self.stations[i] = Station(self.frame[self.length:])
            self.updateLength(self.stations[i].length)
            print("***** Station ", (i+1), " *****", sep="") if self.dbg else None
 
    def parseDATARATE(self):
        """Parse data rate at which data will be received"""
        datarateSize = 4
        self.datarate = int(self.frame[self.length:self.length+datarateSize],16)
        self.updateLength(datarateSize)
        print("DATARATE: ", self.datarate) if self.dbg else None

class TimeBase:
    """Class for parsing the TIME_BASE word"""

    def __init__(self, timeBaseHexStr, debug=False):
        self.dbg = debug
        self.timeBaseHex = timeBaseHexStr
        self.flagsBinStr = hexToBin(timeBaseHexStr, 32)[:8] # Not parsed anywhere because so far they aren't being used
        self.baseDecStr = int(timeBaseHexStr[1:], 16)

class Station:
    """Class for parsing station information including all PMU information.  Fields 8-19

    :param theStationHex: Station fields in hex str format
    :type theStationHex: str
    :param debug: Print debug statements
    :type debug: bool
    """

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
        """Updates length of station frames only
        
        :param sizeToAdd: Number of bytes to add to frame length
        :type sizeToAdd: int
        """
        self.length = self.length + sizeToAdd

    def parseSTN(self):
        """Parses station name field"""
        l = 32
        self.stn = bytes.fromhex(self.stationFrame[self.length:self.length+l]).decode('ascii').replace('\x00', '')
        self.updateLength(l)
        print("STN: ", self.stn, sep="") if self.dbg else None

    def parseIDCODE_data(self):
        """Parses station ID code field"""
        l = 4
        self.idcode_data = int(self.stationFrame[self.length:self.length+l], 16)
        self.updateLength(l)
        print("IDCODE_data: ", self.idcode_data) if self.dbg else None

    def parseFORMAT(self):
        """Parses data format field"""
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
        """Parses number of phasors field"""
        l = 4
        self.phnmr = int(self.stationFrame[self.length:self.length+l], 16)
        self.updateLength(l)
        print("PHNMR: ", self.phnmr, sep="") if self.dbg else None

    def parseANNMR(self):
        """Parses number of analog values field"""
        l = 4
        self.annmr = int(self.stationFrame[self.length:self.length+l], 16)
        self.updateLength(l)
        print("ANNMR: ", self.annmr, sep="") if self.dbg else None

    def parseDGNMR(self):
        """Parses number of digital values field"""
        l = 4
        self.dgnmr = int(self.stationFrame[self.length:self.length+l], 16)
        self.updateLength(l)
        print("DGNMR: ", self.dgnmr, sep="") if self.dbg else None

    def parseCHNAME(self):
        """Parses phasor and channel names field"""
        self.numOfChns = self.phnmr + self.annmr + (16 * self.dgnmr)
        self.channels = [None]*self.numOfChns
        l = 32
        for i in range(0, self.numOfChns):
            self.channels[i] = bytes.fromhex(self.stationFrame[self.length:self.length+l]).decode('ascii')
            self.updateLength(l)
            print(self.channels[i]) if self.dbg else None

    def parsePHUNIT(self):
        """Parse conversion factor for phasor channels"""
        self.phunits = [None]*self.phnmr
        l = 8
        for i in range(0, self.phnmr):
            self.phunits[i] = Phunit(self.stationFrame[self.length:self.length+l])
            self.updateLength(l)

    def parseANUNIT(self):
        """Parse conversion factor for analog channels"""
        self.anunits = [None]*self.annmr
        l = 8
        for i in range(0, self.annmr):
            self.anunits[i] = Anunit(self.stationFrame[self.length:self.length+l])
            self.updateLength(l)

    def parseDIGUNIT(self):
        """Parse mask words for digital status words"""
        self.digunits = [None]*self.dgnmr
        l = 8
        for i in range(0, self.dgnmr):
            self.digunits[i] = Digunit(self.stationFrame[self.length:self.length+l])
            self.updateLength(l)

    def parseFNOM(self):
        """Nominal line frequency code and flags"""
        l = 4
        hexDigit = self.stationFrame[self.length+4]
        hexDigitLSB = hexToBin(hexDigit, 8)[7]
        hexDigitDec = int(hexDigitLSB, 2)
        
        self.fnom = FundFreq(hexDigitDec).name
        self.updateLength(l)
        print("FNOM: ", self.fnom) if self.dbg else None

    def parseCFGCNT(self):
        """Parse configuration change count"""
        l = 4
        self.cfgcnt = int(self.stationFrame[self.length:self.length+l], 16)
        self.updateLength(l)
        print("CFGCNT: ", self.cfgcnt) if self.dbg else None

class Phunit:
    """Class for conversion factor for phasor channels
    
    :param phunitHexStr: Conversion factor field in hex str format
    :type phunitHexStr: str
    """

    def __init__(self, phunitHexStr, debug=False):
        self.voltORcurr = None
        self.value = None

        self.dbg = debug
        self.phunitHex = phunitHexStr
        self.parseVoltOrCurr()
        self.parseValue()
        print("PHUNIT: ", self.voltORcurr, " - ", self.value, sep="") if self.dbg else None

    def parseVoltOrCurr(self):
        """Determine if measurement type is voltage or current"""
        self.voltORcurr = MeasurementType(int(self.phunitHex[0:2], 16)).name 

    def parseValue(self):
        """Parse value of conversion factor"""
        self.value = int(self.phunitHex[2:], 16)

class Anunit:
    """Class for conversion factor for analog channels

    :param anunitHexStr: Conversion factor for analog channels field in hex str format
    :type anunitHexStr: str
    """
    def __init__(self, anunitHexStr, debug=False):

        self.anlgMsrmnt = None
        self.userDefinedScale = None

        self.dbg = debug
        self.anunitHex = anunitHexStr
        self.parseAnlgMsrmnt()
        self.parseUserDefinedScale()
        print("ANUNIT: ", self.anlgMsrmnt, " - ", self.userDefinedScale, sep="") if self.dbg else None

    def parseAnlgMsrmnt(self):
        """Parse analog measurement type"""
        self.anlgMsrmnt = AnlgMsrmnt(int(self.anunitHex[0:2],16)).name

    def parseUserDefinedScale(self):
        """Parse user defined scaling"""
        self.userDefiend = self.anunitHex[1:]

class Digunit:
    """Class for mask of digital status words

    :param digunitHexStr: Conversion factor for digital status channels field in hex str format
    :type digunitHexStr: str
    """

    def __init__(self, digunitHexStr, debug=False):
        self.dbg = debug
        self.digunitHex = digunitHexStr
        print("DIGUNIT: ", self.digunitHex) if self.dbg else None
