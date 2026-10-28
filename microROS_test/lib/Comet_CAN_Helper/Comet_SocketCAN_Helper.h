#ifndef COMET_CAN_HELPER_H
#define COMET_CAN_HELPER_H

#define NO_ACTIVE_CAN_DEVICES -1
// There should be no FRC devices with a device id equal to 0!
#define NO_MATCHING_FRC_DEVICE_ID 255

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <unistd.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include "SocketCAN_Device_Interface.h"
#include "Comet_SocketCAN_Common.h"



/*
Removed CAN0 int because mcp required a pin number, but irrelevant because no longer using MCP2515
Removed MCP filters/masks
"String" was an Arduino related datatype, so replaced it with std::string


*/
class Comet_SocketCAN_Helper{

    Comet_SocketCAN_Helper(int socket_fd):can_socket(socket_fd){ //fd stands for file descriptor

        for(int i = 0; i < MAX_CAN_DEVICES; i++){
            can_devices[i] = nullptr;
        }
    }


  /*
    * Functions
    */
    // When parsing, if there is an 0x8 at the beggining, that is added by the mcp library to signify it's an extended frame
                // See line 1233 in mcp_can.cpp
    std::string parse_CAN_frame();

    // CAN Core functions
    uint8_t send_enabled_heartbeat();             // Send enabled heartbeat
    uint8_t send_disabled_heartbeat();            // Send disabled heartbeat
    std::string send_message();   // Sends the queued CAN frame of the selected CAN dev and then moves to the next dev

    // SHOULD ONLY BE CALLED IN SETUP() OR DURING DEVICE INITIALIZATION
    uint8_t add_to_CAN_dev_arr(ICAN_Device *CAN_dev);        // Adds the Spark Max object to the list of Spark Maxs
    



private:
    /*
    * Constants/variables
    */
    int can_socket;
    int can0 = can_socket;
    ICAN_Device* can_devices[MAX_CAN_DEVICES]; // Array of pointers to CAN devices
    uint8_t num_CAN_devs = 0;
    uint32_t selected_CAN_dev = 0;
    const uint32_t DEVICE_ID_MASK = FRC_dev_id_mask; // Mask everything but device ID bits (last 6). Follows FRC CAN Protocol

    // For reading input buffer
    long unsigned int rxId;
    unsigned char len = 0;
    unsigned char rxBuf[8];

    /*
    * Heartbeat frame
    */
    const uint32_t HEARTBEAT_ID = 0x2052C80;
    const uint8_t HEARTBEAT_DLC = 8;
    uint8_t heartbeat_data_enabled[8] = {255, 255, 255, 255, 255, 255, 255, 255};
    uint8_t heartbeat_data_disabled[8] = {0, 0, 0, 0, 0, 0, 0, 0};

    /*
    * Functions
    */
    
    int16_t get_next_enabled_device();
    uint8_t get_device_from_FRC_id(uint8_t frc_id);





};


#endif
