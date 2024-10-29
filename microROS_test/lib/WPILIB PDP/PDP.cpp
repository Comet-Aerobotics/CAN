#include "WPILIB_PDP.h"
#include <Comet_CAN_Helper.h>


/*********************************************************************************************************
** Function name:           parse_status_frame_1
** Descriptions:            Function to parse PDP Periodic Status Frame 1
*********************************************************************************************************/
void PDP::parse_status_frame_1(uint8_t * data, uint8_t size){
  //data[i] >> (8-n) gets the most significant n bits of the data 
  //(static_cast<uint32_t>(data[i] >> (8-n)) << k converts the data to an int32 so no info is lost when you add k zeroes on the end for...
  //((static_cast<uint32_t>(data[i] >> (8-n)) << k) | (data[2] & ((1 << k) - 1))) uses a bit mask to binary or the k least significant bits on the end, therefore appending the two binary numbers
  status.currents[0] = 0.125 * ((static_cast<uint32_t>(data[0]) << 2) | (data[1] & ((1 << 2) - 1)));
  status.currents[1] = 0.125 * ((static_cast<uint32_t>(data[1] >> (8-6)) << 4) | (data[2] & ((1 << 4) - 1)));
  status.currents[2] = 0.125 * ((static_cast<uint32_t>(data[2] >> (8-4)) << 6) | (data[3] & ((1 << 6) - 1)));
  status.currents[3] = 0.125 * ((static_cast<uint32_t>(data[3] >> (8-2)) << 8) | data[4]);
  status.currents[4] = 0.125 * ((static_cast<uint32_t>(data[5]) << 2) | (data[6] & ((1 << 2) - 1)));
  status.currents[5] = 0.125 * ((static_cast<uint32_t>(data[6] >> (8-6)) << 4) | (data[7] & ((1 << 4) - 1)));
}

/*********************************************************************************************************
** Function name:           parse_status_frame_2
** Descriptions:            Function to parse PDP Periodic Status Frame 2
*********************************************************************************************************/
void PDP::parse_status_frame_2(uint8_t * data, uint8_t size){
  status.currents[6] = 0.125 * ((static_cast<uint32_t>(data[0]) << 2) | (data[1] & ((1 << 2) - 1)));
  status.currents[7] = 0.125 * ((static_cast<uint32_t>(data[1] >> (8-6)) << 4) | (data[2] & ((1 << 4) - 1)));
  status.currents[8] = 0.125 * ((static_cast<uint32_t>(data[2] >> (8-4)) << 6) | (data[3] & ((1 << 6) - 1)));
  status.currents[9] = 0.125 * ((static_cast<uint32_t>(data[3] >> (8-2)) << 8) | data[4]);
  status.currents[10] = 0.125 * ((static_cast<uint32_t>(data[5]) << 2) | (data[6] & ((1 << 2) - 1)));
  status.currents[11] = 0.125 * ((static_cast<uint32_t>(data[6] >> (8-6)) << 4) | (data[7] & ((1 << 4) - 1)));
}

/*********************************************************************************************************
** Function name:           parse_status_frame_3
** Descriptions:            Function to parse PDP Periodic Status Frame 3
*********************************************************************************************************/
void PDP::parse_status_frame_3(uint8_t * data, uint8_t size){
  status.currents[12] = 0.125 * ((static_cast<uint32_t>(data[0]) << 2) | (data[1] & ((1 << 2) - 1)));
  status.currents[13] = 0.125 * ((static_cast<uint32_t>(data[1] >> (8-6)) << 4) | (data[2] & ((1 << 4) - 1)));
  status.currents[14] = 0.125 * ((static_cast<uint32_t>(data[2] >> (8-4)) << 6) | (data[3] & ((1 << 6) - 1)));
  status.currents[15] = 0.125 * ((static_cast<uint32_t>(data[3] >> (8-2)) << 8) | data[4]);
  status.internalResBattery_mOhms = data[5];
  // update_status_3(data[6] * 0.05 + 4.0, data[7] * 1.85851506524 - 90.1416100873);
  status.voltage = data[6] * 0.05 + 4.0; /* 50mV per unit plus 4V. */
  status.temperature = data[7] * 1.85851506524 - 90.1416100873; //magic numbers, but(units are F)
}

/*********************************************************************************************************
** Function name:           parse_energy_status
** Descriptions:            Function to parse PDP Energy Status
*********************************************************************************************************/
void PDP::parse_energy_status(uint8_t * data, uint8_t size){
  // status.totalCurrent = 0.125 * ((static_cast<uint32_t>(data[1]) << 4) | (data[2] & ((1 << 4) - 1))); /* 7.3 fixed pt value in Amps */
  // status.totalPower = 0.125 * ((static_cast<uint32_t>(data[2] >> (8-4)) << 8) | data[3]);  /* 7.3 fixed pt value in Watts */
  uint32_t tempEnergy;
  tempEnergy = static_cast<uint32_t>(data[4] >> (8-4));
  tempEnergy <<=8;
  tempEnergy |= data[5];
  tempEnergy <<=8;
  tempEnergy |= data[6];
  tempEnergy <<=8;
  tempEnergy |= data[7];
  status.totalEnergy *= 0.125 * 0.001 * data[0]; /* mW integrated every TmeasMs; convert from mW to W, multiplied by TmeasMs = joules */
  
}