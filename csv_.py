import streamlit as st
import serial
from crc import append_crc, verify_packet
import time
import csv
import os
import signal
from datetime import datetime

st.set_page_config(page_title="AP4C communication", layout="wide")

# ser=None

def start():

    ####### SHUT DOWN BUTTON #########
    if st.toggle("shut down server"):
        pid = os.getpid()
        os.kill(pid, signal.SIGTERM)
    try:

        #### COM-PORT configuration #####

        def get_com_port():
            config_file = "config_file.txt"
            if os.path.exists(config_file):
                with open(config_file, "r") as file:
                    com_port = file.read().rstrip()
                    print(f"__loaded COM port: {com_port}")
                    return com_port
        my_port = get_com_port()

        ser = serial.Serial(
            port=f'{my_port}',  # port name
            baudrate=115200,  # rate of communication or sending data (bits/sec)
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1  # wait time for reading
        )

        #### MAKING A TIMESTAMP-NAMED FILE ########

        timestamp2 = datetime.now().strftime("%Y-%m-%d__%H;%M;%S.%f")[:-3]
        LOG_FILE = f"[csv] {timestamp2}.csv"
        # LOG_FILE='s_log.csv'

        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', newline='') as f:
                # writer = csv.writer(f)
                csv.writer(f).writerow(['Time Stamp'] + ['res_0'] + ['res_1'] + ['CH_con'] + ['As_con'] +
                                       ['CN_con'] + ['Ph_con'] + ['Sul_con'] + ['Alarm'] + ['Status'])

        ######### AFTER OPENING SERIAL-PORT ##########

        if ser.is_open:
            # st.write("### Server Connected")

            data_spot = st.empty()      ##### AN EMPTY CONTAINER FOR REFRESHING THE DATA
            if 'i' not in st.session_state:
                st.session_state.i = 1
            @st.fragment(run_every=2)    ##### REPEATING THE func() to receive data repeatedly

            def func():
                st.write(st.session_state.i)
                st.session_state.i += 1
                with data_spot.container():
                    # data = input("Enter hex values (space separated): ").split()
                    data=[161, 3, 00, 15, 0, 15]

                    packet=append_crc(data) #adding crc to data

                    bytes_sent=ser.write(packet)   #sending bytes packet and storing no. of bytes in bytes_sent

                    time.sleep(0.5)  # even if data not received the program will not shut for this amount of time

                    line = ser.readline(35).rstrip()
                    # byte_array = line  # decimal array of 35 inputs
                    byte = line[3:33]      ## PUTTING USABLE VALUES IN byte #####
                    line_length = len(line)
                    print(f"line: {line.hex()}")
                    print(f"byte: {byte.hex()}")

        ################### IF DATA NOT RECEIVED #################

                    if line_length==0:
                        print("NO DATA RECEIVED")
                        st.info("Port Connected, No Data Received !")
                        byte=byte*0 #for b in byte

                        var = ['res_0', 'res_1', 'CH_con', 'As_con', 'CN_con', 'Ph_con', 'Sol_con', 'Alarm', 'Status']
                        # byte_array = line  # decimal array of 35 inputs
                        # byte = byte_array[3:33]
                        # print(byte)
                        # st.write(f"{byte}")
                        # st.write(f"Device Address: {line[0]:02x}")
                        col1, col2, col3, col4 = st.columns(4, gap='large', border=True)
                        try:
                            with col1:  ########33333333333333333################
                                j = 0
                                for i in range(0, 4, 2):
                                    sum = 0

                                    vari = var[j]
                                    st.write(f"###### {vari}: "+f"{sum}")
                                    # st.write(f"{sum}")  # {sum: 04b}

                                    j += 1
                        except Exception as e:
                            st.write(f"{e}")

                        try:
                            with col2:  ########33333333333333333################
                                j = 2
                                for i in range(4, 13, 2):
                                    sum = 0
                                    vari = var[j]
                                    st.write(f"###### {vari}: "+f"{sum}")
                                    # st.write(f"{sum}")  # {sum: 04b}

                                    j += 1
                        except Exception as e:
                            st.write(f"{e}")

                        # for alarm and status
                        try:
                            with col3:
                                # Alarm
                                sum = 0 #(byte[14])
                                vari = var[7]
                                # st.write(f"##### Alarm: {sum:08b}")
                                eight_bit = f"{sum:08b}"
                                lenS = len(eight_bit)
                                k = lenS

                                Alarm = {
                                    'Alarm[1]': '###### Alarm_0',
                                    'Alarm[2]': '###### Alarm_1',
                                    'Alarm[3]': '###### Alarm_CH',
                                    'Alarm[4]': '###### Alarm_As',
                                    'Alarm[5]': '###### Alarm_CN',
                                    'Alarm[6]': '###### Alarm_G',
                                    'Alarm[7]': '###### Alarm_HD',
                                    'Alarm[8]': '',
                                }

                                for val in eight_bit:
                                    k -= 1
                                    if k != 7:
                                        if val == '1':
                                            st.write(Alarm[f"Alarm[{k + 1}]"]+": 0")
                                        elif val != '1':
                                            st.write(Alarm[f"Alarm[{k + 1}]"]+": 0")
                                # print("----")
                        except Exception as e:
                            st.write(f"{e}")

                        try:
                            with col4:
                                # Status
                                sum = 0 #(byte[15])
                                vari = var[8]
                                # st.write(f"##### Status: {sum:08b}")
                                eight_bit = f"{sum:08b}"
                                lenS = len(eight_bit)

                                Status = {
                                    'Status[1]': '###### Power_Supply_too_low',
                                    'Status[2]': '###### Purge_is_required',
                                    'Status[3]': '###### Monitor',
                                    'Status[4]': '###### Detector_ready',
                                    'Status[5]': '###### Device_fault',
                                    'Status[6]': '###### Lack_of_Hydrogen',
                                    'Status[7]': '###### Maintainence_required',
                                    'Status[8]': '###### Test_Mode',
                                }

                                k = lenS
                                for val in eight_bit:
                                    k -= 1
                                    if val == '1':
                                        st.write(Status[f"Status[{k + 1}]"]+": 0")
                                    elif val != '1':
                                        st.write(Status[f"Status[{k + 1}]"]+": 0")
                        except Exception as e:
                            st.write(f"{e}")




            ############################################## Printing Data On Screen ###################################################


                    else:
                        concen = []
                        print(f"Data is {line.hex()}")
                        var = ['res_0', 'res_1', 'CH_con', 'As_con', 'CN_con', 'Ph_con', 'Sul_con', 'Alarm', 'Status']
                        byte_array = line  # decimal array of 35 inputs

                        col1, col2, col3, col4 = st.columns(4, gap='large', border=True)
                        try:
                            with col1:  ########33333333333333333################
                                j = 0
                                for i in range(0, 4, 2):
                                    sums = (byte[i] * 256) + byte[i + 1]
                                    if sums > 32768:
                                        sums -= 65536
                                    print(f"res[{i}]: {sums}")
                                    vari = var[j]
                                    concen.append(sums)
                                    st.write(f"###### {vari} ")
                                    st.write(f"{sums}")  # {sum: 04b}
                                    j += 1
                        except Exception as e:
                            print(e)

                        try:
                            with col2:  ########33333333333333333################
                                j = 2
                                for i in range(4, 13, 2):
                                    sum = (byte[i] * 256) + byte[i + 1]
                                    if sum > 32768:
                                        sum -= 65536
                                    print(f"{vari}: {sum}")
                                    vari = var[j]
                                    if vari == 'HC_con':
                                        sum /= 500
                                    elif vari == 'As_con':
                                        sum /= 50
                                    elif vari == 'Cn_con':
                                        sum /= 25
                                    elif vari == 'Ph_con':
                                        sum /= 5
                                    elif vari == 'Sul_con':
                                        sum /= 200

                                    concen.append(sum)
                                    st.write(f"###### {vari} ")
                                    st.write(f"{sum}")  # {sum: 04b}

                                    j += 1
                                # print("----")
                        except Exception as e:
                            print(e)

                        # for alarm and status
                        try:
                            with col3:
                                # Alarm
                                sum = (byte[14])
                                concen.append(sum)
                                print(sum)
                                vari = var[7]
                                # st.write(f"##### Alarm: {sum:08b}")
                                eight_bit = f"{sum:08b}"
                                lenS = len(eight_bit)
                                k = lenS

                                Alarm = {
                                    'Alarm[1]': '###### Alarm_0',
                                    'Alarm[2]': '###### Alarm_1',
                                    'Alarm[3]': '###### Alarm_CH',
                                    'Alarm[4]': '###### Alarm_As',
                                    'Alarm[5]': '###### Alarm_CN',
                                    'Alarm[6]': '###### Alarm_G',
                                    'Alarm[7]': '###### Alarm_HD',
                                    'Alarm[8]': '',
                                }

                                for val in eight_bit:
                                    k -= 1
                                    if k != 7:
                                        if val == '1':
                                            st.write(Alarm[f"Alarm[{k + 1}]"]+": ON")
                                        elif val != '1':
                                            st.write(Alarm[f"Alarm[{k + 1}]"]+": OFF")
                                # print("----")
                        except Exception as e:
                            print(e)

                        try:
                            with col4:
                                # Status
                                sum = (byte[15])
                                print(sum)
                                concen.append(sum)
                                vari = var[8]
                                # st.write(f"##### Status: {sum:08b}")
                                eight_bit = f"{sum:08b}"
                                lenS = len(eight_bit)

                                Status = {
                                    'Status[1]': '###### Power_Supply_too_low',
                                    'Status[2]': '###### Purge_is_required',
                                    'Status[3]': '###### Monitor',
                                    'Status[4]': '###### Detector_ready',
                                    'Status[5]': '###### Device_fault',
                                    'Status[6]': '###### Lack_of_Hydrogen',
                                    'Status[7]': '###### Maintenance_required',
                                    'Status[8]': '###### Test_Mode',
                                }

                                k = lenS
                                for val in eight_bit:
                                    k -= 1
                                    if val == '1':
                                        st.write(Status[f"Status[{k + 1}]"]+": ON")
                                    elif val != '1':
                                        st.write(Status[f"Status[{k + 1}]"]+": OFF")
                        except Exception as e:
                            print(e)

                        # st.write(f"#### Data received:")
                        # st.info(f"{line}")
                        # st.write(f"length of data: {line_length}")
                        #
                        # st.write(f"#### Usable Data: ")
                        # st.info(f"{byte}")

                        # st.write(f"##### Device Address: ")
                        # st.info(f"{line[0]}")
                        # st.write(f"##### Function Code: ")
                        # st.info(f"{line[1]}")
                        # st.write(f"##### No. Of Variable: ")
                        # st.info(f"{line[2]}")

            ################################## Logging this Data to log file###############################

                    #### PUTTING DATA TO CSV FILE CREATED EARLIER #########
                        # Capture Time Stamp
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                        # Extracting data

                        try:
                            # d1 = byte[0]*256 + byte[1]
                            d1=concen[0]
                            data1 = f"{d1}" if len(byte) > 1 else "N/A"

                            # d2 = byte[2] + byte[3]
                            d2 = concen[1]
                            data2 = f"{d2}" if len(byte) > 3 else "N/A"

                            # d3 = byte[4] + byte[5]
                            d3 = concen[2]
                            data3 = f"{d3}" if len(byte) > 5 else "N/A"

                            # d4 = byte[6] + byte[7]
                            d4 = concen[3]
                            data4 = f"{d4}" if len(byte) > 7 else "N/A"

                            # d5 = byte[8] + byte[9]
                            d5 = concen[4]
                            data5 = f"{d5}" if len(byte) > 9 else "N/A"

                            # d6 = byte[10] + byte[11]
                            d6 = concen[5]
                            data6 = f"{d6}" if len(byte) > 11 else "N/A"

                            # d7 = byte[12] + byte[13]
                            d7 = concen[6]
                            data7 = f"{d7}" if len(byte) > 13 else "N/A"

                            # d8 = byte[14]
                            d8 = concen[7]
                            data8 = f"{d8:08b}" if len(byte) > 14 else "N/A"

                            # d9 = byte[15]
                            d9 = concen[8]
                            data9 = f"{d9:08b}" if len(byte) > 15 else "N/A"

                        except Exception as e:
                            print(e)

                        #### PUTTING DATA INTO A VARIABLE ######

                        try:
                            data_csv = [data1, data2, data3, data4, data5, data6, data7, f"'{data8}", f"'{data9}"]
                        except Exception as e:
                            print(e)

                        # Dump to csv

                        try:
                            with open(LOG_FILE, 'a', newline='') as f:
                                # writerr = csv.writer(f)  # ????
                                csv.writer(f).writerow([timestamp] + data_csv)
                                print(f"Data Logged: data1: {data1}, data2: {data2} at time: {timestamp}")
                        except Exception as e:
                            print(e)

            func()

        else:
            st.error("Port not connected!")

    except Exception as e:
        print(f"Erorr: {e}")
        st.write(f"Error: {e}")

start()
