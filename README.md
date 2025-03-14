# GIP2024Dynamometer
The VESC DYNO was created as part of a masters group project in 2024/25 at the University of Bristol.

The dynamometer is designed to characterise <1kW electric motors, using the VESC MKVI as motor controllers, and a decently modular setup to allow you to swap sensors.

This Repo contains test results, code etc. pertaining to our GIP creating a desktop dynamometer for <1kW electric motors. It is based on the VESC and python-can projects.

make sure to run:
pip install requirements.txt

## \CAN
### \DANCANServer
Contains the GUI and CAN control to run the motors and get results
### \TeensyTorqueSensor
Contains C code to turn a Teensy 3.6 into an ADC - CAN message device using the Waveshare CAN Board SN65HVD230.

## \Motor Characterisation
Contains the results from two tests carried out where Trampa 6340 motors were rotated externally and their back EMF recorded. The second experiment, carried out on the 17th of December 2024 is trusted over the former performed on the 13th, due to the use of a drill achieving higher speeds and therefore a greater voltage, signal to noise and error rejection etc... The first test results are stored in a folder headed OBSOLETE_Back_EMF_Data_Hand.

There is one important executable: Torque_Constant_Calculator.ipynb
This is a jypter notebook overviewing how torque constant was calculated from drill experiment data.

### \Back_EMF_Data_Drill
Contains data stored in many folders, each representing one output from the oscilloscope.