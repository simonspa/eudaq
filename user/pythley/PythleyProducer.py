#!/usr/bin/env python3
# load binary lib/pyeudaq.so
import yaml
import pyeudaq
from Keithley import KeithleySMU2400Series

class PythleyProducer(pyeudaq.Producer):
    def __init__(self, name, runctrl):
        pyeudaq.Producer.__init__(self, name, runctrl)
        self.is_running = 0
        print ('New instance of PythleyProducer')

    def DoInitialise(self):
        print ('DoInitialise')

        configuration_file = ''
        with open(self.GetInitItem("config_file"), 'r') as file:
            configuration_file = yaml.load(file, Loader=yaml.SafeLoader)

        self.keithley = KeithleySMU2400Series(configuration_file)
        self.keithley.disable_output();

    def DoConfigure(self):
        print ('DoConfigure')
        self.keithley.disable_output();

        # set V_Start
        self.keithley.set_voltage(self.GetConfigItem("v_start"), unit='V')
        self.keithley.enable_output()

        # ramp to V_Set
        self.keithley.vramp(self.GetConfigItem("v_set"), self.GetConfigItem("v_step"), 'V')

    def DoStartRun(self):
        print ('DoStartRun')
        self.is_running = 1
        self.keithley.enable_output()

    def DoStopRun(self):
        print ('DoStopRun')
        self.is_running = 0

        # ramp to V_Sart
        self.keithley.vramp(self.GetConfigItem("v_start"), self.GetConfigItem("v_step"), 'V')
        # Switch off
        self.keithley.disable_output();

    def DoReset(self):
        print ('DoReset')
        self.is_running = 0
        self.keithley.disable_output();
        del self.keithley

if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser(description='Pythley EUDAQ2 Producer',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--run-control' ,'-r',default='tcp://localhost:44000')
    parser.add_argument('--name' ,'-n',default='Pythley')
    args=parser.parse_args()

    pythleyproducer = PythleyProducer(args.name, args.run_control)
    print("connecting to runcontrol at %s", args.run_control)
    pythleyproducer.Connect()
    time.sleep(1)
    while(pythleyproducer.IsConnected()):
        time.sleep(1)
