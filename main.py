import streamlit as st
import serial
from crc import append_crc, verify_packet
import time
import csv
import os
from datetime import datetime

#Configuration

ser = serial.Serial(
    port ='COM7',         #port name
    baudrate = 115200,      #rate of communication or sending data (bits/sec)
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout = 1           #wait time for reading
)

timestamp2 = datetime.now().strftime("%Y-%m-%d__%H;%M;%S.%f")[:-3]
LOG_FILE = f"[csv] {timestamp2}.csv"
# LOG_FILE='s_log.csv'

if not os.path.exists(LOG_FILE):
    with open (LOG_FILE, 'w', newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['Time Stamp'] + ['res_0[HEX]'] + ['res_1[HEX]'] + ['CH_con[HEX]'] + ['As_con [HEX]'] + ['CN_con[HEX]'] + ['Ph_con[HEX]'] + ['Sol_con[HEX]'] + ['Alarm'] + [' Status'])

try:
    st.set_page_config(page_title="AP4C communication", layout="wide")
    # st.write("### Server Connected")
    # st.text("Send Request to check data")
    if ser.is_open:
        st.write("### Server Connected")
        data_spot = st.empty()
        if 'i' not in st.session_state:
            st.session_state.i = 1
        @st.fragment(run_every=5)
        def func():
            st.write(st.session_state.i)
            st.session_state.i += 1
            with data_spot.container():
                # data = input("Enter hex values (space seperated): ").split()
                data=[161, 3, 00, 15, 0, 15]

                packet=append_crc(data) #adding crc to data

                bytes_sent=ser.write(packet)   #sending bytes packet and storing no. of bytes in bytes_sent
                # print(f"Sent: {packet}")
                # print(packet)
                # print(f"sent: {packet.hex(' ')}")
                # print(f"Total bytes written: {data}")

                time.sleep(0.5)  # even if data not received the program will not shut for this amount of time

                line = ser.readline(35).rstrip()   #receiving data
                line_length = len(line)

                byte_array = line  # decimal array of 35 inputs
                byte = byte_array[3:33]
                # st.write(f"#### Data received:")
                # st.info(f"{line}")
                # st.write(f"length of data: {line_length}")
                
                device_add=line[0]
                st.write(f"##### Device Address: {line[0]} [{device_add:02x}]")

                if line_length==0:
                    st.info("Port Connected, No Data Received !")


        ###############################################Printing Data On Screen####################################################
                else:

                    var = ['res_0', 'res_1', 'CH_con', 'As_con', 'CN_con', 'Ph_con', 'Sol_con', 'Alarm', 'Status']
                    # byte_array = line  # decimal array of 35 inputs
                    # byte = byte_array[3:33]
                    print(byte)
                    # st.write(f"{byte}")
                    col1, col2, col3, col4 = st.columns(4, gap='large', border=True)
                    with col1:  ########33333333333333333################
                        j = 0
                        for i in range(0, 4, 2):
                            sum = (byte[i] * 256) + byte[i + 1]
                            # print(sum)
                            # print(f"{sum:016b}")
                            vari = var[j]

                            # print(f"{vari}: {sum}")
                            st.write(f"##### {vari} ")

                            st.info(f"{sum}")  # {sum: 04b}
                            j += 1

                    with col2:  ########33333333333333333################
                        j = 2
                        for i in range(4, 13, 2):
                            sum = (byte[i] * 256) + byte[i + 1]
                            # print(sum)
                            # print(f"{sum:016b}")
                            vari = var[j]

                            # print(f"{var[j]}: {sum}")
                            st.write(f"##### {vari} ")

                            st.info(f"{sum}")  # {sum: 04b}

                            j += 1

                            # print("----")

                    # for alarm and status
                    with col3:
                        # Alarm
                        sum = (byte[14])
                        vari = var[7]
                        # print(f"Alarm: {sum}")
                        # print(f"{sum:04b}")
                        st.write(f"##### Alarm: {sum:04b}")
                        sixteen_bit = f"{sum:04b}"
                        lenS = len(sixteen_bit)
                        k = lenS
                        for val in sixteen_bit:
                            k -= 1
                            if val == '1':
                                # print(f'Alarm[{k}]: on')
                                # st.write(f'Alarm[{k+1}]: on')
                                st.success(f"Alarm[{k + 1}]: ON")
                            elif val != '1':
                                st.error(f"Alarm[{k + 1}]: OFF")
                        # print("----")
                    with col4:
                        # Status
                        sum = (byte[15])
                        vari = var[8]
                        # print(f"Status: {sum}")
                        # print(f"{sum:04b}")
                        st.write(f"##### Status: {sum:04b}")
                        sixteen_bit = f"{sum:04b}"
                        lenS = len(sixteen_bit)
                        k = lenS
                        for val in sixteen_bit:
                            k -= 1
                            if val == '1':
                                # print(f'Status[{k}]: on')
                                # st.write(f'Status[{k+1}]: on')
                                st.success(f"Status[{k + 1}]: ON")
                            elif val != '1':
                                st.error(f"Status[{k + 1}]: OFF")

                    st.write(f"#### Data received:")
                    st.info(f"{line}")
                    st.write(f"length of data: {line_length}")

                    st.write(f"#### Usable Data: ")
                    st.info(f"{byte}")

                    st.write(f"##### Device Address: ")
                    st.info(f"{line[0]}")
                    st.write(f"##### Function Code: ")
                    st.info(f"{line[1]}")
                    st.write(f"##### No. Of Variable: ")
                    st.info(f"{line[2]}")

        ################################## Logging this Data to log file###############################
                    if not line:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}]Port Connected, but no data received.")
                    else:
                        # 1 Capture Time Stamp
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        # print("done1-date and time values assigned")
                        # 2 Extract specific data (Adjust indices based on your device's protocol)
                        # Example: data1 is byte index 3, data2 is byte index 4,
                        d1 = line[3] + line[4]
                        data1 = f"{d1:02x}" if len(line) > 4 else "N/A"
                        # print("done2-data1 value assigned")
                        d2 = line[5] + line[6]
                        data2 = f"{d2:02x}" if len(line) > 5 else "N/A"
                        # print("done3-data2 value assigned")
                        d3 = line[7] + line[8]
                        data3 = f"{d3:02x}" if len(line) > 8 else "N/A"
                        # print("done3-data3 value assigned")
                        d4 = line[9] + line[10]
                        data4 = f"{d4:02x}" if len(line) > 10 else "N/A"
                        # print("done3-data4 value assigned")
                        d5 = line[11] + line[12]
                        data5 = f"{d5:02x}" if len(line) > 12 else "N/A"
                        # print("done3-data5 value assigned")
                        d6 = line[13] + line[14]
                        data6 = f"{d6:02x}" if len(line) > 14 else "N/A"
                        # print("done3-data6 value assigned")
                        d7 = line[15] + line[16]
                        data7 = f"{d7:02x}" if len(line) > 16 else "N/A"
                        # print("done3-data7 value assigned")
                        d8 = line[17]
                        data8 = f"{d8:04b}" if len(line) > 17 else "N/A"
                        # print("done3-data8 value assigned")
                        d9 = line[18]
                        data9 = f"{d9:04b}" if len(line) > 18 else "N/A"
                        # print("done3-data9 value assigned")

                        # print("done4--converting 'line' to bytes then hex...")
                        full_payload = bytes(line).hex(' ')  #### converting 'line' to bytes then hex
                        # print("done4-converted")

                        data_csv = [data1, data2, data3, data4, data5, data6, data7, data8, data9]
                        # 3 Dump to csv
                        # print("logging data to csv...")
                        with open(LOG_FILE, 'a', newline='') as f:
                            writerr = csv.writer(f)  # ????
                            writerr.writerow([timestamp] + data_csv)
                            print(f"Data Logged: data1: {data1}, data2: {data2} at time: {timestamp}")

                # if ser.in_waiting > 0:
                #     line = ser.readline().decode('utf-8').rstrip()
                #     print("Received : " + line)
                # elif status=='/exit':
                #
                #     break

        func()
except Exception as e:
    print(f"Erorr: {e}")
