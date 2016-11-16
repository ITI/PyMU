import socket
import sys
import os
import time

class Server:
    """
    Server class that creates a server and provides simple functions for incoming connections/data from PMUs or PDCs without needing
    to directly use Python's socket library.  Supports INET sockets only (will eventually be updated).

    :param thePort: Local port to listen on
    :type thePort: int
    :param proto: Protocol to use.  Accepts TCP or UDP
    :type proto: str
    :param printInfo: Specifies whether or not to print debug statements
    :type printInfo: bool
    """
    
    def __init__(self, thePort, proto="TCP", printInfo=False):

        self.serverIP = None
        self.socketConn = None
        self.connection = None
        self.clientAddr = None
        self.serverAddr = ""
        self.printInfo = printInfo
        
        self.serverPort = thePort
        self.serverAddr = (self.serverAddr, self.serverPort)
        if (proto.lower() == "udp"):
            self.useUdp = True
        else:
            self.useUdp = False

        self.startServer(5)
        self.waitForConnection()

    def startServer(self, queueLen):
        """Starts the python server and listens for connections

        :param queueLen: Max number of queued connections.  Usually defaults to 5
        :type queueLen: int
        """
        if self.useUdp:
            self.socketConn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print("Starting UDP Server on", self.serverAddr) if self.printInfo else None
            self.socketConn.bind(self.serverAddr)
        else:
            self.socketConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Starting TCP Server on", self.serverAddr) if self.printInfo else None
            self.socketConn.bind(self.serverAddr)
            self.socketConn.listen(queueLen)

    def waitForConnection(self):
        """Will block program execution until a connection is achieved"""
        print("**********") if self.printInfo else None
        if self.useUdp:
            return
        print("Waiting for connection...") if self.printInfo else None

        self.connection, self.clientAddr = self.socketConn.accept()

    def readSample(self, length):
        """Will read exactly exactly as many bytes as specified by length and return them as an int"""
        data = ""
        if self.useUdp:
            data, address = self.socketConn.recvfrom(length)
        else:
            if self.connection == None:
                self.waitForConnection()
            data = self.connection.recv(length)

        if data:
            return data
        else:
            print("Invalid/No Data Received") if self.printInfo else None

    def stop(self):
        """Closes server connections"""
        print("\n**********") if self.printInfo else None
        if self.useUdp:
            self.socketConn.close()
        else:
            print("Stopping server...") if self.printInfo else None
            #self.connection.close()
        
        print("Stopping", self.serverAddr) if self.printInfo else None

    def setTimeout(self, numOfSecs):
        """Set socket timeout
        
        :param numOfSecs: Time to wait for socket action to complete before throwing timeout exception
        :type numOfSecs: int
        """
        self.socketConn.settimeout(numOfSecs)

    def __class__(self):
        return "server"
