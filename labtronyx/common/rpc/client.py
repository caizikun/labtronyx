import threading
import socket
import select
import logging
import errno

from jsonrpc import *
from errors import *

class RpcClient(object):
    """
    Flexible RPC client that connects to an RpcServer instance either on a local
    host or remote host. Abstracts a remote object using the magic of Python.
    By utilizing functions from the remote RpcServer and object that extends
    RpcBase, RpcClient can dynamically create method aliases. In this way, a
    RpcClient object can "become" an instance of an object on a remote host.
    
    Establishes a TCP connection to the server through which all requests are
    send and responses are received. This is a blocking operation, so only one
    request can be sent at a time (currently). 
    
    To manually call a remote method, use the function RpcClient._rpcCall
    
    TODO: Add batch processing
    
    :param address: IP Address of remote RpcServer (Defaults to 'localhost')
    :type address: str - IPv4
    :param port: Port of remote RpcServer
    :type port: int
    """
    
    RPC_TIMEOUT = 10.0
    RPC_MAX_PACKET_SIZE = 1048576 # 1MB
    
    def __init__(self, address, port, **kwargs):
        
        self.address = self._resolveAddress(address)
        self.port = port
        self.logger = kwargs.get('logger', logging)
        self.timeout = self.RPC_TIMEOUT
        self.nextID = 1
        
        if self.port is None:
            raise RpcServerNotFound()
        
        self.methods = []
        self._callbacks = {}
        
        self._connect()
            
        # Update the hostname
        self.hostname = self._rpcCall('rpc_getHostname')
            
        self._refresh()
            
        self._setTimeout() # Default
        
    def _resolveAddress(self, address):
        try:
            socket.inet_aton(address)
            return address
            #self.hostname, _ = socket.gethostbyaddr(address)
        except socket.error:
            # Assume a hostname was given
            #self.hostname = address
            return socket.gethostbyname(address)
        
    def _connect(self):
        # Open a TCP socket
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.address, self.port))
            self.socket.setblocking(0)
            self.socket.settimeout(self.timeout)
        
        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                raise RpcServerNotFound()
            
            elif e.errno == errno.ECONNRESET: #10054: # Connection reset
                raise RpcServerNotFound()
                
            elif e.errno == errno.ETIMEDOUT: #10060: # Time out
                raise RpcServerNotFound()
            
            else:
                raise
            
        except:
            self.socket = None
            raise
        
    def _disconnect(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None
            
    def _enableNotifications(self):
        """
        Open a UDP port and send a notification registration request to the
        server.
        
        :returns: True if successful, False otherwise
        """
        try:
            self.note_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.note_socket.bind(('', 0))
            self.note_socket.setblocking(0)
            
            # Get the IP Address of the socket bound to the server
            address, _ = self.socket.getsockname()
            # Get the port of the UDP socket
            _, port = self.note_socket.getsockname()
            
            self._rpcCall('rpc_register', address, port)
            return True
        
        except:
            self.logger.exception("Exception while enabling notifications")
            return False
        
    def _disableNotifications(self):
        try:
            address, _ = self.socket.getsockname()
            self.note_socket.close()
            
            self._rpcCall('rpc_unregister', address)
            
            del self.note_socket
        except:
            pass
        
        return True
    
    def _registerCallback(self, event, method):
        self._callbacks[event] = method
    
    def _checkNotifications(self):
        try:
            while True:
                data = self.note_socket.recv(self.RPC_MAX_PACKET_SIZE)
                
                # Decode the RPC request
                in_packet = JsonRpcPacket(data)
                
                requests = in_packet.getRequests()
                for req in requests:
                    method = req.getMethod()
                    method = self._callbacks.get(method, None)
                    
                    if method is not None:
                        # Return from notification is discarded
                        req.call(method)
                    
                
        except socket.error:
            pass
    
    def _send(self, data_out):
        for attempt in range(2):
            try:
                self.socket.send(data_out)
                break
                
            except socket.error as e:
                if e.errno == errno.ECONNRESET:
                    self._disconnect()
                    self._connect()
                else:
                    raise
    
    def _recv(self):
        ready_to_read, _, _ = select.select([self.socket], [], [], self.timeout)
        
        if self.socket in ready_to_read:
            data = self.socket.recv(self.RPC_MAX_PACKET_SIZE)
            
            return data
        
    def _refresh(self):
        """
        Get a list of methods from the RPC server and dynamically fill the
        object
        """
        # Clear out old aliases
        for proc in self.methods:
            self._removeAlias(proc)
            
        # Request a list of methods
        self._setTimeout(2.0)
        self.methods = self._rpcCall('rpc_getMethods')
        
        for proc in self.methods:
            self._addAlias(proc)
            
    def _addAlias(self, methodName):
        """
        Dynamically create a method internal to the RpcClient object that will
        invoke an RPC method call when called.
        
        :param methodName: Name of method
        :type methodName: str
        """
        dynFunc = lambda *args, **kwargs: self._rpcCall(methodName, *args, **kwargs)
        setattr(self, methodName, dynFunc)
        
    def _removeAlias(self, methodName):
        
        if hasattr(self, methodName):
            delattr(self, methodName)
            
    def _setTimeout(self, new_to=None):
        """
        Set the Timeout limit for an RPC Method call
        
        :param new_to: New Timeout time in seconds
        :type new_to: float
        """
        if new_to is not None:
            self.timeout = float(new_to)
        else:
            self.timeout = self.RPC_TIMEOUT
        
            
    def _getHostname(self):
        return self.hostname
    
    def _getAddress(self):
        return self.address
    
    def _ready(self):
        return self.ready
    
    def _close(self):
        pass
    
    def _rpcCall(self, remote_method, *args, **kwargs):
        """
        Calls a function on the remote host with both positional and keyword
        arguments
        
        Returns:
            - Whatever the remote function returns
            
        Exceptions:
            - AttributeError when method not found (same as if a local call)
            - RuntimeError when the remote host sent back a server error
            - Rpc_Timeout when the request times out
        """
        # Encode the RPC Request
        nextID = int(self.nextID)
        self.nextID += 1
        packet = JsonRpcPacket()
        packet.addRequest(nextID, remote_method, *args, **kwargs)
        
        # Send the encoded request
        out_str = packet.export()
        
        # Retry if there is an error
        for attempt in range(2):
            try:
                self._send(out_str)
                
                # Wait for return data or timeout
                data = self._recv()
                
                if data:
                    packet = JsonRpcPacket(data)
                    errors = packet.getErrors()
                    responses = packet.getResponses()
                    
                    if len(errors) > 0:
                        # There is a problem if there are more than one errors,
                        # so just check the first one
                        err_obj = JsonRpc_to_RpcErrors.get(type(errors[0]), RpcError)
                        raise err_obj()
                    
                    elif len(responses) == 1:
                        resp = responses[0]
                        return resp.getResult()
                
                    else:
                        raise RpcInvalidPacket()
                    
                else:
                    # Timeout
                    raise RpcTimeout()
                    
            except socket.error as e:
                raise
                        
            except RpcInvalidPacket:
                print data # DEBUG
                self.logger.exception("Invalid RPC Packet")
                    
        raise RpcTimeout()
    
    def __str__(self):
        return '<RPC Instance of %s:%s>' % (self.address, self.port)