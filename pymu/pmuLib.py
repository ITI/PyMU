"""
Commonly used functions for parsing PMU Frames
"""

import codecs
import struct

def hexToBin(hexStr, numOfBits):
    """Converts hex string to binary

    :param hexStr: Hex value in string format
    :type hexStr: str
    :param numOfBits: Number of bits to convert
    :type numOfBits: int

    :return: bits representing the hex values
    """
    return bin(int(hexStr, 16))[2:].zfill(numOfBits)

def bytesToHexStr(bytesInput):
    """Converts byte array to hex str

    :param bytesInput: byte array to convert
    :type bytesInput: byte-array

    :return: Hex string representing bytesInput
    """
    
    return codecs.encode(bytesInput, 'hex').decode('ascii')

def doubleToHex(f):
    """Converts double to hex

    :param f: Double value to convert
    :type f: double

    :return: Hex representation of double value
    """
    return hex(struct.unpack('!Q', struct.pack('!d', f))[0])

def doubleToHexStr(f):
    """Converts double to hex str

    :param f: Double value to convert
    :type f: double

    :return: Hex string representation of double value
    """
    return hex(struct.unpack('!Q', struct.pack('!d', f))[0])[2:]

def doubleToBytes(f):
    """Converts double to byte array

    :param f: Double value to convert
    :type f: double

    :return: Byte array representation of double value
    """
    return struct.pack('d', f)

def bytesToFloat(b):
    """Converts byte array to double

    :param b: Byte array to convert
    :type b: byte-array

    :return: Float value
    """
    return struct.unpack('d', b)[0]

def intToBytes(i):
    """Converts unsigned int to byte array

    :param i: Integer value to convert
    :type i: int

    :return: Byte array representing i
    """
    return struct.pack('!I', i)

def intToHexStr(i):
    """Converts int to hex

    :param i: Integer value to convert
    :type i: int

    :return: Hex string representing i
    """
    return hex(i)[2:]
