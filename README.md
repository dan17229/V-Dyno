![Logo](VDyno/GUI/styles/v-dyno-09.jpg)
# V-dyno
V-Dyno was created as part of a masters group project in 2024/25 at the University of Bristol.

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

!
## Usage example


## Development setup

To install all development dependencies and how to run an automated test-suite of some kind.

```sh
pip install requirements.txt
```
## Meta

Your Name – [LinkedIN]() – danielmuir167@gmail.com

Distributed under the MIT license. See ``LICENSE`` for more information.

[https://github.com/dan17229/GIP2024Dynamometer](https://github.com/dan17229/VDyno)

## Contributing

1. Fork it (<https://github.com/dan17229/Vdynio/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

<!-- Markdown link & img dfn's -->
[npm-image]: v
[npm-url]: https://npmjs.org/package/datadog-metrics
[npm-downloads]: https://img.shields.io/npm/dm/datadog-metrics.svg?style=flat-square
[travis-image]: https://img.shields.io/travis/dbader/node-datadog-metrics/master.svg?style=flat-square
[travis-url]: https://travis-ci.org/dbader/node-datadog-metrics
[wiki]: https://github.com/yourname/yourproject/wiki