# H. Wennlöf, based on code from C. Riegel
# 2018

import serial
from serial import Serial
import time
import yaml

Units = {
          'Voltage' :
          { 'mV' : 0.001,
             'V' : 1.0},

          'Current' :
          { 'nA' : 0.000000001,
            'uA' : 0.000001,
            'mA' : 0.001,
             'A' : 1.0}
         }

Modi = {
         'Source' :
         { 'V' : 'VOLT',
            'v' : 'VOLT',
            'A' : 'CURR',
            'a' : 'CURR'
         },
         'Measure' :
         { 'V' : 'VOLT',
          'v' : 'VOLT',
           'A' : 'CURR',
           'a' : 'CURR'}
         }


#Class for the Keithley SMU 2400/2410 series
class KeithleySMU2400Series:
    ser = None

    def __init__(self, conf):
        self.configuration_file = conf
        self.set_device_configuration()

    #===========================================================================
    # Open serial interface
    #===========================================================================
    def open_device_interface(self):
        self._ser.open()
        print ("Device Ready at Port " + self.configuration_file["Device"]["Configuration"]["Port"])

    #===========================================================================
    # Switch on the output
    #===========================================================================
    def enable_output(self):
        self._ser.write(b':OUTPUT ON\r\n')
        print ("Output On")

    def disable_output(self):
        self._ser.write(b':OUTPUT OFF\r\n')
        print ("Output Off")

        # short commands for interpreter
    def on(self):
        for x in range(0,2):
            self.enable_output()
            time.sleep(0.5)

    def off(self):
        for x in range(0,2):
            self.disable_output()
            time.sleep(0.5)

    #===========================================================================
    # Close serial interface
    #===========================================================================
    def close_device_interface(self):
        self._ser.close()
        print("Device Closed at Port " + self.configuration_file["Device"]["Configuration"]["Port"])


    def set_device_configuration(self):
        #Initialization of the Serial interface
        try:
            self._ser = Serial(
                                 port = self.configuration_file["Device"]["Configuration"]["Port"],
                                 baudrate = self.configuration_file["Device"]["Configuration"]["Baudrate"],
                                 timeout = 2,
                                 parity = 'E'
                                 )
            self._source = Modi['Source'][self.configuration_file["Device"]["Configuration"]["Source"]]
            self._measure = Modi['Measure'][self.configuration_file["Device"]["Configuration"]["Measure"]]

            #Specifies the size of data buffer
            self._triggerCount = self.configuration_file["Device"]["Configuration"]["TriggerCount"]

            #Specifies trigger delay in seconds
            self._triggerDelay = self.configuration_file["Device"]["Configuration"]["TriggerDelay"]

            #Specifics source and measure
            self._rangeSource = self.configuration_file["Device"]["Configuration"]["RangeSource"]
            self._autorangeSource = self.configuration_file["Device"]["Configuration"]["AutoRangeSource"]
            self._complianceSource = self.configuration_file["Device"]["Configuration"]["ComplianceSource"]

            self._rangeMeasure = self.configuration_file["Device"]["Configuration"]["RangeMeasure"]
            self._autorangeMeasure = self.configuration_file["Device"]["Configuration"]["AutoRangeMeasure"]
            self._complianceMeasure = self.configuration_file["Device"]["Configuration"]["ComplianceMeasure"]

            #Setup the source
            self._ser.write(("*rst" + "\r\n").encode('utf-8'))
            self._ser.write((':SYST:BEEP:STAT OFF' + '\r\n').encode('utf-8'))
            self._ser.write((':SOUR:CLEar:IMMediate' + '\r\n').encode('utf-8'))
            self._ser.write((":SOUR:FUNC:MODE " + self._source + "\r\n").encode('utf-8'))
            #self._ser.write(b':SOUR:CLEar:IMMediate\r\n')
            self._ser.write((':SOUR:' + self._source + ':MODE FIX' + '\r\n').encode('utf-8'))
            self._ser.write((':SOUR:' + self._source + ':RANG:AUTO ' + self._autorangeSource + '\r\n').encode('utf-8'))
            self._ser.write((':SOUR:' + self._source + ':PROT:LEV ' + str(self._complianceSource) + '\r\n').encode('utf-8'))
            if(self._autorangeSource == 'OFF'):
                self._ser.write((':SOUR:' + self._source + ':RANG ' + str(self._rangeSource) + '\r\n').encode('utf-8'))
            else:
                None

            #Setup the sensing
            self._ser.write((':SENS:FUNC \"' + self._measure + '\"\r\n').encode('utf-8'))
            self._ser.write((':SENS:' + self._measure + ':PROT:LEV ' + str(self._complianceMeasure) + '\r\n').encode('utf-8'))
            self._ser.write((':SENS:' + self._measure + ':RANG:AUTO ' + str(self._autorangeMeasure) + '\r\n').encode('utf-8'))

            #Setup the buffer
            self._ser.write(b':TRAC:FEED:CONT NEVer\r\n')
            self._ser.write(b':TRAC:FEED SENSE\r\n')
            self._ser.write(str.encode(':TRAC:POIN ' + str(self._triggerCount) + '\r\n'))
            self._ser.write(b':TRAC:CLEar\r\n')
            self._ser.write(b':TRAC:FEED:CONT NEXT\r\n')

            #Setup the data format
            self._ser.write(b':FORMat:DATA ASCii\r\n')
            self._ser.write(b':FORMat:ELEM VOLTage, CURRent\r\n')

            #Setup the trigger
            self._ser.write(str.encode(':TRIG:COUN ' + str(self._triggerCount) + '\r\n'))
            self._ser.write(str.encode(':TRIG:DELay ' + str(self._triggerDelay) + '\r\n'))

            print("Device at Port " + self.configuration_file["Device"]["Configuration"]["Port"] + " Configured")

        except ValueError:
            print('ERROR: No serial connection. Check cable!')


    def enable_auto_range(self):
        self._ser.write(b':SENS:RANG:AUTO ON\r\n')

    def disable_auto_range(self):
        self._ser.write(b':SENS:RANG:AUTO OFF\r\n')

    def reset(self):
        self._ser.write(b'*RST\r\n')

    def set_value(self, source_value):
        if(source_value > self._complianceSource):
            print("ERROR: Source value is higher than Compliance!")
        else:
            self._ser.write(str.encode(':SOUR:' + self._source + ':LEVel ' + source_value + '\r\n'))
            time.sleep(self.configuration_file["Device"]["Configuration"]["SettlingTime"])

    # # check vs hardcoded settings
    # def set_voltage(self, voltage_value, unit):
    #     val = voltage_value*Units['Voltage'][unit]
    #     if(val>0):
    #         print ("Please do not set positive VSUB: " + str(val))
    #         return val
    #     elif(val<-8):
    #         print ("Please do not set too low VSUB: " + str(val))
    #         return val
    #     else:
    #         if(val > self._complianceSource):
    #             print("ERROR: Source value is higher than Compliance!")
    #         else:

    #             val = voltage_value*Units['Voltage'][unit]
    #             self._ser.write(str.encode(':SOUR:' + self._source + ':LEVel ' + str(val) + '\r\n'))
    #             time.sleep(self.configuration_file["Device"]["Configuration"]["SettlingTime"])
    #             print ("Output voltage set to " + str(val))

    # check vs polarity and comliance
    def set_voltage(self, voltage_value, unit):
        val = voltage_value*Units['Voltage'][unit]

        # check range of val for positive compliance
        if  ( self._complianceSource >= 0 and not ( val >= 0 and val < self._complianceSource ) ):
            raise ValueError('Parameter out of bounds')

        # check range of val for positive compliance
        elif( self._complianceSource <= 0 and not ( val <= 0 and val > self._complianceSource ) ):
            raise ValueError('Parameter out of bounds')

        # set values
        else:
            val = voltage_value*Units['Voltage'][unit]
            self._ser.write(str.encode(':SOUR:' + self._source + ':LEVel ' + str(val) + '\r\n'))
            time.sleep(self.configuration_file["Device"]["Configuration"]["SettlingTime"])
            print ("  Output voltage set to " + str(val))

    def set_source_upper_range(self, senseUpperRange):
        self._ser.write(str.encode(':SENSE:' + self._source + ':RANG:UPP ' + senseUpperRange + '\r\n'))

    def sample(self):
        self._ser.write(b':TRAC:FEED:CONT NEVer\r\n')
        self._ser.write(b':TRACe:CLEar\r\n')
        self._ser.write(b':TRAC:FEED:CONT NEXT\r\n')
        self._ser.write(b':INIT\r\n')

    def get_raw_values(self):
        self._ser.write(b':TRACe:DATA?\r\n')

    def get_mean(self):
        self._ser.write(b':CALC3:FORM MEAN\r\n')
        self._ser.write(b':CALC3:DATA?\r\n')

    def get_std(self):
        self._ser.write(b':CALC3:FORM SDEV\r\n')
        self._ser.write(b':CALC3:DATA?\r\n')

    def read(self, time_to_wait):
        while ( self._ser.inWaiting() <= 2 ):
            pass
        time.sleep(time_to_wait)
        data = self._ser.read(self._ser.inWaiting())
        return data

    #===========================================================================
    # Returns a list with format [voltage,current]
    #===========================================================================

    def get_value(self, with_error = False):
        self.sample()
        self.get_mean()
        dmean = eval(self.read(self.configuration_file["Device"]["Configuration"]["WaitRead"]))
        if(with_error == True):
            self.get_std()
            dstd = eval(self.read(self.configuration_file["Device"]["Configuration"]["WaitRead"]))
            return dmean, dstd
        else:
            return dmean

    def get_voltage(self):
        self.sample()
        self.get_mean()
        #print(str(self.read(0.1)).split(",")[0])
        d = eval((str(self.read(0.1)).split(",")[0]).split("'")[-1]) #Need to strip away the leading b', to get just the numbers
        self.get_std()
        derr = eval((str(self.read(0.1)).split(",")[0]).split("'")[-1])
        #print ("Voltage = "+str(d)+"V +/- "+str(derr)+"V" )
        return d, derr


    def get_current(self):
        self.sample()
        self.get_mean()
        d = float(str(self.read(0.1)).split(",")[1])/0.000001
        self.get_std()
        derr = float(str(self.read(0.1)).split(",")[1])/0.000001
        #print ("Current = "+str(d)+"uA +/- "+str(derr)+"uA" )
        return d, derr


    #===========================================================================
    # One simple command to read out the status
    #===========================================================================

    def state(self):
        print ("If the script stops here, the output is turned off\n.")
        print ("Output voltage:", self.get_voltage()[0], "V")
        # 2 : Read-Voltage
        print ("Output current:", self.get_current()[0], "uA")
        # 3 : Current

    #ramps the voltage, from current voltage to the given new one.
    def vramp(self, vset, vstep, unit):
        print("Voltage Ramp. If the script stops here, the output is turned off.")
        d = self.get_voltage()[0]
        print("  Ramping output from " + str(d) + "V to " + str(vset) + str(unit))
        while( (d-vstep) > vset ): # Ramping down
            try:
                self.set_voltage(d-vstep, unit)
                time.sleep(0.1)
                d = self.get_voltage()[0]
            except ValueError:
                print("  Error occured, check comliance and voltage.")
                self.set_voltage(   0,unit)
                raise ValueError("Voltage ramp failed")
        while( (d+vstep) < vset ): # Ramping up
            try:
                self.set_voltage(d+vstep, unit)
                time.sleep(0.1)
                d = self.get_voltage()[0]
            except ValueError:
                print("  Error occured, check comliance and voltage.")
                self.set_voltage(   0,unit)
                raise ValueError("Voltage ramp failed")
        try:
            self.set_voltage(vset,unit)
        except ValueError:
            print("  Error occured, check comliance and voltage.")
            self.set_voltage(   0,unit)
            raise ValueError("Voltage ramp failed")
