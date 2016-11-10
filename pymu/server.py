#!/usr/bin/python

import socket
import sys
import os
import time

class Server:
    
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

    # Starts the python server and listens for connections
    def startServer(self, queueLen):
        if self.useUdp:
            self.socketConn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print("Starting UDP Server on", self.serverAddr) if self.printInfo else None
            self.socketConn.bind(self.serverAddr)
        else:
            self.socketConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Starting TCP Server on", self.serverAddr) if self.printInfo else None
            self.socketConn.bind(self.serverAddr)
            self.socketConn.listen(queueLen)

    # Will block program execution until a connection is achieved
    def waitForConnection(self):
        print("**********") if self.printInfo else None
        if self.useUdp:
            return
        print("Waiting for connection...") if self.printInfo else None

        self.connection, self.clientAddr = self.socketConn.accept()

    # Will read exactly exactly as many bytes as specified by length and return them as an int
    def readSample(self, length):
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

    # Closes server connections
    def stop(self):
        print("\n**********") if self.printInfo else None
        if self.useUdp:
            self.socketConn.close()
        else:
            print("Stopping server...") if self.printInfo else None
            #self.connection.close()
        
        print("Stopping", self.serverAddr) if self.printInfo else None

    def setTimeout(self, numOfSecs):
        self.socketConn.settimeout(numOfSecs)

    def __class__(self):
        return "server"
