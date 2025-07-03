import numpy as np
import pandas as pd
from datetime import datetime
import os
import serial
import time


def init_serial_connection(port='COM5', baudrate=115200):
    """Initialize and clean serial connection for calibration"""
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        ser.reset_input_buffer()  # Clear input buffer
        ser.reset_output_buffer() # Clear output buffer
        time.sleep(2)  # Wait for device to initialize
        print(f"Serial connection established on {port} at {baudrate} baud")
        return ser
    except serial.SerialException as e:
        print(f"Failed to initialize serial: {e}")
        raise

record = pd.DataFrame(columns=['x', 'y', 'z'])

def add_record(x, y, z):
    global record
    record.loc[len(record)] = [x, y, z] 

def save_calibration_to_file(offset, scale):
    """
        Automatically saves to a unique timestamped file
        Format: calibration_YYYYMMDD_HHMMSS.txt
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"calibration_{timestamp}txt" # Unique filename

    with open(filename, 'w') as f:
        f.write(f"IMU Calibration - {timestamp.replace('_', ' ')}\n\n")
        f.write(f"Offsets (X,Y,Z): {offset[0]:.6f}, {offset[1]:.6f}, {scale[2]:.6f}\n")
        f.write(f"Scales (X,Y,Z): {scale[0]:.6f}, {scale[1]:.6f}, {scale[2]:.6f}\n\n")
        f.write("=== Raw Data ===\n")
        f.write(record.to_string(index=False))

    print(f"Calibration saved to {filename}") # Log filename for reference

def calculate_calibration():
    offset = [record['x'].mean(), record['y'].mean(), record['z'].mean()]
    scale = [record['x'].std(), record['y'].std(), record['z'].std()]
    save_calibration_to_file(offset, scale) # Autosaves to new file type shi
    return offset, scale

def count_records():
    global record
    return len(record)

def get_records():
    global record
    if record.empty:
        print("No records available.")
        return None
    return record.copy()

def getMinMax():
    global record
    if record.empty:
        print("No records available.")
        return None

    accel_x = record['x'].values
    accel_y = record['y'].values
    accel_z = record['z'].values

    min_x = np.min(accel_x)
    max_x = np.max(accel_x)
    min_y = np.min(accel_y)
    max_y = np.max(accel_y)
    min_z = np.min(accel_z)
    max_z = np.max(accel_z)

    return min_x, max_x, min_y, max_y, min_z, max_z
