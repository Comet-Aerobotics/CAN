# Status of one SPARK MAX (same fields as microROS_test custom_messages/SparkMaxMessage)
uint8 device_id
float32 applied_output   # -1 .. 1
float32 velocity         # RPM
float32 position         # rotations
uint8 temperature        # deg C
float32 voltage          # volts
float32 current          # raw 12-bit value for now (probably amps * 32, needs checking)
