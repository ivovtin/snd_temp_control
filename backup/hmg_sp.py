import pyvisa
import time
import sys
import os
# import copy

file = open("log.txt", "a")
datafile = open("data.txt", "a")

U1set = 0.5
I1set = 1.

setTemp = int(sys.argv[1])
polar = sys.argv[2]
file.write(f"\n\n********START********\nsetTemp = {setTemp}, polar = {polar}\n\n")
file.flush()

if setTemp >= 50:
    print("temp is too big")
    file.write(f"setTemp is too big\n")
    file.flush()
    sys.exit()

if polar != "-" and polar != "+":
    print("polar is not set correctly")
    file.write(f"polar is not set correctly\n")
    file.flush()
    sys.exit()

if polar == "-":
    print("switch polar")

def poweron():
    inst.write("OUTP:GEN ON")
    
def hamegopen():
    Numport = 0
    rm = None
    inst = None
    while True:   
        try:
            rm = pyvisa.ResourceManager("@py")
            rm.list_resources()
            inst = rm.open_resource(f'ASRL/dev/ttyUSB{Numport}::INSTR')
            data = inst.query("*IDN?")
            if (data.find("HAMEG,HMP4040") >= 0 and data.find("014944687") >= 0 ): 
                break  
        except:
            if Numport == 1:
                Numport = -1
            
        Numport += 1
    return inst

def poweroff():
    inst = hamegopen()
    print("\nSwiching off power supplies and exit ")
    inst.write(f"VOLT {0}")
    inst.write(f"CURR {0}")
    inst.write("OUTP:GEN OFF")
    file.write("\n********POWEROFF********\n")
    file.flush()
    file.close()
    datafile.close()
    sys.exit()

def setU(U1set, realTemp, setTemp, polar):
    if realTemp >= setTemp + 10:
        U1set = U1set - 0.5 if polar == "+" else U1set + 0.5
    elif realTemp <= setTemp - 10:
        U1set = U1set + 0.5 if polar == "+" else U1set - 0.5
    elif setTemp + 10 > realTemp >= setTemp + 1:
        U1set = U1set - 0.25 if polar == "+" else U1set + 0.25
    elif setTemp - 10 < realTemp <= setTemp - 1:
        U1set = U1set + 0.25 if polar == "+" else U1set - 0.25
    return U1set 

def wait_func(waitTime):
    for _ in range(waitTime):
        print(f"Wait...{'.' * _}", end="\r")
        time.sleep(1)

def checkTemp():
    usbtmc = os.open("/dev/usbtmc0", os.O_RDWR)
    os.write(usbtmc, "MEAS:RES?\r\n".encode())
    resp = os.read(usbtmc, 1000).decode()
    temp = (float(resp)/10000. -1)/0.003850
    print(f"Temp = {round(temp, 2)}")
    os.close(usbtmc)
    return round(temp, 2)

try:

    while True:
        print("\r")
        realTemp = checkTemp()

        if realTemp >= 50:
            print("temp is too big")
            file.write(f"{time.ctime()}\ntemp is too big = {realTemp}\n")
            file.flush()
            break

        U1set = setU(U1set, realTemp, setTemp, polar)
        
        inst = hamegopen()
        # inst2 = copy.copy(inst)
        
        inst.write("INST:OUT1")
        inst.write(f"VOLT {U1set}")
        inst.write(f"CURR {I1set}")
        
        print("Imon = ", inst.query("MEAS:CURR?"), end="")
        print("Umon = ", inst.query("MEAS:VOLT?"), end="")
        print("Uset = ", U1set)
        time.sleep(0.2)

        poweron()

        file.write(f"\n{time.ctime()}\nU1 = {U1set}\nTemp = {realTemp}\nCURR = {inst.query('MEAS:CURR?')}\n\n")
        file.flush()
        datafile.write(f"{int(time.time())} {float(inst.query('MEAS:CURR?'))} {float(inst.query('MEAS:VOLT?'))} {realTemp}\n")

        if U1set >= 8.0:
            break

        wait_func(15)

except KeyboardInterrupt:
    file.write(f"{time.ctime()}\nKeyboardInterrupt\n")
    file.flush()

finally:
    poweroff()