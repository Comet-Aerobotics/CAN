# Building
Using PlatformIO: ```pio build```
If that doesn't work, try ```pio clean``` or ```rm -rf log build install```
# Running 
Using PlatformIO: ```pio run```. PlatformIO can also flash the ESP32.

Explanations for the repository:
extra_packages/custom_messages contains different status messages the C++ code sends, like SparkMaxMesasges from the motors
/lib/: Contains code for interfacing with the MCP as well as sending & recieving SPARK_MAX messages
/src/: Contains the main orchestrator
