# ComfoAir (WHR950)
Port of ComfoAir protocol to ESPHome.io firmware.

Based on [wichers/esphome-comfoair](https://github.com/wichers/esphome-comfoair)

## Previous setup using MQTT
I've been using a NodeMCU v2 (ESP8266) connected to my ComfoAir WHR950, which sent all data to MQTT. Check out [nilsbebelaar/esp8266-whr930-mqtt](https://github.com/nilsbebelaar/esp8266-whr930-mqtt) for more details.

This mostly worked okay, but I have been wanting to switch to ESPHome for some time now to improve the reliability. The MQTT route isn't super responsive, and when the WiFi drops, I have to go into the basement to reset the device. I'm hoping ESPHome will be more reliable.

## Testing
In order to test the new code running on the ESP, I created a python script to simulate the ComfoAir device. (As I didn't fancy sitting in my cold basement while testing).
The [dummyWHR.py](dummyWHR.py) can be used in combination with a RS232 to USB cable. Connect the cable to a computer and start the script (you'll probably need to change the COM port on the second line).  
It will send hard coded values for most of the possible data 'addresses' as described in [the protocol description](doc\Protokollbeschreibung_ComfoAir.pdf).  
Configurations that are 'set' by the ESP, will printed as output on the console for debugging.


