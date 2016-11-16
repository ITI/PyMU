"""
File containing all the enums used for PyMU
"""

from enum import Enum

class FrameType(Enum):
    Data = 0
    Header = 1
    Config1 = 2
    Config2 = 3
    Command = 4
    Config3 = 5

class NumType(Enum):
    INTEGER = 0
    FLOAT = 1

class PhsrFmt(Enum):
    RECT = 0
    POLAR = 1

class FundFreq(Enum):
    HZ60 = 0
    HZ50 = 1

class MeasurementType(Enum):
    VOLTAGE = 0
    CURRENT = 1

class AnlgMsrmnt(Enum):
    INSTANTANEOUS = 0
    RMS = 1
    PEAK = 2

class DataError(Enum):
    GOOD = 0
    PMUERROR = 1
    TESTMODE = 2
    PMUERROR_NOVALUES = 3

class PmuSync(Enum):
    UTCSOURCE = 0
    NO_UTCSOURCE = 1

class Sorting(Enum):
    TIMESTAMP = 0
    ARRIVAL = 1

class Trigger(Enum):
    NO_TRIGGER = 0
    TRIGGER = 1

class ConfigChange(Enum):
    DID_CHANGE = 0
    WILL_CHANGE = 1

class DataModified(Enum):
    OTHER = 0
    POSTPROCESSING = 1

class TimeQuality(Enum):
    NOT_USED = 0
    ERR_LT100_NS = 1
    ERR_LT1_US = 2
    ERR_LT10_US = 3
    ERR_LT100_US = 4
    ERR_LT1_MS = 5
    ERR_LT10_MS = 6
    ERR_GT10_MS_UNKNOWN = 7

class UnlockedTime(Enum):
    LOCKED_LT10S = 0
    BTWN_10S_100S = 1
    BTWN_100S_1000S = 2
    GT_1000S = 3

class TriggerReason(Enum):
    MANUAL = 0
    MAG_LOW = 1
    MAG_HI = 2
    PHASE_ANG_DIFF = 3
    FREQ_HI_LO = 4
    DF_DT_HI = 5
    RESERVED = 6
    DIGITAL = 7

class Command(Enum):
    UNDEFINED = 0
    DATAOFF = 1
    DATAON = 2
    HEADER = 3
    CONFIG1 = 4
    CONFIG2 = 5
    CONFIG3 = 6
 
class Unit(Enum):
    VOLTS = 0
    AMPS = 1
    RADIANS = 2
    DEGREES = 3
