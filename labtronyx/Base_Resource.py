import uuid
import time
import threading
import importlib
import sys

import common
import common.rpc as rpc

class Base_Resource(object):
    type = "Generic"
    
    def __init__(self, resID, interface, **kwargs):
        
        common_globals = common.ICF_Common()
        self.config = common_globals.getConfig()
        self.logger = common_globals.getLogger()
        
        self.__uuid = str(uuid.uuid4())
        self.__resID = resID
        self.__interface = interface
        self.__groupTag = kwargs.get('groupTag', '')
        self.__status = 'INIT'
        
        self.driver = None
        
        # Start RPC Server
        self.rpc_server = rpc.RpcServer(name='%s-%s' % (interface.getInterfaceName(), resID),
                                        logger=self.logger)
        self.rpc_server.registerObject(self)
        
    def getUUID(self):
        return self.__uuid
    
    def getResourceID(self):
        return self.__resID
    
    def getGroupTag(self):
        return self.__groupTag
    
    def getResourceType(self):
        return self.type
    
    def getResourceStatus(self):
        return self.__status
    
    def setResourceStatus(self, new_status):
        self.__status = new_status
        
        self.rpc_server.notifyClients('event_status_change')
    
    def getInterfaceName(self):
        """
        Returns the Resource's Controller class name
        
        :returns: str
        """
        return self.__interface.getInterfaceName()
    
    def getPort(self):
        # Start the RPC server if it isn't already started
        if self.rpc_server.rpc_isRunning():
            return self.rpc_server.rpc_getPort()
    
    def getProperties(self):
        res_prop = {
            'uuid': self.getUUID(),
            'interface': self.getInterfaceName(),
            'resourceID': self.getResourceID(),
            'resourceType': self.getResourceType(),
            'groupTag': self.getGroupTag(),
            'status': self.getResourceStatus(),
            'port': self.getPort()
            }
        
        # Append Model properties if a Model is loaded
        if self.driver is not None:
            driver_prop = self.driver.getProperties()
            
            driver_prop['driver'] = self.driver.getDriverName()
            
            res_prop.update(driver_prop)
        
        return res_prop
    
    #===========================================================================
    # Resource State
    #===========================================================================
    
    def isOpen(self):
        raise NotImplementedError
        
    def open(self):
        """
        Open the resource
        
        :returns: True if open was successful, False otherwise
        """
        raise NotImplementedError
    
    def close(self):
        """
        Close the resource
        
        :returns: True if close was successful, False otherwise
        """
        raise NotImplementedError
    
    def lock(self):
        raise NotImplementedError
    
    def unlock(self):
        raise NotImplementedError
    
    #===========================================================================
    # Data Transmission
    #===========================================================================
    
    def write(self, data):
        raise NotImplementedError
    
    def read(self):
        raise NotImplementedError
    
    def query(self):
        raise NotImplementedError
    
    #===========================================================================
    # Driver
    #===========================================================================
    
    def hasDriver(self):
        return self.driver is not None
    
    def loadDriver(self, driverName):
        """
        Load a Driver for a resource. A driver name can be specified to load a 
        specific module, even if it may not be compatible with this resource. 
        Reloads driver when importing, in case an update has occured.
        
        Example::
        
            instr.loadDriver('Tektronix.Oscilloscope.m_DigitalPhosphor')
        
        :param driverName: Module name of the desired Model
        :type driverName: str
        :returns: True if successful, False otherwise
        """
        try:
            # Check if the specified model is valid
            testModule = importlib.import_module(driverName)
            reload(testModule) # Reload the module in case anything has changed
            
            className = driverName.split('.')[-1]
            testClass = getattr(testModule, className)
            
            self.driver = testClass(self)
            self.driver._onLoad()
            
            # RPC register object
            self.rpc_server.registerObject(self.driver)
            self.rpc_server.notifyClients('event_driver_loaded')
            
            return True

        except:

            self.logger.exception('Failed to load driver: %s', driverName)
            return False
    
    def unloadDriver(self):
        """
        If a Driver is currently loaded for the resource, unload it.
        
        :returns: True if successful, False otherwise
        """
        if self.driver is not None:
            try:
                self.driver._onUnload()
                # RPC unregister object
                
                self.rpc_server.unregisterObject(self.driver)
                self.rpc_server.notifyClients('event_driver_unloaded')
                
            except:
                self.logger.exception('Exception while unloading driver')
                
            del self.driver
            self.driver = None
                
            return True
        
        else:
            return False