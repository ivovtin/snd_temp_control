import pyvisa
import time
import sys
import os
import copy
import socket
import re
from datetime import datetime

#SND TTI PS (ttisnd)
#ssh -NfL:9222:10.0.0.132:9221 beam-online

HOST_TTI = "localhost"  # The server's hostname or IP address
PORT_TTI = 9222  # The port used by the server

file = open("log.txt", "a")
datafile = open("data.txt", "a")

setTemp = int(sys.argv[1])
polar = sys.argv[2]
file.write(f"\n\n********START********\nsetTemp = {setTemp}, polar = {polar}\n\n")
file.flush()

U1set = 2.0 #45C 
I1set = 1.0

#U1set = 0.1 #25C and 15C
#I1set = 0.5

U2set = 5.2
I2set = 0.5

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

def send_command_socket(dev,msg):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if (dev == "TTI") :
        s.connect((HOST_TTI, PORT_TTI))
    else :
        print("Wrong device")
        sys.exit(0)
    #msg = msg.encode()
    s.sendall(msg.encode())
    if msg.endswith('?'):
        data = s.recv(100)
        #print(f"Received {data.decode()!r}")
    else:
        data = ''.encode()
    s.close()
    return data.decode()


def ttiopen():
    
    print("Try to connect to tti SND ... ")
    data=send_command_socket("TTI","*IDN?")
    print(f"Received {data!r}")
    if (data.find("CPX400DP") >= 0 and data.find("367097") >= 0) : print("OK")
    else :
        print("Can't conect to tti SND .")
        sys.exit(0)
    time.sleep(0.1)

def set_PS_parametrs(U1, I1, U2, I2):
    print("Set tti voltage and current parameters ...")
    msg = f'V1 {U1:.2f};V2 {U2:.2f};I1 {I1:.2f};I2 {I2:.2f}'
    #print(msg)
    data=send_command_socket("TTI",msg)
    #time.sleep(0.5)
    #print("Read set U and I ")
    data=send_command_socket("TTI","V1?;I1?;V2?;I2?")
    #print(f"V1set, I1set, V2set, I2set = {data!r}") # 'V1 5.60\r\nI1 0.50\r\nV2 49.00\r\nI2 1.50\r\n'
    U1snd = re.findall(r'V1 ([0-9]*.[0-9]+)',data)
    U1snd = float(U1snd[0])
    U2snd = re.findall(r'V2 ([0-9]*.[0-9]+)',data)
    U2snd = float(U2snd[0])
    I1snd = re.findall(r'I1 ([0-9]*.[0-9]+)',data)
    I1snd = float(I1snd[0])
    I2snd = re.findall(r'I2 ([0-9]*.[0-9]+)',data)
    I2snd = float(I2snd[0])
    if ( abs(U1snd- U1)>0.1  or abs(U2snd-U2)>0.1  or abs(I1snd - I1)>0.1 or abs(I2snd-I2)>0.1) :
        print("Can't set tti  PS parameters")
        print(f"Try to set: V = {U1}V (I={I1}A)")
        print(f"Read back: V = {U1snd}V (I={I1snd}A)")
        sys.exit(0)
    else :
        print(f"U1={U1snd} I1={I1snd} U2={U2snd} I2={I2snd}")
    time.sleep(0.1)

def read_PS_parametrs():
    #print("Read measured tti SND voltage and current ...")
    data=send_command_socket("TTI","V1O?;I1O?;V2O?;I2O?")
    #print(f"V1, I1, V2, I2 = {data!r}") # '5.598V\r\n0.003A\r\n48.992V\r\n-0.015A\r\n'
    (U1,U2) = re.findall(r'([0-9]*.[0-9]+)V',data)
    (I1,I2) = re.findall(r'([0-9]*.[0-9]+)A',data)
    return (float(U1),float(I1),float(U2),float(I2))

def poweron():
    print("Switch on tti SND .. ")
    data=send_command_socket("TTI","OPALL 1")
    time.sleep(0.2)
    data=send_command_socket("TTI","OP1?;OP2?")
    #print(f"Channel 1 and 2 is  {data!r}") #    '1\r\n1\r\n'
    (ch1ttisnd,ch2ttisnd) = re.findall(r'([0-9])',data)
    if ( float(ch1ttisnd)==1 and  float(ch2ttisnd) == 1) :
        print("OK")
    else :
        print("Can't switch on tti TRB power supply")
        poweroff()
        sys.exit(0)
    

def poweroff():

    print("Turn off tti SND ... ")
    data=send_command_socket("TTI","OP1 0")
    time.sleep(0.2)
    data=send_command_socket("TTI","OP1?")
    #print(f"Channel 1 and 2 is  {data!r}") #    '1\r\n1\r\n'
    (ch1ttisnd) = re.findall(r'([0-9])',data)
    if ( float(ch1ttisnd)==0 ) :
        print("OK")
    else :
        print("Can't switch off tti SND power supply")
        sys.exit(0)

    sys.exit()








def setU(U1set, realTemp, setTemp, polar):
    if realTemp >= setTemp + 10:
        U1set = U1set - 0.25 if polar == "+" else U1set + 0.25
    elif realTemp <= setTemp - 10:
        U1set = U1set + 0.25 if polar == "+" else U1set - 0.25
    elif setTemp + 10 > realTemp >= setTemp + 1:
        U1set = U1set - 0.1 if polar == "+" else U1set + 0.1
    elif setTemp - 10 < realTemp <= setTemp - 1:
        U1set = U1set + 0.1 if polar == "+" else U1set - 0.1
    
    if U1set < 0 : U1set = 0.
    return U1set 

def wait_func(waitTime):
    for _ in range(waitTime):
        print(f"Wait...{'.' * _}", end="\r")
        time.sleep(1)

def checkTemp():
    usbtmc = os.open("/dev/usbtmc0", os.O_RDWR)
    os.write(usbtmc, "MEAS:RES?\r\n".encode())
    resp = os.read(usbtmc, 1000).decode()
    #temp = (float(resp)/10000. -1)/0.003850 #20240624
    temp = (float(resp)/1000. -1)/0.003850
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
        
        ttiopen()

        set_PS_parametrs(U1set, I1set, U2set, I2set)
        
        (U1mon, I1mon, U2mon, I2mon) = read_PS_parametrs()


        print("Imon = ", I1mon)
        print("Umon = ", U1mon)
        print("Uset = ", U1set)
        time.sleep(0.2)

        poweron()

        file.write(f"\n{time.ctime()}\nU1 = {U1set}\nTemp = {realTemp}\nCURR = {I1mon}\n\n")
        file.flush()
        datafile.write(f"{int(time.time())} {I1mon} {U1mon} {realTemp}\n")

        if U1set >= 8.0:
            break

        wait_func(45)

except KeyboardInterrupt:
    file.write(f"{time.ctime()}\nKeyboardInterrupt\n")
    file.flush()

finally:
    poweroff()
