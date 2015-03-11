from Base_Driver import Base_Driver

class m_620XXP(Base_Driver):
    
    info = {
        # Model revision author
        'author':               'KKENNEDY',
        # Model version
        'version':              '1.0',
        # Revision date of Model version
        'date':                 '2015-01-31',
        # Device Manufacturer
        'deviceVendor':         'Chroma',
        # List of compatible device models
        'deviceModel':          ['62006P-30-80', '62006P-100-25', '62006P-300-8',
                                 '62012P-40-120', '62012P-80-60', '62012P-100-50', '62012P-600-8',
                                 '62024P-40-120', '62024P-80-60', '62024P-100-50', '62024-600-8',
                                 '62052P-100-100'],
        # Device type    
        'deviceType':           'Power Supply',      
        
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
    
    def _onUnload(self):
        pass
    
    def powerOn(self):
        self.instr.write("CONF:OUTP ON")
        
    def powerOff(self):
        self.instr.write("CONF:OUTP OFF")
        #self.instr.write("ABORT")
        
    def setVoltage(self, voltage):
        self.instr.write("SOUR:VOLT %f" % float(voltage))
    
    def setVoltageLimit(self, voltage):
        self.instr.write("SOUR:VOLT:LIM:HIGH %f" % float(voltage))
        
    def measureVoltage(self):
        return self.instr.ask("FETC:VOLT?")
    
    def setCurrent(self, current):
        self.instr.write("SOUR:CURR %f" % float(current))
        
    def setCurrentLimit(self, current):
        self.instr.write("SOUR:CURR:PROT:HIGH %f" % float(current))
        
    def measureCurrent(self):
        return self.instr.ask("FETC:CURR?")
    
    def measurePower(self):
        return self.instr.ask("FETC:POW?")