import paho.mqtt.client as mqtt
import time
from binascii import unhexlify
import serial

mqttBroker = "192.168.1.100"
deviceName = "BatteryBank1"
rfDevice = "/dev/rfcomm0"
cellCount = 16

client = mqtt.Client(deviceName)
client.connect(mqttBroker)
serial = serial.Serial(
    port=rfDevice,
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout = 0)


#ENUMS stolen from the android app
MOSFET_Discharge_String=["OFF", "ON", "CellLow", "OverCurrent", "Level2 OverCurrent", "TotalVoltLow", "Battery TemperatureHigh", "Mos TemperatureHigh", "CurrentError", "WireDisconnected", "MainBoardHighTemperature", "ChargeMosON", "ShortCircuit", "DisChgMOS Error", "PrechargeFailure", "Manual OFF", "Level2 CellLow", "Low Temperature", "CellDiffHigh", "19", "CellVoltCheckError", "21", "22", "23", "24"]

MOSFET_Charge_String=["OFF", "ON", "CellHigh", "OverCurrent", "BatteryFull", "TotalVoltHigh", "BatteryTemperatureHigh", "MosTemperatureHigh", "CurrentError", "WireDisconnected", "MainBoardHighTemperature", "Unknown", "PrechargeFailure", "ChgMOS Error", "Waiting", "Manual OFF", "Level2 CellHigh", "LowTemperature", "CellDiffHigh", "19", "CellVoltCheckError", "21", "22", "23", "24"]

Balance_String=["OFF", "BalanceLimit", "CellDiffBalance", "BalanceHighTemperature", "AutoBalance", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]

#put your mqtt,post,blahblah here
def handleString(dataName, data):
    print(data)
    #client.publish(deviceName + "/" + dataName, data)


while True:
    try:
        serial.write(bytes.fromhex('DBDB00000000'))
    except: 
        serial.close()
    time.sleep(1)
    if(serial.isOpen() == False):
        serial.open()
    ANTSerial = serial.read(140)

    #Skip if invalid data
    if (len(ANTSerial) < 140):
        continue
    if (ANTSerial[0:4] != bytes([0xaa, 0x55, 0xaa, 0xff])):
        continue

    #Voltage
    #be u16 voltage @ 0x4; // * 0.1
    data = int.from_bytes(ANTSerial[4:6], 'big') * 0.1
    handleString("Voltage", str(data))

    #Cell Voltages
    #be u16 cell_volt[32] @ 0x6; // * 0.001
    for cell_index in range(cellCount):
        data = int.from_bytes(ANTSerial[6 + (cell_index * 2):8 + (cell_index * 2)], 'big') * 0.001
        handleString("Cell_Voltage_" + str(cell_index), str(data))

    #Current
    #be u16 current @ 0x46; // * 0.1
    data = int.from_bytes(ANTSerial[70:72], 'big', signed=True) * 0.1
    handleString("Current", str(data))

    #SOC
    #u8 soc @ 0x4A; // percentage
    data = int.from_bytes(ANTSerial[74:76], 'big')
    handleString("SOC", str(data))

    #Capacity
    #be u32 capacity @ 0x4f; // * 0.000001
    data = int.from_bytes(ANTSerial[79:83], 'big') * 0.000001
    handleString("Capacity", str(data))

    #Cycle AH
    #be u32 cycle_ah @ 0x53; // * 0.001  // unknown
    data = int.from_bytes(ANTSerial[83:87], 'big')
    handleString("Cycle_AH", str(data))

    #Runtime
    #be u32 timer_s_32_zhi @ 0x57; // runtime
    data = int.from_bytes(ANTSerial[87:91], 'big')
    handleString("Runtime", str(data))

    #MOS Temp
    #be u16 mos @ 0x5b; // unknown
    data = int.from_bytes(ANTSerial[91:93], 'big')
    handleString("MOS_Temp", str(data))

    #Balance Temp
    #be u16 balance @ 0x5d; // unknown
    data = int.from_bytes(ANTSerial[93:95], 'big')
    handleString("Balance_Temp", str(data))

    #Temperature String
    #be u16 temperature[4] @ 0x5f;
    for temp_index in range(4):
        data = int.from_bytes(ANTSerial[95 + (temp_index * 2):97 + (temp_index * 2)], 'big')
        handleString("Temp_" + str(temp_index), str(data))

    #MOSFET Charge Status
    #u8 mosfet_charge_status @ 0x67;
    data = ANTSerial[103]
    handleString("MOSFET_Charge_Status", MOSFET_Charge_String[data])

    #MOSFET Discharge Status
    #u8 mosfet_discharge_status @ 0x68;
    data = ANTSerial[104]
    handleString("MOSFET_Discharge_Status", MOSFET_Discharge_String[data])

    #Balancing Status
    #u8 balancing_status @ 0x69;
    data = ANTSerial[105]
    handleString("Balancing_Status", Balance_String[data])

    #Power
    #be u16 Power @ 0x71;
    data = int.from_bytes(ANTSerial[113:115], 'big', signed=True)
    handleString("Power", str(data))

    #Cell max index
    #u8 cell_max_index @ 0x73; // cell_volt[index - 1]
    data = ANTSerial[115]
    handleString("Cell_Max_Index", str(data))

    #Cell max
    #be u16 cell_max @ 0x74; // * 0.001
    data = int.from_bytes(ANTSerial[116:118], 'big') * 0.001
    handleString("Cell_Max", str(data))

    #Cell min index
    #u8 cell_min_index @ 0x76; // cell_volt[index - 1]
    data = ANTSerial[118]
    handleString("Cell_Min_Index", str(data))

    #Cell min
    #be u16 cell_min @ 0x77; // * 0.001
    data = int.from_bytes(ANTSerial[119:121], 'big') * 0.001
    handleString("Cell_Min", str(data))

    #Cell average
    #be u16 cell_average @ 0x79; // * 0.001
    data = int.from_bytes(ANTSerial[121:123], 'big') * 0.001
    handleString("Cell_Average", str(data))

    #Cell count
    #u8 cell_count @ 0x7b; // possibly cell count
    data = ANTSerial[123]
    handleString("Cell_Count", str(data))
    
    #u8 unk1[4] @ 0x84; // im guessing 32 bits representing balance state
    #data = int.from_bytes(ANTSerial[132], 'big')
    #handleString("", str(data))