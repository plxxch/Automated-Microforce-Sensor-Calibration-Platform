
## 循环测量，无回程， 取消了测量之前加的延时 通常用这个
import os
import sys
import glob
from os import system, name 
import platform
import time
from time import sleep
import serial
import struct
import numpy as np
import crcmod
import array
import binascii
from datetime import datetime
import pandas as pd
from libreVNA import libreVNA
import logging
import math
import pyttsx3
import subprocess
import signal
import psutil


####adjustable parameters
Num_cycle_index=1
Tracking_recover_maxtime=1800
max_force_differ=0.04
global update_average
update_average=3

speed_push_zeroing=-0.015   ##0.01
speed_push_firstforce=-0.009   ### 0.0005
speed_push_normal=-0.0015
speed_pull_normal=0.0005

delay_before_measurement=2

global loading
loading=0

force_ranges = [
    # np.arange(0, 1.2, 0.2),
    # # # np.arange(0, 2.2, 0.2),
    # np.arange(0, 3.2, 0.2),
    np.arange(0, 10.5, 0.5),
    #np.arange(0, 10.2, 0.2),
    # np.arange(0, 1.1, 0.1),
    # np.arange(0, 2.1, 0.1),
    # np.arange(0, 3.1, 0.1),
    # np.arange(0, 5.1, 0.1)
]
#force_tobetest_back=np.arange(10.1,0,-0.2)

print(force_ranges)
#######adjustable parameters

data_bytes=bytearray()
datacount=0
loc_str=[]
Returnloss_average=[]
Returnloss_1=[]
Returnloss_2=[]
Returnloss_3=[]
rec_str=''
torque=0

global Returnloss
global Force_list
global Force_list_real
global displacement_list
global freq_resonance
global S11_resonance
global S11_resonance_recovery
global freq_resonance_recovery
global s11_list
global start_time_all
global start_time_scan
global start_time_list


global recheck
global Datanum_list_recovery

global data_receive
global Mea_time_recovery


freq_resonance=[]
S11_resonance=[]
freq_resonance_recovery=[]
S11_resonance_recovery=[]
Force_list=[]
Force_list_real=[]
s11_list=[]
rechecklist=[]



lengthofRL=1500

Datanum_list=[]
Datanum_list_recovery=[]
Datanum_list_real=[]

Returnloss_average=[]
S11_all_list=[]
S11_all_list_recovery=[]
Results=[]##np.zeros(5)
loc_str=[]
Forcemeter_buffer=[]
displacement_list=[]

Mea_time_gpt=0
Mea_time_recovery=0
sweeppoint=1000
Measurement_time=1
testname_input=''
testname=''

motor_running=0

English="HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
Chinese="HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ZH-CN_HUIHUI_11.0"

address_VNA = 'TCPIP0::YOUR_VNA_HOST::5025::SOCKET'

path=r'YOUR_PATH\measurement-output'

zeropoint=0
calibrated=0
dataframe_built=0
dataframe_built_recovery=0

colum_index=1


Count=0
Results=[]##np.zeros(5)
loc_str=[]
Datapoint=0
force=0
measure_completed=0
displacement=0
Num_cycle=0

Forcemeter_buffer=[]

Motor_command_base='CC 10 00 1E 00 02 04'

Force_command='20 03 00 00 00 02 C2 BA'

Force_zeroing='20 06 00 02 00 01 EF 7B'

Motor_read_base='CC 01 00 19 00 01'


Motor_command_base='CC 10 00 1E 00 02 04'

Motor_acc_base='CC 10 00 09 00 02 04'

Force_command='20 03 00 00 00 02 C2 BA'


Trigger_open_command='A0 01 00 A1'    #open 'normal open'port
Trigger_close_command='A0 01 01 A2'    # close normal open port





title='Invisalign'
Force_title=''

##电机控制
serialPort = 'YOUR_MOTOR_COM_PORT'  # 串口
baudRate = 9600  # 波特率
is_exit=False

##力传感器
serialPort_force = 'YOUR_FORCE_SENSOR_COM_PORT'  # 串口
baudRate_force = 38400

##继电器
serialport_trigger='YOUR_TRIGGER_COM_PORT'
baudRate_trigger=9600







force=0

measure_completed=0

displacement=0
displacement_list=[]





Num_cycle=0

Mea_time=0
sweeppoint=1000
Measurement_time=1

testname_input=''
testname=''



motor_running=0






################## VNA



# Store the process object globally to access it later
process = None

def start_program():
    global process

    # Get the absolute path to the program
    program_path = os.path.abspath(r'YOUR_PATH\LibreVNA-GUI.exe')


    arguments = []

    try:
        # Check if the program is already running
        if is_program_running(program_path):
            print("Program is already running. Killing the existing instance...")
            kill_program(program_path)

        # Start the program and store the process object
        process = subprocess.Popen([program_path] + arguments, cwd=os.path.dirname(program_path))
        print("Program started.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.returncode}")



def is_program_running(program_path):
    program_name = os.path.basename(program_path)
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == program_name:
            return True
    return False

def kill_program(program_path):
    program_name = os.path.basename(program_path)

    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == program_name:
            try:
                process = psutil.Process(proc.info['pid'])
                process.terminate()
                process.wait()
                print("Existing instance killed.")
            except psutil.NoSuchProcess:
                pass    


def restart_GUI_VNA():
    pyttsx3.speak("卡住了")
    print('stuked but restarting GUI')
    
    time.sleep(5)
    ##mSerial.send_data(Trigger_close_command)   ##此处可能卡住
    send_trigger_command(Trigger_close_command)
    time.sleep(5)
    kill_program(r'YOUR_PATH\LibreVNA-GUI.exe')
    time.sleep(5)
    ##mSerial.send_data(Trigger_open_command)
    send_trigger_command(Trigger_open_command)
    time.sleep(5)
    start_program()
    time.sleep(5)


    VNA_connecting()
    VNA_loadcalibration()
    VNA_presetting()
    time.sleep(1)


class SerialPort:
    def __init__(self, port, buand):
        self.port = serial.Serial(port, buand)
        self.port.close()
        if not self.port.isOpen():
            self.port.open()

    def port_open(self):
        if not self.port.isOpen():
            self.port.open()

    def port_close(self):
        self.port.close()

    def send_data(self,val):
        
        command=val


        command_tosend=bytes.fromhex(command)
                
        command_tosend.hex()

        #print('command_tosend:', command_tosend)
        self.port.write(command_tosend)


    def port_flush(self):
        self.port.flushInput()

    def read_data(self):
        global is_exit
        global datacount
        global time_minute
        global colum_index


        rec_str=''
        global data_receive
        count = self.port.inWaiting()
        ##加在这里会不work print('port count is:',count)
        if count > 0:
            #print('port count is:',count)
            ##rec_str = self.port.readline().decode('utf-8')
            rec_str = self.port.read_all()
            #rec_str = rec_str.split("\n") 

            #print('接收:',rec_str)
            ##databuffer=rec_str[3:7]
            #print(rec_str[3])
            
        
        
            rec_hex=(rec_str[3:7]).hex()
       
            #print('converted rex_hex is:',rec_hex)

            rec_hex=rec_hex[4:8]+rec_hex[0:4]


            #print('orgnised rec_hex is:',rec_hex)
   

            #print(rec_str[3:7])


            

            number=twos_complement(rec_hex, 32)
       
            #print(bin(number))
            #print('weight in g is:',number)



            force=number/1000*10
            force=round(force,3)
            print('force is:',force)    
  
            count=0
            data_receive=1
            return force
        
    def read_motor_status(self):
           
        global is_exit
        global datacount
        global time_minute
        global colum_index
        global motor_running

        rec_str=''
        global data_receive
        count = self.port.inWaiting()
        ##加在这里会不work print('port count is:',count)
        if count > 0:
            #print('port count is:',count)
            ##rec_str = self.port.readline().decode('utf-8')
            rec_str = self.port.read_all()
            #rec_str = rec_str.split("\n") 

            # print('接收:',rec_str)
            # #databuffer=rec_str[3:7]
            # print(rec_str[3])
            
            # print(int(rec_str[3]))

            motor_running=int(rec_str[3])
    def read_motor_acc(self):
        global is_exit
        global datacount
        global time_minute
        global colum_index
        global motor_running
       
       
        rec_str=''
        global data_receive
        count = self.port.inWaiting()
        ##加在这里会不work print('port count is:',count)
        if count > 0:
            #print('port count is:',count)
            ##rec_str = self.port.readline().decode('utf-8')
            rec_str = self.port.read_all()
            #rec_str = rec_str.split("\n") 

            print('接收acc data:',rec_str)
            #databuffer=rec_str[3:7]
            print(rec_str[4])
            
            print(int(rec_str[4]))
          


def calc_crc16(string):
        
		data = bytearray.fromhex(string)
		logging.info(type(data))
		crc = 0xFFFF
		for pos in data:
				crc ^= pos
				for i in range(8):
						if((crc & 1) != 0):
								crc >>= 1
								crc ^= 0xA001
						else:
								crc >>= 1

		return ((crc & 0xff) << 8) + (crc >> 8)




def package_motor(RW,val):
    global Motor_command

    value=val
    Motor_command=''

    if RW==1:

        
       
        #value_bytes=IEEE754(value)


        
        y=struct.unpack('<I',struct.pack('<f',value)) # 将浮点数按照4byte float转换
        hextotal=hex(y[0])[2:]
        
        #print(hextotal)
        #hextotal=hex(int(value_bytes,2))[2:]
        #print('value_bytes is',value_bytes)

        # hex_1=numberinhex>>24
        # hex_2=numberinhex>>16
        # hex_3=numberinhex>>8
        # hex_4=numberinhex&0xFFename_s11_all
        # hex_3 = '{:02X}'.format(hex_1)
        # hex_4 = '{:02X}'.format(crc_low)

        # hextotal= '{:02X}'.format(value_bytes)

        hex_1=hextotal[0:2]
        hex_2=hextotal[2:4]
        hex_3=hextotal[4:6]
        hex_4=hextotal[6:8]

        # print('hextotal is:',hextotal)


        # print(hex_1)
        # print(hex_2)
        # print(hex_3)
        # print(hex_4)

        Motor_command_packaged=Motor_command_base+' '+hex_3+' '+hex_4+' '+hex_1+' '+hex_2



        # print('packag wating for crc:',Motor_command_packaged)
        crc=calc_crc16(Motor_command_packaged)
        crc_high=crc>>8
        crc_low=crc&0xFF
        crc_high = '{:02X}'.format(crc_high)
        crc_low = '{:02X}'.format(crc_low)
        # print(crc_high)
        # print(crc_low)

        Motor_command_packaged=Motor_command_packaged+' '+crc_high+' '+crc_low        

        # print('The packaged Motor_command is:', Motor_command_packaged)

        Motor_command=Motor_command_packaged

        # print('Motor_command_clear?:',Motor_command)

        Motor_command_packaged=''

        # print('Motor_command_packaged_clear?:',Motor_command_packaged)



def VNA_connecting():
        # Create the control instance
    global vna
    vna = libreVNA('localhost', 19542)

    # Quick connection check (should print "LibreVNA-GUI")
    print(vna.query("*IDN?"))

    # Make sure we are connecting to a device (just to be sure, with default settings the LibreVNA-GUI auto-connects)
    vna_founded=0
    while vna_founded==0:
        vna.cmd(":DEV:CONN")
        dev = vna.query(":DEV:CONN?")
        if dev == "Not connected":
            vna_founded=0
            print("Not connected to any device, aborting")
            send_trigger_command(Trigger_close_command)
            time.sleep(2)
            send_trigger_command(Trigger_open_command)
            time.sleep(2)
            # exit(-1)
        else:
            vna_founded=1
            print("Connected to "+dev)
            break


def VNA_presetting():
    global vna
    global sweeppoint
    sweeppoint=1200
    print("Setting up the sweep...")
    vna.cmd(":DEV:MODE VNA")
    vna.cmd(":VNA:SWEEP FREQUENCY")
    vna.cmd(":VNA:STIM:LVL -10")
    vna.cmd(":VNA:ACQ:IFBW 1000")
    vna.cmd(":VNA:ACQ:AVG 1")
    vna.cmd(":VNA:ACQ:POINTS "+str(sweeppoint))
    vna.cmd(":VNA:FREQuency:START 2200000000")
    vna.cmd(":VNA:FREQuency:STOP 3200000000")



def VNA_loadcalibration():
    print('LOADING CALIBRATION FILE')
    vna.cmd(':VNA:CAL:LOAD? SOLT_1_1_00M-6_00G_4500pt.cal')


def VNA_results():
    VNA_connecting()
    VNA_presetting()
    waiting_count=0
    while vna.query(":VNA:ACQ:FIN?") == "FALSE":
        time.sleep(0.1)
        waiting_count=waiting_count+1
        if waiting_count>100:
             print('stuck when query FIN')
             restart_GUI_VNA()
             waiting_count=0
        
       

    data="FALSE" 
    waiting_count=0
    while data== "FALSE":
        data = vna.query(":VNA:TRACE:DATA? S11")  
        print('data=false') 
        time.sleep(0.2)      
        waiting_count=waiting_count+1
        if waiting_count>100:
             print('stuck when query trace data')
             restart_GUI_VNA()
             waiting_count=0     
   
    ##time.sleep(Measurement_time)

    freq=[]

    S11,freq = vna.parse_trace_data(data,freq)
    freq=np.array(freq)
    S11=np.array(S11)
    return freq, S11






def calibration_nocontact():
    
    global S11_force_initial
    global freq_zeropoint
    global S11_coil
    global S11_coil_average
    global S11_coil_list
    global update_average

    S11_coil_average=[]
    S11_coil_list=[]


##### read calibration data
    # CSV file path
    csv_file_path = r"YOUR_PATH\coil-calibration.csv"

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Extract the 1st column to freq list and 5th column to S11_coil list
    freq = df.iloc[:, 0].tolist()  # Assuming the 1st column is at index 0
    S11_coil = df.iloc[:, 2].tolist()  # Assuming the 5th column is at index 4pr


    freq=np.array(freq)
    S11_coil=np.array(S11_coil)


    S11_coil_list.append(S11_coil)

    S11_coil_average=np.average(S11_coil_list,axis=0)


#     ####### normal
#     for i in range(0,update_average):
#         print('averaging')
         
#         print("Reading trace data...")


#         VNA_presetting()

#         # wait for the sweep to finish
#         print("Waiting for the sweep to finish...")
#         waiting_count=0
#         while vna.query(":VNA:ACQ:FIN?") == "FALSE":
#             time.sleep(0.1)
#             waiting_count=waiting_count+1
#             if waiting_count>100:
#                 print('stuck when query FIN')
#                 restart_GUI_VNA()
#                 waiting_count=0
#             #print('waiting for data')

#         data="FALSE"
#         waiting_count=0
#         while data== "FALSE":
#             data = vna.query(":VNA:TRACE:DATA? S11")
#             time.sleep(0.2) 
#             waiting_count=waiting_count+1
#             if waiting_count>100:
#                 print('stuck when query trace data')
#                 restart_GUI_VNA()
#                 waiting_count=0
#         ##time.sleep(Measurement_time)

#         S11_coil=[]
#         freq=[]
#         S11_coil,freq = vna.parse_trace_data(data,freq)
#         freq=np.array(freq)
#         S11_coil=np.array(S11_coil)
#         S11_coil_list.append(S11_coil)

#     #S11_coil_list=np.array(S11_coil_list)
#         ##print(S11_coil)
#     S11_coil_average=np.average(S11_coil_list,axis=0)

  
# ############  S11 of coil
    
    
#     if update_average==1:
#         datatest={"Frequency":freq,"Returnloss_1":S11_coil_list[0],"Returnloss_average":S11_coil_average}
#     elif update_average==3:
#         datatest={"Frequency":freq,"Returnloss_1":S11_coil_list[0],"Returnloss_2":S11_coil_list[1],"Returnloss_3":S11_coil_list[2],"Returnloss_average":S11_coil_average}
  
#     ##datatest={"Power":power_Buffer,"Returnloss_1":Returnloss_1}
#     dfall_coil=pd.DataFrame(datatest)
#     filename_s11_coil=path+'\\'+title+'_'+'coil'+'.csv'
#     print('writing to path:')
#     print(filename_s11_coil)


#     operation_done=0
#     while operation_done==0:
    
#         try:
#             dfall_coil.to_csv(filename_s11_coil,index=False)
#         except Exception as e:
#             print("An error occurred:", str(e))
#             pyttsx3.speak("操作错误")
#         else:
#             operation_done=1
 

# ######################################################


def cal_sensor_on_tooth():
    global S11_force_initial
    global freq_zeropoint
    global S11_coil
    global S11_sensor_ontooth
    global S11_sensor_ontooth_list
    global S11_sensor_ontooth_average

    global Force_list
    global Force_list_real
    global displacement_list
    global freq_resonance
    global S11_resonance
    global rechecklist

    global update_average
    S11_sensor_ontooth_list=[]
    S11_sensor_ontooth_average=[]
    S11_force_initial=[]
    S11_sensor_ontooth=[]

    for i in range(0,update_average):

        waiting_count=0
        VNA_presetting()
        # wait for the sweep to finish
        print("Waiting for the sweep to finish...")
        while vna.query(":VNA:ACQ:FIN?") == "FALSE":
            time.sleep(0.1)
            waiting_count=waiting_count+1
            if waiting_count>100:
                print('stuck when query trace data')
                restart_GUI_VNA()
                waiting_count=0
            #print('waiting for data')

        data="FALSE"
        waiting_count=0
        while data== "FALSE":
            data = vna.query(":VNA:TRACE:DATA? S11")
            waiting_count=waiting_count+1
            if waiting_count>100:
                print('stuck when query trace data')
                restart_GUI_VNA()
                waiting_count=0
            ##time.sleep(Measurement_time)
        freq=[]

        S11_sensor_ontooth=[]

        S11_sensor_ontooth,freq = vna.parse_trace_data(data,freq)
        freq=np.array(freq)
        S11_sensor_ontooth=np.array(S11_sensor_ontooth)
        S11_sensor_ontooth_list.append(S11_sensor_ontooth)

    #S11_sensor_ontooth_list=np.array(S11_sensor_ontooth_list)

    S11_sensor_ontooth_average=np.average(S11_sensor_ontooth_list,axis=0)





    S11_force_initial=S11_sensor_ontooth_average-S11_coil_average    ##initial force applied by the invisalign

   
    # print(S11_force_initial)
    
    
    indexa=np.argmin(S11_force_initial)
    freq_zeropoint=(freq[indexa])

    
    Force_list.append('no contact')
    Force_list_real.append('0')
    displacement_list.append(0)
    freq_resonance.append(freq_zeropoint)
    S11_resonance.append((np.min(S11_force_initial)))
    rechecklist.append(0)

    # print('frequency zero point is:')
    # print(freq_zeropoint)

#############  S11 of calibration
    if update_average==1:
        datatest={"Frequency":freq,"Returnloss_ontooth_1":S11_sensor_ontooth_list[0],"S11_average":S11_sensor_ontooth_average[0],"S11_sensor-coil":S11_force_initial[0]}
    elif update_average==3:
        datatest={"Frequency":freq,"Returnloss_ontooth_1":S11_sensor_ontooth_list[0],"RReturnloss_ontooth_2":S11_sensor_ontooth_list[1],"Returnloss_ontooth_3":S11_sensor_ontooth_list[2],"S11_average":S11_sensor_ontooth_average[0],"S11_sensor-coil":S11_force_initial[0]}
    ##datatest={"Power":power_Buffer,"Returnloss_1":Returnloss_1}
    pd.set_option('display.float_format', lambda x: '{:.2f}'.format(x))
    dfall_coil=pd.DataFrame(datatest)
    filename_calibration=path+'\\'+title+'_'+'calibration'+'.csv'
    print('writing to path:')
    print(filename_calibration)

    operation_done=0
    while operation_done==0:
    
        try:
            dfall_coil.to_csv(filename_calibration,index=False)
        except Exception as e:
            print("An error occurred:", str(e))
            pyttsx3.speak("操作错误")
        else:
            operation_done=1

   #print(dfall)
    #check=pd.read_csv('testall.csv')



def sweepvna():


    global S11_coil
    global freq
    global s11_list
  
    global sweeppoint
    global displacement_list
    global freq_resonance
    global S11_resonance
    #pyttsx3.speak("开始读取")
    print('start')
    

    VNA_readcycle=0

    while VNA_readcycle < update_average:
    #for i in range(1,4):
        VNA_readcycle=VNA_readcycle+1
        
        print(VNA_readcycle)
        ##VNA_connecting()
        freq=[]
        RL=[]

        VNA_result_got=0
        while VNA_result_got==0:
                
            try:
                freq, RL=VNA_results()
            except Exception as e:
                print(e)
                VNA_result_got=0
                print('vna read failed')

 
                print('stuck when query freq,RL')
                restart_GUI_VNA()
               
                time.sleep(2)
            else:
                VNA_result_got=1
                #print('vna read succesed')
                time.sleep(0.5)    
                 
        
        if len(RL) != sweeppoint:
            print('RL length is wrong:',len(RL))
            VNA_readcycle=0
            s11_list.clear()
            #time.sleep(1)
            
        else:

            #time.sleep(1)
            s11_list.append(RL)






def update(val):
    

    global S11_coil
    global freq
    global s11_list
    global dataframe_built
    global sweeppoint
    global displacement_list
    global freq_resonance
    global rechecklist
    global S11_resonance
    global freqresonance_now
    global recheck
    global loading


    sweepvna()
    
    recheck_trigger=val
         
         
         
    

    Returnloss_average=[]
    
    try:
        Returnloss_average=np.average(s11_list,axis=0)
    except:
        print('average failed')
        #Returnloss_average=np.average(RL)
        print('length of Returnloss-average is:',len(Returnloss_average))
        #print(Returnloss_average)

    RL_curve=[]
    RL_curve=Returnloss_average-S11_coil


    ## print(Returnloss_average)

    ##################   calculate resonance point
    s11_min_index=np.argmin(RL_curve)

    print('resonance frequency is',freq[s11_min_index])

    freqresonance_now=freq[s11_min_index]

    recheck=0


    if recheck_trigger==1:
      
        print('freqnow is')
        print(freqresonance_now)
        print('freqold is')
        print(freq_resonance[-1])
        if (abs(freqresonance_now - freq_resonance[-1])) < 0.5:
            recheck=1
        else:
            recheck=0
    else:
         recheck=0




    k=len(force_tobetest)+1
    if recheck==1:
        print('recheck required')
        s11_list.clear()
    
    elif recheck==0:
    
        # if loading==1:
        S11_all_list.append(RL_curve)
        print('put loading result data in to')
        freq_resonance.append(freq[s11_min_index])    
        S11_resonance.append((np.min(RL_curve))) 

        # elif loading==0:  ##unloading

        #     S11_all_list.insert(k,RL_curve)

        #     print('put unloading data in to')
        #     freq_resonance.insert(k,freq[s11_min_index])    

        #     S11_resonance.insert(k,(np.min(RL_curve))) 
        
        ####bulid the frame of the pandas csv file:
        #############  S11 of each measurement : individual file
       
        ##datatest={"Frequency":freq,"Returnloss_1":s11_list[0],"Returnloss_2":s11_list[1],"Returnloss_3":s11_list[2],"Returnloss_average":Returnloss_average}
        if update_average==1:
            datatest={"Frequency":freq,"Returnloss_1":s11_list[0],"Returnloss_average":Returnloss_average}
        elif update_average==3:
            datatest={"Frequency":freq,"Returnloss_1":s11_list[0],"Returnloss_2":s11_list[1],"Returnloss_3":s11_list[2],"Returnloss_average":Returnloss_average}
        ##datatest={"Power":power_Buffer,"Returnloss_1":Returnloss_1}
        pd.set_option('display.float_format', lambda x: '{:.2f}'.format(x))
        dfall=pd.DataFrame(datatest)
        filename_averages=path+'\\'+title+'_'+Force_title+'.csv'
        print('writing to path:')
        print(filename_averages)

        operation_done=0
        while operation_done==0:

            try:
                dfall.to_csv(filename_averages,index=False)
            except Exception as e:
                print("An error occurred:", str(e))
                pyttsx3.speak("操作错误")
            else:
                operation_done=1

        #print(dfall)
        #check=pd.read_csv('testall.csv')
        s11_list.clear()


        #############  Resonance point of each measurement
        ##datatest_resonance={"Force":Datanum_list,'Force real':Datanum_list_real,"Frequency":freq_resonance,"Returnloss":S11_resonance,"displacement":displacement_list}nt
    
        datatest_resonance={"Target Force":Force_list,"Force_real":Force_list_real,"displacement":displacement_list,"Frequency":freq_resonance,"Returnloss":S11_resonance}
        print(len(Force_list))
        print(len(Force_list_real))
        print(len(displacement_list))
        print(len(freq_resonance))
        print(len(S11_resonance))
        

        
        dfall_resonance=pd.DataFrame(datatest_resonance)
        pd.set_option('display.float_format', lambda x: '{:.2f}'.format(x))
        
        filename_resonance=path+'\\'+title+'S11_resonance'+'.csv'
        print('writing to path:')
        print(filename_resonance)

        operation_done=0
        while operation_done==0:

            try:
                dfall_resonance.to_csv(filename_resonance,index=False)
            except Exception as e:
                print("An error occurred:", str(e))
                pyttsx3.speak("操作错误")
            else:
                operation_done=1




        #############  concluded original file of S11

        filename_S11_all=path+'\\'+title+'S11_all'+'.csv'

        if dataframe_built==0:
            datatest_S11_all={"Frequency":freq,"Returnloss":S11_all_list[0]}
            #print('df all is')
            #print(datatest_S11_all)
            pd.set_option('display.float_format', lambda x: '{:.2f}'.format(x))
            dfall_S11_all=pd.DataFrame(datatest_S11_all)
            filename_S11_all=path+'\\'+title+'S11_all'+'.csv'


            operation_done=0
            while operation_done==0:
            
                try:
                    print('writing the first s11_all file to path:')
                    print(filename_S11_all)
                    
                    dfall_S11_all.to_csv(filename_S11_all,index=False)
                
                except Exception as e:
                    print("An error occurred:", str(e))
                    pyttsx3.speak("操作错误")
                else:
                    operation_done=1

            dataframe_built=1
        else:
            print('second writing')
            new_data = {
                str(Mea_time_gpt): S11_all_list[0]
            }
            new_df = pd.DataFrame(new_data)
            pd.set_option('display.float_format', lambda x: '{:.2f}'.format(x))

            existing_df = pd.read_csv(filename_S11_all)

            # Concatenate the existing DataFrame with the new DataFrame along the columns
            concatenated_df = pd.concat([existing_df, new_df], axis=1)

            # Write the concatenated DataFrame to the CSV file, including the new columns
            print('writing to path:')
            print(filename_S11_all)

            operation_done=0
            while operation_done==0: 
            
                try:
                    concatenated_df.to_csv(filename_S11_all,index=False)
                except Exception as e:
                    print("An error occurred:", str(e))
                    pyttsx3.speak("操作错误")
                else:
                    operation_done=1



        S11_all_list.clear()

    return recheck
        
###################################  VNA





def update_recovery():

    global S11_coil
    global freq
    global s11_list
    global dataframe_built_recovery
    global sweeppoint
    global freq_resonance_recovery
    global S11_resonance_recovery
    global start_time_list
    global freq_point_recovery
    global Datanum_list_recovery
    #pyttsx3.speak("开始读取")
    print('start')
    

    VNA_readcycle=0

    while VNA_readcycle < 3:
    #for i in range(1,4):
        VNA_readcycle=VNA_readcycle+1
        # print('average:')
        # print(VNA_readcycle)
        ##VNA_connecting()
        freq=[]
        RL=[]

        VNA_result_got=0
        while VNA_result_got==0:
                
            try:
                freq, RL=VNA_results()
            except Exception as e:
                print(e)
                VNA_result_got=0
                print('vna read failed')
                print('stuck when query trace data in update_recovery')
                restart_GUI_VNA()
            else:
                VNA_result_got=1
                # print('vna read succesed')
                 
        
        if len(RL) != sweeppoint:
            print('RL length is wrong:',len(RL))
            VNA_readcycle=0
            s11_list.clear()
            #time.sleep(1)
            
        else:

            #time.sleep(1)
            s11_list.append(RL)
        
       
    ##print(s11_list)

    
    

    try:
        Returnloss_average=np.average(s11_list,axis=0)
    except:
        print('average failed')
        Returnloss_average=np.average(RL)
        print('length of Returnloss-average is:',len(Returnloss_average))
        print(Returnloss_average)
    
    RL_curve=[]
    RL_curve=Returnloss_average-S11_coil

    S11_all_list_recovery.append(RL_curve)




    ## print(Returnloss_average)

##################   calculate resonance point
    s11_min_index=np.argmin(RL_curve)
    
    freq_point_recovery=freq[s11_min_index]

    print('resonance frequency is',freq[s11_min_index])

    freq_resonance_recovery.append(freq[s11_min_index])    


    S11_resonance_recovery.append((np.min(RL_curve))) 

    print('minimum S11 is:', np.min(RL_curve))

   
    


    ####bulid the frame of the pandas csv file:
#############  S11 of each measurement : individual file
    ##datatest={"Frequency":freq,"Returnloss_1":s11_list[0],"Returnloss_2":s11_list[1],"Returnloss_3":s11_list[2],"Returnloss_average":Returnloss_average}
    datatest_recovery={"Frequency":freq,"Returnloss_1":s11_list[0],"Returnloss_2":s11_list[1],"Returnloss_3":s11_list[2],"Returnloss_average":Returnloss_average}
    ##datatest={"Power":power_Buffer,"Returnloss_1":Returnloss_1}
    dfall_recovery=pd.DataFrame(datatest_recovery)
    filename=path+'\\'+title+'_'+'recovery'+'_'+str(Mea_time_recovery)+'.csv'
    dfall_recovery.to_csv(filename,index=False)
   #print(dfall)
    #check=pd.read_csv('testall.csv')
    s11_list.clear()


#############  Resonance point of each measurement
    ##datatest_resonance={"Force":Datanum_list,'Force real':Datanum_list_real,"Frequency":freq_resonance,"Returnloss":S11_resonance,"displacement":displacement_list}
    datatest_resonance_recovery={"Datanum":Datanum_list_recovery,"time":start_time_list,"Frequency":freq_resonance_recovery,"Returnloss":S11_resonance_recovery}
    try:
        dfall_resonance_recovery=pd.DataFrame(datatest_resonance_recovery)
    except:
        print(Datanum_list_recovery)
        print(start_time_list)
        print(freq_resonance_recovery)
        print(S11_resonance_recovery)

    filename_resonance=path+'\\'+title+'recovery'+'_''S11_resonance'+'.csv'
    dfall_resonance_recovery.to_csv(filename_resonance,index=False)
    

#############  concluded original file of S11

    filename_S11_all_recovery=path+'\\'+title+'_'+'recovery'+'S11_all'+'.csv'

    if dataframe_built_recovery==0:
        datatest_S11_all_recovery={"Frequency":freq,"Returnloss":S11_all_list_recovery[0]}
        #print('df all is')
        #print(datatest_S11_all)
        dfall_S11_all_recovery=pd.DataFrame(datatest_S11_all_recovery)
        ##filename_S11_all_recovery=path+'\\'+title+'recovery'+'_''S11_all'+'.csv'
        dfall_S11_all_recovery.to_csv(filename_S11_all_recovery,index=False)
        dataframe_built_recovery=1
    else:
        
        new_data = {
            str(Mea_time_gpt): S11_all_list_recovery[0]
        }
        new_df = pd.DataFrame(new_data)

        existing_df = pd.read_csv(filename_S11_all_recovery)

        # Concatenate the existing DataFrame with the new DataFrame along the columns
        concatenated_df = pd.concat([existing_df, new_df], axis=1)

        # Write the concatenated DataFrame to the CSV file, including the new columns
        concatenated_df.to_csv(filename_S11_all_recovery, index=False)

    S11_all_list_recovery.clear()
        
###################################  VNA







def Tracking_recovery():
    global freq_zeropoint
    global start_time_list
    global freq_point_recovery
    global Mea_time_recovery
    global Datanum_list_recovery
    global freq_resonance_recovery
    global S11_resonance_recovery

    time_begin=time.time()  ##time at the beginning
    start_time_list=[]
    Datanum_list_recovery=[]
    freq_resonance_recovery=[]
    S11_resonance_recovery=[]
    
    Mea_time_recovery=1

    while True:
        
    
        Datanum_list_recovery.append(Mea_time_recovery)
        
        print("Datanum is:")
        print(Mea_time_recovery)

        time_startscan=time.time()-time_begin
        start_time_list.append(time_startscan)

        update_recovery()

      

        Mea_time_recovery=Mea_time_recovery+1
        

        # time_stage_1_total=6000000    ## in second

        # time_stage_1=1

        # time_stage_2_total=10000
        # time_stage_2=60

        # if Mea_time_recovery<time_stage_1_total/time_stage_1/44 :

        #     time.sleep(time_stage_1)
        #     print('stage_1')
        # else:
        #     time.sleep(time_stage_2)
        #     print('stage_2')


        if abs(freq_zeropoint-freq_point_recovery)<3:
            print('frequency recovery ready')
            break
        else:
            print('difference is:')

            print(abs(freq_zeropoint-freq_point_recovery))

        if time_startscan>Tracking_recover_maxtime:
            print('maximum time reached')
            break

        time.sleep(20)


        


def package_motor_acc(RW,val):
    global Motor_command

    value=val
    Motor_command=''

    if RW==1:

        
       
        #value_bytes=IEEE754(value)


        
        y=struct.unpack('<I',struct.pack('<f',value)) # 将浮点数按照4byte float转换
        hextotal=hex(y[0])[2:]
        
        print(hextotal)

        hex_1=hextotal[0:2]
        hex_2=hextotal[2:4]
        hex_3=hextotal[4:6]
        hex_4=hextotal[6:8]

        # print('hextotal is:',hextotal)


        # print(hex_1)
        # print(hex_2)
        # print(hex_3)
        # print(hex_4)

        Motor_command_packaged=Motor_acc_base+' '+hex_3+' '+hex_4+' '+hex_1+' '+hex_2



        # print('packag wating for crc:',Motor_command_packaged)
        crc=calc_crc16(Motor_command_packaged)
        crc_high=crc>>8
        crc_low=crc&0xFF
        crc_high = '{:02X}'.format(crc_high)
        crc_low = '{:02X}'.format(crc_low)
        # print(crc_high)
        # print(crc_low)

        Motor_command_packaged=Motor_command_packaged+' '+crc_high+' '+crc_low        

        print('The packaged Motor_command is:', Motor_command_packaged)

        Motor_command=Motor_command_packaged

        # print('Motor_command_clear?:',Motor_command)

        Motor_command_packaged=''

        # print('Motor_command_packaged_clear?:',Motor_command_packaged)



        ##address=address+1







def twos_complement(hexstr, bits):
    value = int(hexstr, 16)
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value



def Motor_move(val):
        position=val
        package_motor(1,position)

        Serial_opened=0
        while Serial_opened==0:

            try:            
                # mSerial.port_flush()
                # mSerial.port_close()
                #print('Opening serial port_motor')
                time.sleep(0.2)
                mSerial.port_open()
               
                
            except:
                 print('Serial open failed')
                 Serial_opened=0
                 time.sleep(0.2)
            else:
                #print('Serial open succesed')
                Serial_opened=1
                 
        print('writing to motor',position)
        mSerial.send_data(Motor_command)
        time.sleep(0.2)
        ##mSerial.read_data()

        mSerial.port_flush()
        mSerial.port_close()

        while write_readcommand_to_motor()==1:
            #print('motor is running')
            time.sleep(0.1)
def Motor_move_secure(val):
    forcenow=0
    forcenow=Readforce()
    if forcenow>15:
        Motor_move(0.5)
        print('Secure force exceeded')
    else:
        Motor_move(val)



def Motor_setacc(val):
        acceleration=val
        package_motor_acc(1,acceleration)
        mSerial.port_open()
        print('set acceleration',acceleration)
        mSerial.send_data(Motor_command)
        time.sleep(0.2)
        ##mSerial.read_data()

        time.sleep(1)

        print('oread the acc')

        mSerial.read_motor_acc()


        time.sleep(0.5)



        mSerial.port_flush()
        mSerial.port_close()




def Readforce():
    global data_receive
    mSerial_force.port_open()
    
    mSerial_force.send_data(Force_command)

    while data_receive==0:
        
        force=mSerial_force.read_data()   
        time.sleep(0.01)                 
    
    data_receive=0

    mSerial_force.port_flush()
    mSerial_force.port_close()
    return force


def Writeforce():
    mSerial_force.port_open()
    mSerial_force.send_data(Force_zeroing)
    
    time.sleep(0.1)

    mSerial_force.port_flush()
    mSerial_force.port_close()

def Zeroingforce():
    force_res=0
    while True:
        force_res=Readforce()    
        if force_res>0:
            Motor_move_secure(0.1)
        elif force_res<0:
            print('force already < 0')
            Writeforce()
            break
        elif force_res==0:
            print('no need to move motor')
            break


def send_trigger_command(trigger_commands):
    MAX_RETRIES = 100  # 最大尝试次数

    # 创建 SerialPort 对象

    # 打开串口
    mSerial_trigger.port_open()

    command = trigger_commands  # 指令内容
    print('command is :')
    print(command)
    retry_count = 0
    success = False

    while retry_count < MAX_RETRIES and not success:
        try:
            time.sleep(1)
            mSerial_trigger.send_data(command)
            success = True  # 如果发送成功，设置 success 为 True
        except serial.SerialException as e:
            print("SerialException occurred:", str(e))
            retry_count += 1
            print('triggering failed')
            success = False  # 如果发送成功，设置 success 为 True
            # 在重试之前执行其他错误处理或操作
            mSerial_trigger.port_close()  # 关闭串口
            time.sleep(1)
            mSerial_trigger.port_flush()  # 刷新串口
            time.sleep(1)
            mSerial_trigger.port_open()  # 重新打开串口

    # 关闭串口
    mSerial_trigger.port_close()




def createdirectory(testname_input):
    global path
    testname=testname_input
    ##testname=input('test name is:')
    
    path = os.path.join(path, testname)
    
    while os.path.exists(path):
        print("New directory already exist!")
        testname=input('please enter a new name!')
        path=os.path.join(path, testname)
            
  
    print("you can create the directory.")
    
    try:
# Create the new directory
        os.mkdir(path)
    except OSError as e:
        print(f'Failed to create the directory: {e}')
    
    
        
    
    # Create the new directory
    #check
    if os.path.exists(path):
        print("New directory created successfully!")
    else:
        print("Failed to create the directory.")
    

   


    
def write_readcommand_to_motor():

    Motor_command_packaged=Motor_read_base



    # print('packag wating for crc:',Motor_command_packaged)
    crc=calc_crc16(Motor_command_packaged)
    crc_high=crc>>8
    crc_low=crc&0xFF
    crc_high = '{:02X}'.format(crc_high)
    crc_low = '{:02X}'.format(crc_low)

    Motor_command_packaged=Motor_command_packaged+' '+crc_high+' '+crc_low        

    #print('The packaged Motor_command is:', Motor_command_packaged)

    Motor_command=Motor_command_packaged

    # print('Motor_command_clear?:',Motor_command)

    Motor_command_packaged=''

    mSerial.port_open()
    #print('Reding motor y status')
    mSerial.send_data(Motor_command)
    time.sleep(0.2)
    ##mSerial.read_data()

    # time.sleep(1)

    mSerial.read_motor_status()



    mSerial.port_flush()
    mSerial.port_close()

    return motor_running
   


# def Motor_adjust():
#     while True:
#         try:
#             a = int(input('Moving motor? (Enter 1 for Yes, 0 for No): '))
#             if a not in (0, 1):
#                 raise ValueError
#             break
#         except ValueError:
#             print('Invalid input. Please enter 0 or 1.')

#     if a == 1:
#         while True:
#             try:
#                 amount_str = input('How much to move the motor? (Enter a numeric value): ')
#                 amount = float(amount_str)
#                 break
#             except ValueError:
#                 print('Invalid input. Please enter a valid numeric value.')

#         Motor_move(amount)

#         while True:
#             try:
#                 ifadjust = int(input('Do you require adjustment? (Enter 1 for Yes, 0 for No): '))
#                 if ifadjust not in (0, 1):
#                     raise ValueError
#                 break
#             except ValueError:
#                 print('Invalid input. Please enter 0 or 1.')

#         # Rest of your code for handling adjustment
#     else:
#         print('No need to move the motor')





if __name__ == '__main__':
    

    data_receive=0

    ########### vna SEARCHING
    engine = pyttsx3.init()                                  
    engine.setProperty('voice', Chinese)

    pyttsx3.speak("开始搜寻VNA")
    
    VNA_connecting()




    mSerial = SerialPort(serialPort, baudRate)
    mSerial_force = SerialPort(serialPort_force, baudRate_force)
    mSerial_trigger = SerialPort(serialport_trigger, baudRate_trigger)


    VNA_loadcalibration()


    print('start')
    time.sleep(1)
    Zeroingforce()
    time.sleep(1)
    print('force is:')
    forcezero=Readforce()
    print(forcezero)
    
    a=int(input('moving motor?'))
    
    if a==1:
        ifadjust=1
        while ifadjust==1:
            amount=float(input('how many?'))
            Motor_move_secure(amount)

            ifadjust=int(input('orequire adjust?'))
        
    else:
        print('No need to move motor')







    time.sleep(1)
    Zeroingforce()
    time.sleep(1)
    
    
    Motor_setacc(0.1)


    testname_main=str(input('test name is?'))
    title=testname_main
    createdirectory(testname_main)
    path_main=path
    a=input('remove sensor for calibration')

    calibration_nocontact()

    a=input('put sensor on gauge')

 

    #cal_sensor_on_tooth()

    a=int(input('moving motor?'))
    if a==1:
        ifadjust=1
        while ifadjust==1:
            amount=float(input('how many?'))
            Motor_move_secure(amount)

            ifadjust=int(input('orequire adjust?'))
        
    else:
        print('No need to move motor')


###################################
###############################
        ##







    range_index=0
    for force_tobetest_index in force_ranges:
        force_tobetest=force_tobetest_index
        range_index=range_index+1
        print('mreasuring range:')
        print(force_tobetest)

        try:
            while Num_cycle<Num_cycle_index:
                Force_title='zeroing'
                ifcalibration=1
                
                # atestname=str(input('test name is?'))
                
                testname=testname_main+'_'+str(range_index)+'_'+str(force_tobetest[-1])+'N_'+str((Num_cycle+1))
                print('testnme is')
                print(testname)
                title=testname

                createdirectory(testname)
                
                
                cal_sensor_on_tooth()

                
                for i in force_tobetest:
                    measure_completed=0
                    force_target=round(i,2)
                    #pyttsx3.speak("正常") 
                    if force_target==0:
                        speed_push=speed_push_zeroing   ## before finding zero point use high speed.
                    elif force_target==force_tobetest[1]:
                        speed_push=speed_push_firstforce
                    else:
                        speed_push=speed_push_normal    ## -0.001

                    speed_pull=speed_pull_normal

                    while measure_completed==0:
                        print('cycle is')
                        print(Num_cycle)
                        
                        force=Readforce()

                        print('Finding target:',force_target)    


                        if force>force_target:
                            
                            if force-force_target> max_force_differ:     ##Measure the force again to check if the force is slide down.
                                time.sleep(0.2)
                                force=Readforce()

                                if force-force_target > max_force_differ:  ##Measure again
                                    
                                    Motor_move_secure(speed_pull)     ##if force change exceeds threshold, adjust the position
                                    print('Require adjustment')

                                    if force_target>0:
                                        displacement=displacement+speed_pull

                                    
                            else:


                                Force_title=str(force_target)+'N'
                                Force_list.append(Force_title)
                                Force_list_real.append(str(force))
                                displacement_list.append(displacement)
                                # if i==0:
                                #     #cal_sensor_on_tooth()
                                #     update(0)
                                # else:
                                time.sleep(delay_before_measurement)
                                recheck_index=1
                                recheck_time=3

                                recheck_index=update(0)

                                if recheck_index==1:
                                    while recheck_index==1:
                                        print('start to recheck')
                                        recheck_index=update(0)
                                        recheck_time=recheck_time-1

                                        if recheck_time<0 and recheck_index==1:
                                            print('omax check reach')
                                            update(0)
                                            break
                                measure_completed=1

                        else:
                            
                            Motor_move_secure(speed_push)

                            if force_target>0:
                                displacement=displacement+speed_push
                                print('Displacement:')
                                print(displacement)
                            print('Please push the motor')
                            #time.sleep(0.2)

    # ####################### 






    #             for i in force_tobetest[::-1]:
    #                 measure_completed=0
    #                 force_target=round(i,2)
                  
    #                 #pyttsx3.speak("正常") 

    #                 speed_push=speed_push_normal

    #                 speed_pull=speed_pull_normal




    #                 while measure_completed==0:
    #                     print('cycle is')
    #                     print(Num_cycle)
    #                     force=Readforce()
    #                     print("unloading")

    #                     print('Finding target:',force_target)    


    #                     if force<force_target or force==0:
                            
    #                         if abs(force-force_target) > max_force_differ:     ##Measure the force again to check if the force is slide down.
    #                             time.sleep(0.2)
    #                             force=Readforce()

    #                             if abs(force-force_target) > max_force_differ:  ##Measure again
                                    
    #                                 Motor_move_secure(speed_push)     ##if force change exceeds threshold, adjust the position
    #                                 print('Require adjustment')

    #                                 if force_target>0:
    #                                     displacement=displacement+speed_pull

                                    
    #                         else:
    #                             force=Readforce()
    #                             k=len(force_tobetest)+1
                                
    #                             Force_title=str(force_target)+'N_back'
    #                             Force_list.append(Force_title)
    #                             Force_list_real.append(str(force))
    #                             displacement_list.append(displacement)


    #                             # Force_title=str(force_target)+'N_back'
    #                             # Force_list.insert(k,Force_title)
    #                             # Force_list_real.insert(k,str(force))
    #                             # displacement_list.insert(k,displacement)


    #                             time.sleep(delay_before_measurement)
    #                             recheck_index=1
    #                             recheck_time=3

    #                             recheck_index=update(0)   ##should be 1
    #                             recheck_index=0

    #                             if recheck_index==1:
    #                                 while recheck_index==1:
    #                                     print('start to recheck')
    #                                     recheck_index=update(0)   ##should be 1
    #                                     recheck_time=recheck_time-1

    #                                     if recheck_time<0 and recheck_index==1:
    #                                         print('omax check reach')
    #                                         update(0)
    #                                         break
    #                             measure_completed=1

    #                     else:
                            
    #                         Motor_move_secure(speed_pull)

    #                         if force_target>0:
    #                             displacement=displacement+speed_push
    #                             print('Displacement:')
    #                             print(displacement)
    #                         print('Please push the motor')
    #                         #time.sleep(0.2)
    #             motorback=0.6 ###float((-1*displacement)+0.4)
    #             print('motor move back is:')
    #             print(motorback)
    #             Motor_move_secure(motorback)
    #             print('omotor move back')
    #             print(displacement)

    #             if force_target==0:
    #                 print('omeasuring no  contact')
    #                 Force_title='N0 contact_back'
    #                 # Force_list.insert(k,Force_title)
    #                 # force=Readforce()
    #                 # Force_list_real.insert(k,(str(force)))
    #                 # displacement_list.insert(k,displacement)

    #                 Force_list.append(Force_title)
    #                 force=Readforce()
    #                 Force_list_real.append((str(force)))
    #                 displacement_list.append(displacement)


    #                 update(0)

                ##一次循环完成

                motorback=1 ###float((-1*displacement)+0.4)
                print('motor move back is:')
                print(motorback)
                Motor_move_secure(motorback)
                print('omotor move back')
                print(displacement)
                Num_cycle=Num_cycle+1
                time.sleep(1)


                print('The cycle ended')
                pyttsx3.speak("end") 
                time.sleep(2)                
                Zeroingforce()
                time.sleep(2)  

                Tracking_recovery()
                


                S11_resonance.clear()
                displacement_list.clear()
                displacement=0
                freq_resonance.clear()
                Force_list.clear()
                Force_list_real.clear()
                dataframe_built=0
                path=path_main

                dataframe_built_recovery=0
                start_time_list.clear()
                S11_resonance_recovery.clear()
                freq_resonance_recovery.clear()  
                Datanum_list_recovery.clear()
                S11_all_list_recovery.clear()
                Returnloss_average.clear()     
                
            

            ###多次循环完成
            S11_all_list.clear()
            dataframe_built_recovery=0
            start_time_list.clear()
            S11_resonance_recovery.clear()
            freq_resonance_recovery.clear()
            Datanum_list_recovery.clear()
            S11_all_list_recovery.clear()
            Returnloss_average.clear()

            



                
        ##所有range完成
        except KeyboardInterrupt as e:
            print('program trying to ended')     
            a=int(input('Moving motor?'))
            if a==1:
                b=float(input('dsplacement?'))
                Motor_move_secure(b)
            else:
                print('program ended sucessfully')


        else:
            print('program ended normally')
            Num_cycle=0
            # wait before conducting next range
            time.sleep(4)






    print('program trying to ended')     
    a=int(input('Moving motor?'))
    if a==1:
        b=float(input('dsplacement?'))
        Motor_move_secure(b)
    else:
        print('program ended sucessfully')    


    while True:
        print(' all ended')
        pyttsx3.speak("全部结束")
        time.sleep(4)