import dearpygui.dearpygui as dpg
import loader.sensor_formatter as sensor_formatter
import loader.serial_loader as serial_loader
import calibration.cal_accelerometer as cal_accel
import threading
import time

reading = False
read_thread = None 
recordContinously = False

def _read_accelerometer_data_thread():
    global reading
    while reading:
        xyzAccel = sensor_formatter.read_sensor_data()['accelerometer']
        dpg.set_value("accel_x_value", f"{xyzAccel['x']:.2f}")
        dpg.set_value("accel_y_value", f"{xyzAccel['y']:.2f}")
        dpg.set_value("accel_z_value", f"{xyzAccel['z']:.2f}")

def cb_start_reading():
    global reading, read_thread
    if read_thread and read_thread.is_alive():
        dpg.set_value("accel_status_text", "Status: Already Reading")
        return
    if not serial_loader.get_serial_instance().is_open:
        dpg.set_value("accel_status_text", "Status: Serial Port Not Open")
        return
    if not reading:
        reading = True
        dpg.set_value("accel_status_text", "Status: Reading...")
        read_thread = threading.Thread(target=_read_accelerometer_data_thread, daemon=True)
        read_thread.start()

def cb_stop_reading():
    global reading
    reading = False
    if read_thread and read_thread.is_alive():
        read_thread.join(timeout=1)
    sensor_formatter.stop_sensor_reading()
    dpg.set_value("accel_status_text", "Status: Not Reading")

def cb_read_once_accel_data():
    accel_data = sensor_formatter.read_once_accelerometer()
    dpg.set_value("accel_x_value", f"{accel_data['x']:.2f}")
    dpg.set_value("accel_y_value", f"{accel_data['y']:.2f}")
    dpg.set_value("accel_z_value", f"{accel_data['z']:.2f}")

def cb_record_once_accel_data():
    accel_data = sensor_formatter.read_once_accelerometer()
    dpg.set_value("accel_x_value_cal", f"{accel_data['x']:.2f}")
    dpg.set_value("accel_y_value_cal", f"{accel_data['y']:.2f}")
    dpg.set_value("accel_z_value_cal", f"{accel_data['z']:.2f}")
    cal_accel.add_record(accel_data['x'], accel_data['y'], accel_data['z']) 
    count = cal_accel.count_records()
    dpg.set_value("recorded_data_count", f"Recorded Data: {count}")

    if count % 2 == 0:  # Save every 2 records
        offset, scale = cal_accel.calculate_calibration()

def cb_record_continuously_accel_data():
    global recordContinously
    count = dpg.get_value("calibration_record_count")
    recordContinously = True
    for _ in range(count):
        if not recordContinously:
            break
        dpg.set_value("record_continuously_accel_data_button", "Stop Recording" if recordContinously else "Record Continuously")
        accel_data = sensor_formatter.read_once_accelerometer()
        dpg.set_value("accel_x_value_cal", f"{accel_data['x']:.2f}")
        dpg.set_value("accel_y_value_cal", f"{accel_data['y']:.2f}")
        dpg.set_value("accel_z_value_cal", f"{accel_data['z']:.2f}")
        cal_accel.add_record(accel_data['x'], accel_data['y'], accel_data['z'])
        dpg.set_value("recorded_data_count", f"Recorded Data: {cal_accel.count_records()}")
        time.sleep(0.3)
        offset, scale = cal_accel.calculate_calibration()  
    recordContinously = False

def cb_get_min_max():
    min_max_values = cal_accel.getMinMax()
    if min_max_values:
        dpg.set_value("min_max_values_input", f"{min_max_values[0]:.2f}, {min_max_values[1]:.2f}, {min_max_values[2]:.2f}, {min_max_values[3]:.2f}, {min_max_values[4]:.2f}, {min_max_values[5]:.2f}")
    else:
        dpg.set_value("min_max_values_input", "No records available")

def cb_save_calibration():
    offset, scale = cal_accel.calculate_calibration() # Save calibration data to txt file

def cb_send_offsets():
    offsets = cal_accel.getMinMax()
    if offsets:
        sensor_formatter.send_calibration_accelerometer(offsets[0], offsets[1], offsets[2], offsets[3], offsets[4], offsets[5])
    else:
        dpg.set_value("min_max_values_input", "No records available")

def create_accelerometer_tab():
    with dpg.tab(label="Accelerometer", tag="accelerometer_tab"):
        with dpg.collapsing_header(label="Accelerometer Data Raw", default_open=True):
            with dpg.group(horizontal=True):
                dpg.add_text("Accelerometer Data:")
                dpg.add_button(label="Read Once", tag="read_once_accel_data_button", callback=cb_read_once_accel_data)
                dpg.add_button(label="Start Read", tag="read_accel_data_button", callback=cb_start_reading)
                dpg.add_button(label="Stop Read", tag="stop_read_accel_data_button", callback=cb_stop_reading)
                dpg.add_text("Status: Not Reading", tag="accel_status_text")
            with dpg.table(tag="accel_data_table", header_row=True, height=50, width=400):
                dpg.add_table_column(label="X")
                dpg.add_table_column(label="Y")
                dpg.add_table_column(label="Z")
                with dpg.table_row():
                    dpg.add_text("0.0", tag="accel_x_value")
                    dpg.add_text("0.0", tag="accel_y_value")
                    dpg.add_text("0.0", tag="accel_z_value")
        with dpg.collapsing_header(label="Calibration", default_open=True):
            with dpg.group():
                dpg.add_text("Calibration Data:")
                dpg.add_button(label="Record Once", tag="record_once_accel_data_button", callback=cb_record_once_accel_data)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Record Continuously", tag="record_continuously_accel_data_button", callback=cb_record_continuously_accel_data)
                    dpg.add_input_int(label="Number of Records", default_value=100, min_value=1, max_value=1000, tag="calibration_record_count", width=100)
            with dpg.table(tag="accel_data_table_cal", header_row=True, height=50, width=400):
                dpg.add_table_column(label="X")
                dpg.add_table_column(label="Y")
                dpg.add_table_column(label="Z")
                with dpg.table_row():
                    dpg.add_text("0.0", tag="accel_x_value_cal")
                    dpg.add_text("0.0", tag="accel_y_value_cal")
                    dpg.add_text("0.0", tag="accel_z_value_cal")
            with dpg.group(horizontal=True):
                dpg.add_text("Recorded Data: 0", tag="recorded_data_count")
                dpg.add_button(label="Get Min/Max", tag="get_min_max_button", callback=cb_get_min_max)
            with dpg.group(horizontal=True):
                dpg.add_text("Min/Max Values: ", tag="min_max_values_text")
                dpg.add_input_text(readonly=True, tag="min_max_values_input", width=400, default_value="0.0, 0.0, 0.0, 0.0, 0.0, 0.0")
            with dpg.group(horizontal=True):
                dpg.add_button(label="Send Offsets", tag="send_offsets_button", callback=cb_send_offsets)
        
