Python C37.118 data parser.  Contains tools for connecting to PMUs and receiving data.

Full documentation at http://pythonhosted.org/PyMU/

# Quickstart - Quick demo of how to connect to a PMU start capturing data

### Get Config Frame

```
import pymu.tools as tools
confFrame = tools.startDataCapture(frameId, port, tcpPort)
```

### Get Data Frame

```
from pymu.pmuDataFrame import DataFrame
from pymu.client import Client
cli = Client(ip, tcpPort, "TCP")
dataSample = tools.getDataSample(cli)
dataFrame = DataFrame(dataSample, confFrame)
```

You are now able to dive into all the fields of the data frame and config frame in real time.  The example provided writes all the phasor values, frequencies, and ROCOF a csv file.  
