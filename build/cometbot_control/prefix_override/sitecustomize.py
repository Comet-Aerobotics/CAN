import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/ros/Documents/CAN-CTRE-PDP/install/cometbot_control'
