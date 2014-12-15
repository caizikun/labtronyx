from . import m_BDPC_ICP

class m_BDPC_BR1(m_BDPC_ICP):
    """
    
    """
    
    # Model device type
    deviceType = 'Source'
    
    # List of Valid Vendor Identifier (VID) and Product Identifier (PID) values
    # that are compatible with this Model
    validPIDs = ['BDPC_BR1']
    
    def getProperties(self):
        prop = m_BDPC_ICP.getProperties(self)
        
        prop['deviceVendor'] = 'UPEL'
        prop['deviceModel'] = 'BDPC Dual 2kW'
        
        # Add any additional properties here
        return prop