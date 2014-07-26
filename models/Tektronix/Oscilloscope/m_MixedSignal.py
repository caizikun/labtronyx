# Models:
# MSO 2XXX, 3XXX, 4XXX, 5XXX
from m_DigitalPhosphor import m_DigitalPhosphor

class m_MixedSignal(m_DigitalPhosphor):
        
    validPIDs = [ # MSO2XXX Series
                    
                    # MSO3XXX Series
                    
                    # MSO4XXX Series
                    
                    # MSO5XXX Series
                    "MSO5034", "MSO5034B", "MSO5054", "MSO5054B", "MSO5104", "MSO5104B", "MSO5204", "MSO5204B"
                    # MSO7XXXX Series
                    "MSO70404C", "MSO70604C", "MSO70804C", "MSO71254C", "MSO71604C", "MSO72004C", "MSO72304DX", "MSO72504DX", "MSO73304DX", 
                    ]

    def onLoad(self):
        m_DigitalPhosphor.onLoad(self)
        
        self.logger.debug("Loaded Tektronix Mixed Signal Oscilloscope Model")