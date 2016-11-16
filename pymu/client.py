import socket
import sys
import os
import time

class Client:
    """
    Client class that creates a client and provides simple functions for connecting to PMUs or PDCs without needing
    to directly use Python's socket library.  Supports INET and UNIX sockets

    :param theDestIp: IP address to connect to.  If using unix socket this is the file name to connect to
    :type theDestIp: str
    :param theDestPort: Port to connect to
    :type theDestPort: int
    :param proto: Protocol to use.  Accepts TCP or UDP
    :type proto: str
    :param sockType: Type of socket to create.  INET or UNIX
    :type sockType: str
    """

    def __init__(self, theDestIp, theDestPort, proto="TCP", sockType="INET"):
    
        self.srcIp = None
        self.srcPort = None
        self.destAddr = None
        self.srcAddr = None
        self.theSocket = None
        self.theConnection = None
        self.useUdp = False
        self.unixSock = False

        self.destIp = theDestIp
        self.destPort = theDestPort
        self.destAddr = (theDestIp, theDestPort)
        if proto.upper() == "UDP":
            self.useUdp = True
        if sockType.upper() == "UNIX":
            self.unixSock = True
        
        self.createSocket()
        self.connectToDest()

    def createSocket(self):
        """Create socket based on constructor arguments""" 
        if self.useUdp:
            if self.unixSock:
                self.theSocket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            else:
                self.theSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            if self.unixSock:
                self.theSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            else:
                self.theSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connectToDest(self):
        """Connect socket to destination IP:Port.  If UNIX socket then use destIP"""
        if not self.useUdp:
            if self.unixSock:
                self.theSocket.connect(self.destIp)
            else:
                self.theSocket.connect(self.destAddr)

    def readSample(self, bytesToRead):
        """
        Read a sample from the socket

        :param bytesToRead: Number of bytes to read from socket
        :type bytesToRead: int

        :return: Byte array of data read from socket
        """
        try:
            if self.useUdp:
                return self.theSocket.recvfrom(bytesToRead)
            else:
                return self.theSocket.recv(bytesToRead)
        except (socket.timeout):
            print("Socket Timeout")
            return ""

    def sendData(self, bytesToSend):
        """Send bytes to destination

        :param bytesToSend: Number of bytes to send
        :type bytesToSend: int
        """
        if self.useUdp:
            if self.unixSock:
                self.theSocket.sendto(bytesToSend, self.destIp)
            else:
                self.theSocket.sendto(bytesToSend, self.destAddr)
        else:
            self.theSocket.send(bytesToSend)

    def stop(self):
        """Close the socket connection"""
        self.theSocket.close()

    def setTimeout(self, numOfSecs):
        """Set socket timeout
        
        :param numOfSecs: Time to wait for socket action to complete before throwing timeout exception
        :type numOfSecs: int
        """
        self.theSocket.settimeout(numOfSecs)

    def __class__(self):
        return "client"
