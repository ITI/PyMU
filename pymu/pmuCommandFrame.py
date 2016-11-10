# # # # # #
# Class for creating a Command Frame
# based on C37.118-2011.  
# # # # # #

from pmuFrame import PMUFrame
from pmuEnum import *
from time import time
from datetime import datetime
from CRCCCITT import CRCCCITT

class CommandFrame(PMUFrame):

    def __init__(self, commandStr, pmuIdInt, debug=False):

        self.commandHex = None
        self.fullFrameHexStr = None
        self.fullFrameBytes = None
        self.length = 0

        self.dbg = debug
        self.command = Command[commandStr.upper()]
        self.pmuId = hex(pmuIdInt)
        self.createCommand()

    def createCommand(self):
       self.sync = self.genSync() # Command frame sync bytes
       self.idcode = self.genIdcode() 
       self.soc = self.genSoc()
       self.fracsec = self.genFracsec() # Should eventually make this but not a priority
       self.commandHex = self.genCmd()
       self.framesize = hex(int((self.length+8)/2))[2:].zfill(4) # No support for extended frame yet 
       cmdHex = self.sync + self.framesize + self.idcode + self.soc + self.fracsec + self.commandHex
       self.genChk(cmdHex)
       cmdHex = cmdHex + self.chk
       self.fullFrameHexStr = cmdHex.upper()
       self.fullFrameBytes = bytes.fromhex(self.fullFrameHexStr)

    # # # # # #
    # Methods follow fields in Command Frame.
    # Return Hex str for easy debugging
    # # # # # #
    def genSync(self):
        self.updateLength(4)
        return "AA41"

    def genIdcode(self):
        self.updateLength(4)
        return self.pmuId[2:].zfill(4).upper() 

    def genSoc(self):
        self.updateLength(8)
        tm = time()
        hex_val = hex(int(round(tm))).upper()[2:].zfill(4)
        return hex_val.upper()

    def genFracsec(self):
        self.updateLength(8)
        now = datetime.now()
        hex_val = hex(now.microsecond)[2:].zfill(8)
        return hex_val.upper() 

    def genCmd(self):
        self.updateLength(4)
        cmdHex = hex(int(bin(self.command.value)[2:].zfill(16), 2))[2:].zfill(4)
        return cmdHex.upper()

    def genChk(self, crcInputData):
        crcCalc = CRCCCITT('FFFF')
        frameInBytes = bytes.fromhex(crcInputData)
        theCrc = hex(crcCalc.calculate(frameInBytes))[2:].zfill(4)
        self.chk = theCrc.upper()
