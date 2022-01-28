from __future__ import print_function
import qwiic_ccs811
import time
import sys

def runExample():

	print("\nSparkFun CCS811 Sensor Basic Example \n")
	mySensor = qwiic_ccs811.QwiicCcs811()

	if mySensor.isConnected() == False:
		print("The Qwiic CCS811 device isn't connected to the system. Please check your connection", \
			file=sys.stderr)
		return

	mySensor.begin()

	while True:

		mySensor.readAlgorithmResults()

		print("CO2:\t%.3f" % mySensor.getCO2())

		print("tVOC:\t%.3f\n" % mySensor.getTVOC())	
    
    mySensor.read_ntc()
    print("Measured Resistance: %.3f ohms" % mySensor.resistance)

    readTemperature = mySensor.temperature
    print("Converted Temperature: %.2f deg C" % readTemperature)

    mySensor.set_environmental_data( 50, readTemperature)

		
		time.sleep(1)


if __name__ == '__main__':
	try:
		runExample()
	except (KeyboardInterrupt, SystemExit) as exErr:
		print("\nEnding Basic Example")
		sys.exit(0)
