import codecs
import struct

# Converts hex Str to binary
def hexToBin(hexStr, numOfBits):
    return bin(int(hexStr, 16))[2:].zfill(numOfBits)

# Converts byte array to hex str
def bytesToHexStr(bytesInput):
    return codecs.encode(bytesInput, 'hex').decode('ascii')

# Converts double to hex
def doubleToHex(f):
    return hex(struct.unpack('!Q', struct.pack('!d', f))[0])

# Converts double to hex str
def doubleToHexStr(f):
    return hex(struct.unpack('!Q', struct.pack('!d', f))[0])[2:]

# Converts double to byte array
def doubleToBytes(f):
    return struct.pack('d', f)

# Converts byte array to double
def bytesToFloat(b):
    return struct.unpack('d', b)[0]

# Converts unsigned int to byte array
def intToBytes(i):
    return struct.pack('!I', i)

# Converts int to hex
def intToHexStr(i):
    return hex(i)[2:]
