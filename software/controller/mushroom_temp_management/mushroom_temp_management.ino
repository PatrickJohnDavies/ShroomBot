//Check this out:
//https://learn.sparkfun.com/tutorials/ccs811bme280-qwiic-environmental-combo-breakout-hookup-guide?_ga=2.54677867.1119812231.1643177890-1066614344.1643177890

//Connect the breakout using quiic connector to quiic board, or use the 3v3 / gnd / sda / scl pins to connect to correpsonding arduino pins

#include <stdint.h>
//#include "SparkFunBME280.h"

#include "Wire.h"
#include "SPI.h"

//Global sensor object
BME280 mySensor;


//Pins to be determined - can use regular digital pins without pwm
int peliterHeaterPin = 2;
int peltierCoolerPin = 3;

//wandering between 66 and 80 f is fine. We can interfere if it gets within 1 degree
int highTemp = 79;
int lowTemp = 69;
float currentTemp;


void setup()
{
  //***Driver settings********************************//
  //commInterface can be I2C_MODE
  //specify I2C address.  Can be 0x77(default) or 0x76

  //For I2C, enable the following
  mySensor.settings.commInterface = I2C_MODE;
  mySensor.settings.I2CAddress = 0x77;

  //***Operation settings*****************************//

  //runMode can be:
  //  0, Sleep mode
  //  1 or 2, Forced mode
  //  3, Normal mode
  mySensor.settings.runMode = 3; //Forced mode

  //tStandby can be:
  //  0, 0.5ms
  //  1, 62.5ms
  //  2, 125ms
  //  3, 250ms
  //  4, 500ms
  //  5, 1000ms
  //  6, 10ms
  //  7, 20ms
  mySensor.settings.tStandby = 0;

  //filter can be off or number of FIR coefficients to use:
  //  0, filter off
  //  1, coefficients = 2
  //  2, coefficients = 4
  //  3, coefficients = 8
  //  4, coefficients = 16
  mySensor.settings.filter = 0;

  //tempOverSample can be:
  //  0, skipped
  //  1 through 5, oversampling *1, *2, *4, *8, *16 respectively
  mySensor.settings.tempOverSample = 1;

  //pressOverSample can be:
  //  0, skipped
  //  1 through 5, oversampling *1, *2, *4, *8, *16 respectively
  mySensor.settings.pressOverSample = 1;

  //humidOverSample can be:
  //  0, skipped
  //  1 through 5, oversampling *1, *2, *4, *8, *16 respectively
  mySensor.settings.humidOverSample = 1;
  delay(10);  //Make sure sensor had enough time to turn on. BME280 requires 2ms to start up.         Serial.begin(57600);

  Serial.print("Starting BME280... result of .begin(): 0x");
  //Calling .begin() causes the settings to be loaded
  Serial.println(mySensor.begin(), HEX);




  //peltier heater control pin - set output, set low
  pinMode(peliterHeaterPin, OUTPUT);
  digitalWrite(peliterHeaterPin, LOW);

  //peltier cooler control pin - set output, set low
  pinMode(peliterCoolerPin, OUTPUT);
  digitalWrite(peliterCoolerPin, LOW);


}


void loop() {
  // put your main code here, to run repeatedly:


  currentTemp = myBME280.readTempF();
  Serial.print("temperature reading is ");
  Serial.print(currentTemp);
  Serial.println(" F");


  //For controlling heating
  if (currentTemp < lowTemp)
  {  
    Serial.print("below cold range, turning on heater");
    Serial.println(" ");

    digitalWrite(peliterHeaterPin, HIGH);
  }


  if (currentTemp > lowTemp && currentTemp < highTemp)
  {  
    Serial.print("happy range, no heating or cooling");
    Serial.println(" ");

    digitalWrite(peliterHeaterPin, LOW);
    digitalWrite(peliterCoolerPin, LOW);
  }


  if (currentTemp > highTemp)
  {  
    Serial.print("above hot range, turning on cooling");
    Serial.println(" ");
    digitalWrite(peliterCoolerPin, HIGH);
  }




}
