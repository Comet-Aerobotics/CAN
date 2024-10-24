/*
::::To Do::::
++++ DONE
---- TODO
~~~~ IDEA

---- Define explicit error codes for adding devices to arr and other functions
*/

#ifndef WPILIB_PDP_H
#define WPILIB_PDP_H

#include <Arduino.h>
#include <mcp_can.h>

#include "Comet_CAN_Common.h"
#include "CAN_Device_Interface.h"
#include "Comet_CAN_Helper.h"

/*********************************************************************************************************
** PDP class
** For configuring and controlling SPARK MAXs
*********************************************************************************************************/
class PDP : public ICAN_Device {
public:
    /*
    * Constructor. MUST BE CALLED AFTER THE CAN MODULE HAS BEEN SETUP
    */
   
    PDP(uint8_t device_id) : device_id(device_id){
    }

    byte initialize_PDP(Comet_CAN_Helper &CAN_Helper,  MCP_CAN &CAN0){
        current_control_frame = empty_frame;
        active = true;

        if (CAN_Helper.add_to_CAN_dev_arr(this) == CAN_OK){
            return CAN_OK;
        }
        else{
            return CAN_FAIL;
        }
    }
    /*
    * Functions
    */
    bool is_FRC() const override {
        return true;
    }

    uint8_t get_device_id() const override {
        if (is_FRC()) {
            return device_id;
        } else {
            return 0; // Return a default value or handle appropriately if ID cannot be reported
                        // There should be no FRC devices with a device id equal to 0!
        }
    }

    bool is_active() const override{
        return active;
    }

    void set_active(bool input) override{
        active = input;
    }

    void parse_CAN_frame(u_int32_t rxId, u_int8_t len, u_int8_t *rxBuf) override{
        // Handle data parsing for specific frames
        if ((rxId & FRC_dev_id_mask) == Status1) {
          parse_status_frame_1(rxBuf, len);
        } else if ((rxId & FRC_dev_id_mask) == Status2) {
          parse_status_frame_2(rxBuf, len);
        } else if ((rxId & FRC_dev_id_mask) == Status3) {
          parse_status_frame_3(rxBuf, len);
        }
        
        
        // Add more cases if necessary
    }

    PDP_status get_status(){
        return status;
    }

    String to_string(){
        double totalCurrent = 0.0;
        String currents = "\nCurrents: {";
        for (int i = 0; i < 15; i++){
            currents+=String(status.currents[i]) + ", ";
            totalCurrent+=status.currents[i];
        }
        return "Device id: " + String(get_device_id()) + 
                "\nTemperature: " + String(status.temperature) +
                currents + String(status.currents[15]) + "}" +
                "\nTotal Current: " + String(totalCurrent + status.currents[15]);
    }

    can_frame get_current_frame() const override {
        return current_control_frame; 
    }

    void clear_current_frame() override {
        current_control_frame = empty_frame;
    }

    // Default destructor
    ~PDP(){
    }

private:
    /*
    * Constants/variables
    */
    PDP_status status = empty_pdp_status;
    can_frame current_control_frame;
    bool active = false;
    u_int8_t device_id;

    const float kCurrentScalar = 0.125f;

    void parse_status_frame_1(uint8_t *data, uint8_t size);   // Parse status frame 1
    void parse_status_frame_2(uint8_t *data, uint8_t size);   // Parse status frame 2
    void parse_status_frame_3(uint8_t *data, uint8_t size);   // Parse status frame 3
};

#endif
