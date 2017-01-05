.. PyMU documentation master file, created by
   sphinx-quickstart on Fri Nov 11 00:46:09 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyMU's documentation!
================================

This library is used for accessing C37.118 data in real-time.  The library is based on the C37.118.2-2011 standard and knowing that standard makes understanding this library much easier.

Installation
------------
* Must use Python 3.0+::

    pip install PyMU

Quickstart
----------
Quick demo of how to connect to a PMU and start capturing data.  A basic understanding of TCP/UDP, Client/Server, and PMU configuration is assumed.

* Get Config Frame::

    import pymu.tools as tools
    confFrame = tools.startDataCapture(frameId, port, tcpPort)

* Get Data Frame::

    from pymu.pmuDataFrame import DataFrame
    from pymu.client import Client
    cli = Client(ip, tcpPort, "TCP")
    dataSample = tools.getDataSample(cli)
    dataFrame = DataFrame(dataSample, confFrame)

You are now able to dive into all the fields of the data frame and config frame in real time.  The example provided (/examples/pmuToCsv.py) writes all the phasor values, frequencies, and ROCOF a csv file.  

Contents
--------

.. toctree::
   :maxdepth: 2

   pymu 
   



Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

