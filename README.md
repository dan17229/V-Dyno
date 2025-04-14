# <img src="VDyno/images/main_logo.png" alt="logo" width="200"/>

V-Dyno was created as part of a masters group project in 2024/25 at the University of Bristol. 

It contains all neccessary files to recreate our setup, including the design files and UI (User Interface) that allows users to easily run dynamic tests.

The dyno is made possible through the open-source, VESC, python-can, cantools and PyQT projects, thank you all.

## Getting Started
To install all development dependencies please run:

```sh
pip install requirements.txt
```

## Usage example
To use the GUI, navigate to VescDyno.py and click run.

## Docs
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

## Meta

Daniel Muir – [LinkedIn](https://www.linkedin.com/in/daniel-muir31415/) – danielmuir167@gmail.com

Distributed under the MIT license. See ``LICENSE`` for more information.

[Github page](https://github.com/dan17229/V-Dyno)

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