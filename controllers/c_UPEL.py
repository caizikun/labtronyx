import controllers
import common.upel_icp as icp

import socket
import select
import time
import threading
import Queue
from sets import Set

class c_UPEL(controllers.c_Base):
    
    resources = {}
    devices = {}

    def open(self):
        # Start the arbiter thread
        self.arbiter = c_UPEL_arbiter(self)
        self.arbiter.start()
        self.arbiter.alive.wait(5.0)
        
        return self.arbiter.alive.is_set()
    
    def close(self):
        self.arbiter.stop()
    
    def getResources(self):
        return self.resources
    
    def canEditResources(self):
        return True
    
    #===========================================================================
    # Optional - Automatic Controllers
    #===========================================================================
    
    def refresh(self):
        """
        Send a UDP broadcast packet on port 7968 and see who responds
        """
        
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        packet = icp.DiscoveryPacket().pack()
        
        #local_ip = str(socket.gethostbyname(socket.getfqdn()))
        
        if self.config.broadcastIP:
            broadcast_ip = self.config.broadcastIP
        else:
            broadcast_ip = '<broadcast>'
        
        # Send Discovery Packet
        self.socket.sendto(packet, (broadcast_ip, self.DEFAULT_PORT))
        
        #s.sendto(packet, ('192.168.1.130', self.DEFAULT_PORT))
        #s.sendto(packet, ('192.168.1.137', self.DEFAULT_PORT))
        t_start = time.time()
        
        while (time.time() - t_start) < 2.0:
            #data = repr(time.time()) + '\n'
            read, _, _ = select.select([self.socket],[],[], 2.0)
            
            if self.socket in read:
                data, address = self.socket.recvfrom(4096)

                try:
                    resp_pkt = icp.UPEL_ICP_Packet(data)
                    
                    if resp_pkt.PACKET_TYPE == 0xF:
                        # Filter Discovery Packets
                        ident = resp_pkt.PAYLOAD.split(',')
                        
                        res = (ident[0], ident[1])
                        self.resources[address[0]] = res
                        
                        self.logger.info("Found UPEL ICP Device: %s %s" % res)
                    
                    
                except icp.ICP_Invalid_Packet:
                    pass
    
    #===========================================================================
    # Optional - Manual Controllers
    #===========================================================================
    
    def addResource(self, ResID, VID, PID):
        pass
    
    def destroyResource(self):
        pass
    
class c_UPEL_arbiter(threading.Thread):
    """
    The UPEL Arbiter thread manages communication in and out of the network socket
    on port 7968.
    
    Structure
    =========
    
    Message Queue
    -------------
    
    Packets to send out to remote devices are queued in the message queue and sent
    one at a time. Queuing a message requires:
    
      * IP Address
      * TTL (Time to Live)
      * Response Queue
      * ICP Packet Object
    
    The response packet object will be loaded into the response queue.
    
    Routing Map
    -----------
    
    When a message is sent, it is assigned an ID within the packet header. If a
    response is expected from an outgoing packet, an entry is made in the map
    table to associate the packet ID of the response packet with the object that
    sent the original packet.
    
    The Arbiter will periodically scan the routing map for old entries. If an
    entry has exceeded the TTL window, a signal is sent to the originating
    object that a timeout condition has occurred. 
    
    The Packet ID is an 8-bit value, so there are 256 possible ID codes. A 
    Packet ID of 0x00 is reserved for "notification" packet where a response is 
    not expected, and thus will never create an entry in the routing map, giving 
    a maximum of 255 possible entries in the routing map.
    
    The routing map has the format: { PacketID: (TTL, ResponseQueue) }
    
    Execution Strategy
    ==================
    
    The arbiter will alternate between servicing the message queue, processing 
    any data in the socket buffer, and checking the status of entries in the 
    routing map. If none of those tasks requires attention, the thread will 
    sleep for a small time interval to limit loading the processor excessively.
    """
    
    DEFAULT_PORT = 7968
    alive = threading.Event()
    
    def __init__(self, controller):
        threading.Thread.__init__(self)
        self.controller = controller
    
    def run(self):
        # Init
        self.__messageQueue = Queue.Queue()
        self.__routingMap = {}
        self.__availableIDs = Set(range(1,255))
        
        #import config
        #self.config = config.Config()
        
        # Configure Socket
        # IPv4 UDP
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(('', self.DEFAULT_PORT))
            self.socket.setblocking(0)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
        except:
            pass
        
        self.alive.set()
        
        while (self.alive.is_set()):
            #===================================================================
            # Service the socket
            #===================================================================
            self._serviceSocket()
            
            #===================================================================
            # Service the message queue
            #===================================================================
            
            #===================================================================
            # Check for dead entries in the routing map
            #===================================================================
            
            # Sleep?
            
    def stop(self):
        self.socket.shutdown(1)
        self.socket.close()
        
        self.alive.clear()
        
    def queueMessage(self, destination, ttl, response_queue, packet_obj):
        """
        Insert a message into the queue
        """
        
    def _getPacketID(self):
        try:
            s = self.__availableIDs.pop()
            return s
        
        except KeyError:
            return False
        
    def _serviceSocket(self):
            read, _, _ = select.select([self.socket],[],[], 0.5)
            
            if self.socket in read:
                data, address = self.socket.recvfrom(4096)
            
                try:
                    resp_pkt = icp.UPEL_ICP_Packet(data)
                    
                    if resp_pkt.PACKET_TYPE == 0xF:
                        # Filter Discovery Packets
                        ident = resp_pkt.PAYLOAD.split(',')
                        
                        res = (ident[0], ident[1])
                        self.resources[address[0]] = res
                        
                        self.logger.info("Found UPEL ICP Device: %s %s" % res)
                    
                    
                except icp.ICP_Invalid_Packet:
                    pass