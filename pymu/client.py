import socket
import sys
import os
import time

# # # # # #
# Class do easily create a client without needing to 
# without needing to consult socket library.  Supports
# TCP/UDP and UNIX/INET sockets
# # # # # #

class Client:

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
        if not self.useUdp:
            if self.unixSock:
                self.theSocket.connect(self.destIp)
            else:
                self.theSocket.connect(self.destAddr)

    def readSample(self, bytesToRead):
        try:
            if self.useUdp:
                return self.theSocket.recvfrom(bytesToRead)
            else:
                return self.theSocket.recv(bytesToRead)
        except (socket.timeout):
            print("Socket Timeout")
            return ""

    def sendData(self, bytesToSend):
        if self.useUdp:
            if self.unixSock:
                self.theSocket.sendto(bytesToSend, self.destIp)
            else:
                self.theSocket.sendto(bytesToSend, self.destAddr)
        else:
            self.theSocket.send(bytesToSend)

    def stop(self):
        self.theSocket.close()

    def setTimeout(self, numOfSecs):
        self.theSocket.settimeout(numOfSecs)

    def __class__(self):
        return "client"
