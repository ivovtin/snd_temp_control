import pyvisa
import signal
import time
import sys
import subprocess

U1set = 0.5
I1set = 1.

temp = int(sys.argv[1])

if temp >= 60:
    print("temp is too big")
    sys.exit()

polar = sys.argv[2]

if polar == "-":
    print("switch polar") 

def poweron():
    inst.write("OUTP:GEN ON")

def poweroff():
    inst.write("OUTP:GEN OFF")

def signal_handler(signal, frame):
    inst.write(f"VOLT {0}")
    inst.write(f"CURR {0}")
    print("Swiching off power supplies and exit ")
    poweroff()
    sys.exit()
    
try:
    while True:

        print("\r")
        rt = subprocess.check_output("/home/daq/snd_termal_test/prot2_control", shell=True)
        realtemp = float(rt)
        print(f"Temp: {realtemp}")

        if realtemp >= temp + 10:
            if polar == "+":
                U1set = U1set - 0.5
            else:
                U1set = U1set + 0.5

        elif realtemp <= temp - 10:
            if polar == "+":
                U1set = U1set + 0.5
            else:
                U1set = U1set - 0.5

        elif temp + 10 > realtemp >= temp + 1:
            if polar == "+":
                U1set = U1set - 0.25
            else:
                U1set = U1set + 0.25

        elif temp - 10 < realtemp <= temp - 1:
            if polar == "+":
                U1set = U1set + 0.25
            else:
                U1set = U1set - 0.25

        rm = pyvisa.ResourceManager("@py")
        rm.list_resources()
        inst = rm.open_resource('ASRL/dev/ttyUSB0::INSTR')
        # inst = rm.open_resource('ASRL/dev/ttyUSB1::INSTR')
        inst.write("INST:OUT1")
        inst.write(f"VOLT {U1set}")
        inst.write(f"CURR {I1set}")
        print("Imon = ", inst.query("MEAS:CURR?"), end="")
        print("Umon = ", inst.query("MEAS:VOLT?"), end="")
        print("Uset = ", U1set)
        time.sleep(0.2)
        
        poweron()

        signal.signal(signal.SIGINT, signal_handler)
        
        for _ in range(15):
            print(f"Wait...{'.' * _}", end="\r")
            time.sleep(1)

except KeyboardInterrupt:
    inst.write(f"VOLT {0}")
    inst.write(f"CURR {0}")
    poweroff()
    print("Stopped")
    sys.exit()



except Exception:
    if U1set >= 8.0:
       print("U1 is too big")
       poweroff()
       sys.exit()

    if I1set >= 2.5:
       print("I1 is too big")
       poweroff()
       sys.exit()
            
    if realtemp >= 60:
       print("temp is too big")
       poweroff()
       sys.exit()
