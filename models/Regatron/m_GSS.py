import struct
from models import m_Base

class m_GSS(m_Base):
    
    # Model device type
    deviceType = 'Source'
    
    # List of valid Controllers that are compatible with this Model
    validControllers = ['c_Serial']
    
    # List of Valid Vendor Identifier (VID) and Product Identifier (PID) values
    # that are compatible with this Model
    validVIDs = ['']
    validPIDs = ['']
    
    def _onLoad(self):
        self.controller = self.getControllerObject()
        self.instr = self.controller.openResourceObject(self.resID)
        
        # Configure the COM Port
        self.instr.baudrate = 38400
        self.instr.timeout = 1.0
        self.instr.bytesize = 8
        self.instr.parity = 'N'
        self.instr.stopbits = 1
        
        self.instr.open()
    
    def _onUnload(self):
        self.instr.close()
    
    def getProperties(self):
        ret = m_Base.getProperties(self)
        
        ret['deviceVendor'] = 'Regatron'
        #if self.__identity is not None:
        #    ret['deviceModel'] = ''
        #    ret['deviceSerial'] = ''
        #    ret['deviceFirmware'] = ''
            
        return ret
    
    def _sendFrame(self, frame):
        """
        Send a frame
        
        Calculates the checksum and attaches a header to the outgoing
        data frame.
        
        Checksum is calculated by adding all data bytes, then mod by 0x100
        First byte is a sync byte, it is always 0xA5
        
        :returns: None
        """
        fmt = 'BBB'
        
        total = 0
        for bt in bytearray(frame):
            total += bt
        checksum = total % 0x100
        
        header = struct.pack(fmt, 0xA5, len(frame), checksum)
        
        full = header + frame
        
        self.instr.write(full)
        self.instr.flush()
        
    def _recvFrame(self):
        """
        Receive a frame
        
        Reads the header first to find out how many bytes to receive
        in the payload section
        
        :returns: byte string, payload section of frame
        """
        header = self.instr.read(3)
        
        sync, len, checksum = struct.unpack('BBB', header)
        # TODO Verify checksum?
        
        payload = self.instr.read(len)
        
        return payload
        
    def _cmdReadMemoryWord(self, address):
        """
        Read a memory word
        
        Talk ID: 0x10
        Address is Little-endian (Least Significant Byte first)
        
        :returns: int16
        """
        frame = struct.pack('BBBB', 0x10, address&0xFF, (address>>8)&0xFF, (address>>16)&0xFF);
        
        self._sendFrame(frame)
        
        ret = self._recvFrame()
        
        try:
            talkid, status, datal, datah = struct.unpack('BBBB', ret)
            
            # Process returned data
            data = (datah<<8) | (datal)
            return data
        
        except:
            return 0
    
    def _cmdWriteMemoryWord(self, address, data):
        """
        Write a memory word
        
        Talk ID: 0x11
        Address is Little-endian (Least Significant Byte first)
        Data is Little-endian
        
        :returns: bool, True is successful, False otherwise
        """
        frame = struct.pack('BBBBBB', 0x11, address&0xFF, (address>>8)&0xFF, (address>>16)&0xFF, data&0xFF, (data>>8)&0xFF);
        
        self._sendFrame(frame)
        
        ret = self._recvFrame()
        
        try:
            talkid, status = struct.unpack('BB', ret)
            
            # TODO: Check status?
            
            return True
        
        except:
            return False
    
    def getActualOutputCurrent(self):
        """
        Get the actual output current
        
        Register Address: 0x005085
        Value Range: 0 - 4000 (4000 = 125 A)
        
        :returns: float
        """
        data = self._cmdReadMemoryWord(0x005085)
        
        # The gain from the datasheet seems to be wrong
        # This gain was generated by calibration
        gain = 0.0399877 # 125.0/4000.0
        current = data * gain
        
        return current