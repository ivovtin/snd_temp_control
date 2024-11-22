import pyvisa
import time
import sys
import os
import copy

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

def poweron():
    inst.write("OPALL 1")

    
def hamegopen():
    Numport = 0
    rm = None
    inst = None
    #while True:   
    try:
        rm = pyvisa.ResourceManager("@py")
        rm.list_resources()
        inst = rm.open_resource(f'ASRL/dev/ttyACM0::INSTR')
        data = inst.query("*IDN?")
            #if (data.find("HAMEG,HMP4040") >= 0 and data.find("014944687") >= 0 ): 
            #    break  
    except:
        pass
    return inst





def poweroff():
    inst = hamegopen()
    print("\nSwiching off power supplies and exit ")
#    inst.write(f"VOLT {0}")
#    inst.write(f"CURR {0}")
    inst.write("OPALL 0")
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

        inst.write("V1 {U1set};V2 {U1set};I1 {I1set};I2 {I1set}")


        #print("Imon = ", inst.query("MEAS:CURR?"), end="")
        #print("Umon = ", inst.query("MEAS:VOLT?"), end="")
        #print("Uset = ", U1set)
        #time.sleep(0.2)


        data=inst.query("V1?;I1?;V2?;I2?")
    	#print(f"V1set, I1set, V2set, I2set = {data!r}") # 'V1 5.60\r\nI1 0.50\r\nV2 49.00\r\nI2 1.50\r\n'
        Umon = re.findall(r'V1 ([0-9]*.[0-9]+)',data)
        Umon = float(Umon[0])
        Imon = re.findall(r'I1 ([0-9]*.[0-9]+)',data)
        Imon = float(Imon[0])

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
