from datetime import datetime
from .pmuEnum import *
from .pmuLib import *

class PMUFrame:
    """
    Super class for all C37.118-2005/C37.118-2011 frames

    :param frameInHexStr: Bytes from frame (any time) in hex str format
    :type strameInHexStr: str
    :param debug: Print debug statements
    :type debug: bool
    """

    def __init__(self, frameInHexStr, debug=False):
        """
        PMUFrame constructor

        :param frameInHexStr: Hex representation of frame bytes
        :type frameInHexStr: str
        :param debug: Print debug statements or not
        :type debug: bool
        """
     
        self.length = 0

        self.dbg = debug
        self.frame = frameInHexStr.upper()
        self.parseSYNC()
        self.parseFRAMESIZE()

    def finishParsing(self):
        """
        When getting the config frame, the size is unknown.  After creating a PMUFrame with the first 4 bytes, the remaining frame bytes are read
        and added to self.frame.  Once that is populated the remaining fields can be parsed
        """
        self.parseIDCODE()
        self.parseSOC()
        self.parseFRACSEC()
        self.parseCHK()

    def parseSYNC(self):
        """Parse frame synchronization word"""
        self.sync = SYNC(self.frame[:4])
        self.updateLength(4)

    def parseFRAMESIZE(self):
        """Parse frame size"""
        framesizeSize = 4
        self.framesize = int(self.frame[self.length:self.length+framesizeSize], 16)
        self.updateLength(framesizeSize)
        print("FRAMESIZE: ", self.framesize) if self.dbg else None

    def parseIDCODE(self):
        """Parse data stream ID number"""
        idcodeSize = 4
        self.idcode = int(self.frame[self.length:self.length+idcodeSize], 16)
        self.updateLength(idcodeSize)
        print("IDCODE: ", self.idcode) if self.dbg else None

    def parseSOC(self):
        """Parse second-of-century timestamp"""
        socSize = 8
        self.soc = SOC(self.frame[self.length:self.length+socSize])
        self.updateLength(socSize)

    def parseFRACSEC(self):
        """Parse fraction of second and time quality word"""
        fracsecSize = 8
        self.fracsec = int(self.frame[self.length:self.length+fracsecSize], 16)
        self.updateLength(fracsecSize)
        print("FRACSEC: ", self.fracsec) if self.dbg else None

    def parseCHK(self):
        """Parse CRC-CCITT word"""
        chkSize = 4
        self.chk = self.frame[-chkSize:]
        print("CHK: ", self.chk) if self.dbg else None

    def updateLength(self, sizeToAdd):
        """Keeps track of index for overall frame"""
        self.length = self.length + sizeToAdd

class SYNC:
    """Class for describing the frame synchronization word

    :param syncHexStr: Sync byte array in hex str format
    :type syncHexStr: str
    :param debug: Print debug statements
    :type debug: bool
    """
    
    def __init__(self, syncHexStr, debug=False):
        self.dbg = debug
        self.syncHex = syncHexStr
        self.parseType()
        self.parseVers()

    def parseType(self):
        """Parse frame type"""
        typeBinStr = hexToBin(self.syncHex[2], 3)
        typeNum = int(typeBinStr, 2)
        self.frameType = FrameType(typeNum).name
        print("Type: ", self.frameType) if self.dbg else None

    def parseVers(self):
        """Parse frame version"""
        versBinStr = hexToBin(self.syncHex[3], 4)
        self.frameVers = int(versBinStr, 2)
        print("Vers: ", self.frameVers) if self.dbg else None

class SOC:
    """Class for second-of-century (SOC) word (32 bit unsigned)

    :param socHexStr: Second-of-century byte array in hex str format
    :type socHexStr: str
    :param debug: Print debug statements
    :type debug: bool
    """

    def __init__(self, socHexStr, debug=False):
        self.dbg = debug
        self.socHex = socHexStr
        self.secCount = int(socHexStr, 16)
        self.parseSecCount()
        print("SOC: ", self.secCount, " - ", self.formatted) if self.dbg else None

    def parseSecCount(self):
        """Parse SOC into UTC timestamp and pretty formatted timestamp"""
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

