import serial
import json

port = 'COM3'
baudrate = 9600

def read_sensors():
    try:
        ser = serial.Serial(port, baudrate, timeout=1)

        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').rstrip()
                print(f"Received: {data}")
                data = json.loads(data)

                wire_distance = data['wire_distance']
                metadata = data['metadata']
                active = data['active']
                yield active, wire_distance, metadata

    except serial.SerialException as e:
        print(f"Error: {e}")

    finally:
        if ser.is_open:
            ser.close()