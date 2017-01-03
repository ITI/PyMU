Python C37.118 data parser.  Contains tools for connecting to PMUs and receiving data.

# Full documentation
http://pythonhosted.org/PyMU/

# Installation
* Must use Python 3.0+

```
pip install PyMU
```

# Quickstart
Quick demo of how to connect to a PMU and start capturing data

### Get Config Frame

```python
import pymu.tools as tools
confFrame = tools.startDataCapture(frameId, port, tcpPort)
```

### Get Data Frame

```python
from pymu.pmuDataFrame import DataFrame
from pymu.client import Client
cli = Client(ip, tcpPort, "TCP")
dataSample = tools.getDataSample(cli)
dataFrame = DataFrame(dataSample, confFrame)
```

You are now able to dive into all the fields of the data frame and config frame in real time.  The example provided (/examples/pmuToCsv.py) writes all the phasor values, frequencies, and ROCOF a csv file.  
