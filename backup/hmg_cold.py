import pyvisa
import signal
import time
import sys
import subprocess

U1set = 0.5
U2set = 3.8
U3set = 2.9
U4set = 1.6
I1set = 1.
I2set = 1.
I3set = 2.
I4set = 5.

temp = 10

#def rtf():
#    rt = subprocess.check_output("/home/daq/snd_termal_test/prot2_control", shell=True)
#    realtemp = float(rt)
#    print(f"Temp: {realtemp}")
    
def poweron():
    inst.write("OUTP:GEN ON")
    
def poweroff():
    inst.write("OUTP:GEN OFF")

def signal_handler(signal, frame):
    print("Swiching off power supplies and exit ")
    poweroff()


try:

    while True:
        
        print("\r")
        rt = subprocess.check_output("/home/daq/snd_termal_test/prot2_control", shell=True)
        realtemp = float(rt)
        print(f"Temp: {realtemp}")

        if realtemp >= temp + 10:
            U1set = U1set + 0.5
            print(f"U1 = {U1set}")
            
        elif realtemp <= temp - 10:
            U1set = U1set - 0.5
            print(f"U1 = {U1set}")
            
        elif temp + 10 > realtemp >= temp + 1:
            U1set = U1set + 0.25
            print(f"U1 = {U1set}")
            
        elif temp - 10 < realtemp <= temp - 1:
            U1set = U1set - 0.25
            print(f"U1 = {U1set}")

        rm = pyvisa.ResourceManager("@py")
        rm.list_resources()
        inst = rm.open_resource('ASRL/dev/ttyUSB0::INSTR')
       # print(inst.query("*IDN?"))
        print(inst)
            
        #time.sleep(5)
        print("SET PS parameters ...  ")
        #inst.write("INST:OUT1;VOLT 1.5;CURR 1.");
        inst.write("INST:OUT1");
        inst.write(f"VOLT {U1set}");
        inst.write(f"CURR {I1set}");
       # print(inst.query("CURR?"))
        time.sleep(0.2)
        poweron()

        print("READ PS parameters ...  ")
        inst.write("INST:OUT2")
        print(inst.query("MEAS:VOLT?"))
        print(inst.query("MEAS:CURR?"))
        inst.close()

        signal.signal(signal.SIGINT, signal_handler)
        
        for _ in range(15):
            print(f"Wait...{'.' * _}", end="\r")
            time.sleep(1)
except KeyboardInterrupt:
    print("Stopped")
