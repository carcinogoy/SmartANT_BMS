# SmartANT_BMS
Pulls info from the SmartAnt BMS via bluetooth to a raspberry pi


No clue how I got the bluetooth working on the pi, my steps as far as I can remember.

    bluetoothctl
    scan on
    Find the device ID
    pair ID
    trust ID


    sudo rfcomm bind /dev/rfcomm0 ID 1
