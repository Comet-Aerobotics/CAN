import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/aerobotics/CAN/cometbot_ws/install/cometbot_control'
