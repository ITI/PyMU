# # # # # #
# Super Class for creating all types of frames
# based on C37.118-2011. Contains the fields common
# to all C37.118 frames
# # # # # #

from datetime import datetime
from pmuEnum import *
from pmuLib import *

class PMUFrame:

    def __init__(self, frameInHexStr, debug=False):
     
        self.sync = None
        self.framesize = None
        self.idcode = None
        self.soc = None
        self.fracsec = None
        self.chk = None
        self.length = 0

        self.dbg = debug
        self.frame = frameInHexStr.upper()
        self.parseSYNC()
        self.parseFRAMESIZE()

    def finishParsing(self):
        self.parseIDCODE()
        self.parseSOC()
        self.parseFRACSEC()
        self.parseCHK()

    def parseSYNC(self):
        self.sync = SYNC(self.frame[:4])
        self.updateLength(4)

    def parseFRAMESIZE(self):
        framesizeSize = 4
        self.framesize = int(self.frame[self.length:self.length+framesizeSize], 16)
        self.updateLength(framesizeSize)
        print("FRAMESIZE: ", self.framesize) if self.dbg else None

    def parseIDCODE(self):
        idcodeSize = 4
        self.idcode = int(self.frame[self.length:self.length+idcodeSize], 16)
        self.updateLength(idcodeSize)
        print("IDCODE: ", self.idcode) if self.dbg else None

    def parseSOC(self):
        socSize = 8
        self.soc = SOC(self.frame[self.length:self.length+socSize])
        self.updateLength(socSize)

    def parseFRACSEC(self):
        fracsecSize = 8
        self.fracsec = int(self.frame[self.length:self.length+fracsecSize], 16)
        self.updateLength(fracsecSize)
        print("FRACSEC: ", self.fracsec) if self.dbg else None

    def parseCHK(self):
        chkSize = 4
        self.chk = self.frame[-chkSize:]
        print("CHK: ", self.chk) if self.dbg else None

    def updateLength(self, sizeToAdd):
        self.length = self.length + sizeToAdd

class SYNC:
    
    syncHex = None
    frameType = None
    frameVers = None
    dbg = False

    def __init__(self, syncHexStr, debug=False):
        self.dbg = debug
        self.syncHex = syncHexStr
        self.parseType()
        self.parseVers()

    def parseType(self):
        typeBinStr = hexToBin(self.syncHex[2], 3)
        typeNum = int(typeBinStr, 2)
        self.frameType = FrameType(typeNum).name
        print("Type: ", self.frameType) if self.dbg else None

    def parseVers(self):
        versBinStr = hexToBin(self.syncHex[3], 4)
        self.frameVers = int(versBinStr, 2)
        print("Vers: ", self.frameVers) if self.dbg else None

class SOC:

    socHex = None
    secCount = None
    yyyy = None
    mm = None
    dd = None
    hh = None
    mi = None
    ss = None
    formatted = None
    utcSec = None
    dbg = False

    def __init__(self, socHexStr, debug=False):
        self.dbg = debug
        self.socHex = socHexStr
        self.secCount = int(socHexStr, 16)
        self.parseSecCount()
        print("SOC: ", self.secCount, " - ", self.formatted) if self.dbg else None

    def parseSecCount(self):
        parsedDate = datetime.fromtimestamp(self.secCount)
        self.yyyy = parsedDate.year
        self.mm = parsedDate.month
        self.dd = parsedDate.day
        self.hh = parsedDate.hour
        self.mi = parsedDate.minute
        self.ss = parsedDate.second
        self.ff = 0
        self.formatted = "{:0>4}/{:0>2}/{:0>2} {:0>2}:{:0>2}:{:0>2}".format(self.yyyy, self.mm, self.dd, self.hh, self.mi, self.ss)
        dt = datetime(self.yyyy, self.mm, self.dd, self.hh, self.mi, self.ss) 
        self.utcSec = (dt - datetime(1970, 1, 1)).total_seconds()

