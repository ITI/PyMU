"""
Tools for common functions relayed to commanding, reading, and parsing PMU data
"""

import pmuDataFrame as pdf

from .client import Client
from .pmuCommandFrame import CommandFrame
from .pmuConfigFrame import ConfigFrame

MAXFRAMESIZE = 65535


def turnDataOff(cli, idcode):
    """
    Send command to turn off real-time data

    :param cli: Client being used to connect to data source
    :type cli: Client
    :param idcode: Frame ID of data source
    :type idcode: int
    """
    cmdOff = CommandFrame("DATAOFF", idcode)
    cli.sendData(cmdOff.fullFrameBytes)


def turnDataOn(cli, idcode):
    """
    Send command to turn on real-time data

    :param cli: Client connection to data source
    :type cli: Client
    :param idcode: Frame ID of data source
    :type idcode: int
    """
    cmdOn = CommandFrame("DATAON", idcode)
    cli.sendData(cmdOn.fullFrameBytes)


def requestConfigFrame2(cli, idcode):
    """
    Send command to request config frame 2

    :param cli: Client connection to data source
    :type cli: Client
    :param idcode: Frame ID of data source
    :type idcode: int
    """
    cmdConfig2 = CommandFrame("CONFIG2", idcode)
    cli.sendData(cmdConfig2.fullFrameBytes)


def readConfigFrame2(cli, debug=False):
    """
    Retrieve and return config frame 2 from PMU or PDC

    :param cli: Client connection to data source
    :type cli: Client
    :param debug: Print debug statements
    :type debug: bool
    :return: Populated ConfigFrame
    """
    configFrame = None

    s = cli.readSample(4)
    configFrame = ConfigFrame(pdf.bytesToHexStr(s), debug)
    expSize = configFrame.framesize
    s = cli.readSample(expSize - 4)
    configFrame.frame = configFrame.frame + pdf.bytesToHexStr(s).upper()
    configFrame.finishParsing()

    return configFrame


def getDataSample(rcvr, debug=False):
    """
    Get a data sample regardless of TCP or UDP connection

    :param rcvr: Object used for receiving data frames
    :type rcvr: :class:`Client`/:class:`Server`
    :param debug: Print debug statements
    :type debug: bool
    :return: Data frame in hex string format
    """
    fullHexStr = ""

    if isinstance(rcvr, Client):
        introHexStrSize = 4
        introHexStr = pdf.bytesToHexStr(rcvr.readSample(introHexStrSize))
        totalFrameLength = int(introHexStr[5:], 16)
        lenToRead = totalFrameLength - introHexStrSize
        remainingHexStr = pdf.bytesToHexStr(rcvr.readSample(lenToRead))

        fullHexStr = introHexStr + remainingHexStr
    else:
        fullHexStr = pdf.bytesToHexStr(rcvr.readSample(64000))

    return fullHexStr


def startDataCapture(idcode, ip, port=4712, tcpUdp="TCP", debug=False):
    """
    Connect to data source, request config frame, send data start command

    :param idcode: Frame ID of PMU
    :type idcode: int
    :param ip: IP address of data source
    :type ip: str
    :param port: Command port on data source
    :type port: int
    :param tcpUdp: Use TCP or UDP
    :type tcpUdp: str
    :param debug: Print debug statements
    :type debug: bool

    :return: Populated :py:class:`pymu.pmuConfigFrame.ConfigFrame` object
    """
    configFrame = None

    cli = Client(ip, port, tcpUdp)
    cli.setTimeout(5)

    while configFrame is None:
        requestConfigFrame2(cli, idcode)
        configFrame = readConfigFrame2(cli, debug)

    turnDataOn(cli, idcode)
    cli.stop()

    return configFrame


def getStations(configFrame):
    """
    Returns all station names from the config frame

    :param configFrame: ConfigFrame containing stations
    :type configFrame: ConfigFrame

    :return: List containing all the station names
    """
    stations = []
    for s in configFrame.stations:
        print("Station:", s.stn)
        stations.append(s)

    return stations


def createAggPhasors(configFrame):
    """
    Creates an array of aggregate phasors for data collection

    :param configFrame: ConfigFrame containing stations
    :type configFrame: ConfigFrame

    :return: List containing all the station AggPhasor objects
    """
    pmus = []
    for s in getStations(configFrame):
        phasors = []
        print("Name:", s.stn)
        for p in range(0, s.phnmr):
            print("Phasor:", s.channels[p])
            theUnit = "VOLTS"
            if s.phunits[p].voltORcurr == "CURRENT":
                theUnit = "AMPS"
            phasors.append(
                pdf.AggPhasor(s.stn.strip() + "/" + s.channels[p].strip(), theUnit)
            )

        pmus.append(phasors)

    return pmus


def parseSamples(data, configFrame, pmus):
    """
    Takes an array of dataFrames and inserts the data into an array of aggregate phasors

    :param data: List containing all the data samples
    :type data: List
    :param configFrame: ConfigFrame containing stations
    :type configFrame: ConfigFrame
    :param pmus: List of phasor values
    :type pmus: List

    :return: List containing all the phasor values
    """
    numOfSamples = len(data)
    for s in range(0, numOfSamples):
        for p in range(0, len(data[s].pmus)):
            for ph in range(0, len(data[s].pmus[p].phasors)):
                utcTimestamp = data[s].soc.utcSec + (
                    data[s].fracsec / configFrame.time_base.baseDecStr
                )
                pmus[p][ph].addSample(
                    utcTimestamp,
                    data[s].pmus[p].phasors[ph].mag,
                    data[s].pmus[p].phasors[ph].rad,
                )

    return pmus
