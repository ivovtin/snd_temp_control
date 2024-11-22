import pyvisa
import signal
import time
import sys
import subprocess

U1set = 1.75
U2set = 3.8
U3set = 2.9
U4set = 1.6
I1set = 1.
I2set = 1.
I3set = 2.
I4set = 5.

temp = 40

try:
	
	while True:

		realtemp = subprocess.check_output("/home/daq/snd_termal_test/prot2_control", shell=True)
		realtemp = float(realtemp)

		print(f"Temp: {realtemp}")		
		
		def poweron():
			inst.write("OUTP:GEN ON")

		def poweroff():
    		    	inst.write("OUTP:GEN OFF")
		
		rm = pyvisa.ResourceManager("@py")
		rm.list_resources()
		inst = rm.open_resource('ASRL/dev/ttyUSB0::INSTR')
		print(inst.query("*IDN?"))
		print(inst)
	
		#time.sleep(5)
		print("SET PS parameters ...  ")
		#inst.write("INST:OUT1;VOLT 1.5;CURR 1.");
		inst.write("INST:OUT1");
		inst.write("VOLT 1.5");
		inst.write("CURR 1.");
		print(inst.query("CURR?"))    #1.0000
		time.sleep(0.2)
		poweron()

		print("READ PS parameters ...  ")
		inst.write("INST:OUT2")
		print(inst.query("MEAS:VOLT?")) #1.500
		print(inst.query("MEAS:CURR?"))   #0.0000
		#print(inst.query("MEAS:VOLT?;MEAS:CURR?"))
		inst.close()
		def signal_handler(signal, frame):
			print("Swiching off power supplies and exit ")
			poweroff()
			sys.exit(0)

		signal.signal(signal.SIGINT, signal_handler)
		def run():
    		#	while True:
        	#		time.sleep(1)
        	#		print("a")
			run()

		for _ in range(5):
			print(f"Wait...{'.' * _}", end="\r")
			time.sleep(1)
except KeyboardInterrupt:
	print("Stopped")
