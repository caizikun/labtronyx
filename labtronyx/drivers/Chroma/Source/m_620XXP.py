"""
.. codeauthor:: Kevin Kennedy <kennedy.kevin@gmail.com>

Limitations
-----------

This driver does not include any of the device programming functionality,
it is assumed that an automated program would be designed in a script that
uses this driver.

API
---
"""
from Base_Driver import Base_Driver

class m_620XXP(Base_Driver):
    """
    Driver for Chroma 6200P Series DC Power Supplies
    """
    
    info = {
        # Device Manufacturer
        'deviceVendor':         'Chroma',
        # List of compatible device models
        'deviceModel':          ['62006P-30-80', '62006P-100-25', '62006P-300-8',
                                 '62012P-40-120', '62012P-80-60', '62012P-100-50', '62012P-600-8',
                                 '62024P-40-120', '62024P-80-60', '62024P-100-50', '62024P-600-8',
                                 '62052P-100-100'],
        # Device type    
        'deviceType':           'DC Power Supply',      
        
        # List of compatible resource types
        'validResourceTypes':   ['VISA'],  
        
        #=======================================================================
        # VISA Attributes        
        #=======================================================================
        # Compatible VISA Manufacturers
        'VISA_compatibleManufacturers': ['CHROMA', 'Chroma'],
        # Compatible VISA Models
        'VISA_compatibleModels':        ['62006P-30-80', '62006P-100-25', 
                                         '62006P-300-8', '62012P-40-120', 
                                         '62012P-80-60', '62012P-100-50', 
                                         '62012P-600-8', '62024P-40-120', 
                                         '62024P-80-60', '62024P-100-50', 
                                         '62024-600-8', '62052P-100-100']
    }
    
    def _onLoad(self):
        self.instr = self.getResource()
        
        self.setRemoteControl()
    
    def _onUnload(self):
        self.setLocalControl()
        
    def getProperties(self):
        prop = Base_Driver.getProperties(self)
        
        prop['protectionModes'] = ['Voltage', 'Current', 'Power']
        prop['terminalSense'] = ['Voltage', 'Current', 'Power']
        prop['controlModes'] = ['Voltage', 'Current']
        
        return prop
    
    def setRemoteControl(self):
        """
        Sets the instrument in remote control mode
        """
        self.instr.write("CONF:REM ON")
    
    def setLocalControl(self):
        """
        Sets the instrument in local control mode
        """
        self.instr.write("CONF:REM OFF")
    
    def powerOn(self):
        """
        Enables the instrument to power the output
        """
        self.instr.write("CONF:OUTP ON")
        
    def powerOff(self):
        """
        Disables the output power connections.
        """
        self.instr.write("CONF:OUTP OFF")
        #self.instr.write("ABORT")
        
    def getError(self):
        """
        Returns the error message and code of the last error
        
        :returns str
        """
        return self.instr.query("SYST:ERR?")
    
    def enableRemoteInhibit(self):
        """
        Enables the remote inhibit pin. This behaves as an external ON/OFF
        control.
        """
        self.instr.write("CONF:INH LIVE")
        
    def disableRemoteInhibit(self):
        """
        Disables the remote inhibit pin.
        """
        self.instr.write("CONF:INH OFF")
        
    def setMeasurementSpeed(self, speed):
        """
        Set the reading speed of the voltage/current sensor
        
        :param speed: Samples per second (one of: 30, 60, 120, 240)
        :type speed: int
        """
        valid_speed = {30: 3,
                       60: 2,
                       120: 1,
                       240: 0}
        if speed in valid_speed:
            self.instr.write("CONF:MEAS:SP %i" % valid_speed.get(speed))
            
        else:
            raise ValueError("Invalid Parameter")
        
    def setMeasurementAverage(self, avg):
        """
        Set the number of readings to average.
        
        :param avg: Number of times to average (1, 2, 4 or 8)
        :type avg: int
        """
        valid_avg = {1: 0,
                     2: 1,
                     4: 2,
                     8: 3}
        if avg in valid_avg:
            self.instr.write("CONF:AVG:TIMES %i" % valid_avg.get(avg))
            
        else:
            raise ValueError("Invalid Parameter")
        
    def setMeasurementAverageMethod(self, avg):
        """
        Set the number of readings to average.
        
        :param avg: Method ('FIX' or 'MOV')
        :type avg: str
        """
        valid_avg = {1: 0,
                     2: 1,
                     4: 2,
                     8: 3}
        if avg in valid_avg:
            self.instr.write("CONF:AVG:TIMES %i" % valid_avg.get(avg))
            
        else:
            raise ValueError("Invalid Parameter")
        
    def setVoltage(self, voltage):
        """
        Set the programmed output voltage level
        
        :param voltage: Voltage (in Volts)
        :type voltage: float
        """
        self.instr.write("SOUR:VOLT %f" % float(voltage))
        
    def getVoltage(self):
        """
        Get the output voltage level
        
        :returns: float
        """
        return float(self.instr.query("SOUR:VOLT?"))
    
    def setMaxVoltage(self, voltage):
        """
        Set the maximum output voltage
        
        :param voltage: Voltage (in Volts)
        :type voltage: float
        """
        self.setVoltageRange(0, voltage)
    
    def setVoltageRange(self, lower, upper):
        """
        Set the output voltage range.
        
        :param lower: Minimum Voltage (in Volts)
        :type lower: float
        :param upper: Maximum Voltage (in Volts)
        :type upper: float
        """
        self.instr.write("SOUR:VOLT:LIM:LOW %f" % float(lower))
        self.instr.write("SOUR:VOLT:LIM:HIGH %f" % float(upper))
    
    def getVoltageRange(self):
        """
        Get the configured output voltage range
        
        :returns: tuple (lower, upper)
        """
        lower = self.instr.query("SOUR:VOLT:LIM:LOW?")
        upper = self.instr.query("SOUR:VOLT:LIM:HIGH?")
        return (lower, upper)
    
    def setCurrent(self, current):
        """
        Set the output current level in Amps
        
        :param current: Current (in Amps)
        :type current: float
        """
        self.instr.write("SOUR:CURR %f" % float(current))
        
    def getCurrent(self):
        """
        Get the output current level
        
        :returns: float
        """
        return float(self.instr.query("SOUR:CURR?"))
           
    def setMaxCurrent(self, current):
        """
        Set the maximum output current
        
        :param current: Current (in Amps)
        :type current: float
        """
        self.setCurrentRange(0, current)
        
    def setCurrentRange(self, lower, upper):
        """
        Set the output current range
        
        :param lower: Minimum Current (in Amps)
        :type lower: float
        :param upper: Maximum Current (in Amps)
        :type upper: float
        """
        self.instr.write("SOUR:CURR:LIM:LOW %f" % float(lower))
        self.instr.write("SOUR:CURR:LIM:HIGH %f" % float(upper))
        
    def getVoltageRange(self):
        """
        Get the configured output current range
        
        :returns: tuple (lower, upper)
        """
        lower = float(self.instr.query("SOUR:CURR:LIM:LOW?"))
        upper = float(self.instr.query("SOUR:CURR:LIM:HIGH?"))
        return (lower, upper)
    
    def getTerminalVoltage(self):
        """
        Get the measured voltage from the terminals of the instrument
        
        :returns: float
        """
        return float(self.instr.query("FETC:VOLT?"))
    
    def getTerminalCurrent(self):
        """
        Get the measured current from the terminals of the instrument
        
        :returns: float
        """
        return float(self.instr.query("FETC:CURR?"))
    
    def getTerminalPower(self):
        """
        Get the measured power from the terminals of the instrument
        
        :returns: float
        """
        return float(self.instr.query("FETC:POW?"))
    
    def setSlewRate(self, voltage=None, current=None):
        """
        Set the voltage and current rise/fall time of the power supply. Units are 
        Volts per milliseconds.
        
        :param voltage: Voltage Slew rate (in V/ms)
        :type voltage: float
        :param current: Current Slew rate (in V/ms)
        :type current: float
        """
        if voltage is not None:
            self.instr.write("SOUR:VOLT:SLEW %f" % float(voltage))
        else:
            self.instr.write("SOU")
            
        if current is not None:
            self.instr.write("SOUR:CURR:SLEWINF DISABLE")
            self.instr.write("SOUR:CURR:SLEW %f" % float(current))
        else:
            self.instr.write("SOUR:CURR:SLEWINF ENABLE")
    
    def setProtection(self, voltage=None, current=None, power=None):
        """
        Enable the protection circuitry. If any of the parameters is zero, that
        protection is disabled.
        
        :param voltage: OVP Setting (in Volts)
        :type voltage: float
        :param current: OCP Setting (in Amps)
        :type current: float
        :param power: OPP Setting (in Watts)
        :type power: float
        """
        
        # Voltage
        if voltage is not None:
            self.instr.write("SOUR:VOLT:PROT:HIGH %f" % float(voltage))
                
        # Current
        if current is not None:
            self.instr.write("SOUR:CURR:PROT:HIGH %f" % float(current))
    
        # Power
        if power is not None:
            self.instr.write("SOUR:POW:PROT:HIGH %f" % float(power))
    
    def getProtection(self):
        """
        Get the protection set points
        
        :returns: dict with keys ['Voltage', 'Current', 'Power']
        """
        ret = {}
        
        ret['Voltage'] = self.instr.query('SOUR:VOLT:PROT:HIGH?')
        ret['Current'] = self.instr.query('SOUR:CURR:PROT:HIGH?')
        ret['Power']   = self.instr.query('SOUR:POW:PROT:HIGH?')
        
        return ret
    