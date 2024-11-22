import pyvisa
import signal
import time
import sys
import subprocess
import re
#blac connector to  ch 1+, red connector to ch0-, ch0+ and ch1- have to be connected
UstepL=0.1 #V
UstepH=0.2 #V

U_set = [0.01, 0.9]
I_set = [1.,  1.]
sleeptime = 1.
DEV_HAMEG = "ASRL/dev/ttyUSB0::INSTR" 

temp = int(sys.argv[1])
if temp >= 60:
    print("temp is too big")
    sys.exit()


def connect_to_devices():
    print("Try to connect to HAMEG  ... ")
    rmhameg = pyvisa.ResourceManager("@py")
    print(rmhameg.list_resources())
    isconnected = False
    hameg = rmhameg.open_resource(DEV_HAMEG)
    data = hameg.query("*IDN?")
    hameg.close()   
    print(f"{data!r}")
    if (data.find("HAMEG,HMP4040") >= 0 and data.find("014944687") >= 0 ) :
        print("OK")
        isconnected = True
    if isconnected == False :
        print("Can't conect to HAMEG DIRICH")
        sys.exit(0)
        
        
def set_PS_parametrs(U,I):
    print("Set HAMEG voltage and current parameters ...")
    Uhams=["","","",""]
    Ihams=["","","",""]
    for i in range(2) :
        hameg.write(f"INST OUT{i+1}")
        hameg.write(f"VOLT {U[i]}")
        hameg.write(f"CURR {I[i]}")
        Uhams[i] = hameg.query("VOLT?")
        Ihams[i] = hameg.query("CURR?")
        Uhams[i] = re.findall(r'([0-9]*.[0-9]+)',Uhams[i])
        Ihams[i] = re.findall(r'([0-9]*.[0-9]+)',Ihams[i])
        Uhams[i] = float(Uhams[i][0])
        Ihams[i] = float(Ihams[i][0])
    for i in range(2) :
        if ( Uhams[i] != U[i] or Ihams[i] != I[i]) : 
            print("Can't set HAMEG PS parameters")
            #print(f"U3.3={Uhams[1]} I3.3={Ihams[1]} U2.5={Uhams[2]} I2.5={Ihams[2]} U1.2={Uhams[3]} I1.2={Ihams[3]}")
            sys.exit(0)
    print(f"U0={Uhams[0]} I0={Ihams[0]} U1={Uhams[1]} I1={Ihams[1]}")
        

def poweron():
    print("Switch on HAMEG .. ")
    hameg.write("OUTP:GEN ON")
    onoffham = hameg.query("OUTP:GEN?")
    if ( float(onoffham)==1 ) :
        print("OK")
    else :
        print("Can't switch on HAMEG power supply")
        poweroff()
        sys.exit(0)


def poweroff():
    print("Turn off HAMEG .. ")
    hameg.write("OUTP:GEN OFF")
    onoffham = hameg.query("OUTP:GEN?")
    if ( float(onoffham)==0 ) :
        print("OK")
        hameg.close()
    else :
        print("Can't switch off HAMEG power supply")
        sys.exit(0)    


def signal_handler(signal, frame):
    print("\nSwiching off power supplies and exit ")
    poweroff()
    hameg.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

connect_to_devices()
rmhameg = pyvisa.ResourceManager("@py")
hameg = rmhameg.open_resource(DEV_HAMEG)
set_PS_parametrs(U_set,I_set)
poweron()

rt = subprocess.check_output("/home/daq/snd_termal_test/prot2_control", shell=True)
realtemp = float(rt)
time.sleep(sleeptime)

while True:

    print("\r")
    rt = subprocess.check_output("/home/daq/snd_termal_test/prot2_control", shell=True)
    tmp = float(rt)
    print(f"Temp: {tmp}")
    if abs(temp-tmp) > 0.2 : #что-то меняем только если измеренная температура отличается от цели больше чем 0.5 градуса
        #if temp - tmp > temp - realtemp  :
        if tmp >= temp :
            if abs(temp - tmp) >  abs(temp - realtemp)  :
                U_set = [U_set[0], round(U_set[1] +UstepL,1) ]
            else :
                if abs(tmp-realtemp)<0.2 :
                    U_set = [U_set[0], round(U_set[1] +UstepL,1) ]

        else :
            if  abs(temp - tmp) >  abs(temp - realtemp)  :
                if U_set[1] -UstepL >= 0 :
                    U_set = [U_set[0], round(U_set[1]-UstepL,1)]
            
        #U_set=U
        print(U_set)
        realtemp=tmp
        set_PS_parametrs(U_set,I_set)
   
    for _ in range(15):
        print(f"Wait...{'.' * _}", end="\r")
        time.sleep(1)


