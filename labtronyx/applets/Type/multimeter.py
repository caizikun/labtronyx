from Base_Applet import Base_Applet

import Tkinter as Tk

import matplotlib
import pylab

class multimeter(Base_Applet):
    
    info = {
        # View revision author
        'author':               'KKENNEDY',
        # View version
        'version':              '1.0',
        # Revision date of View version
        'date':                 '2015-03-11',    
        
        # List of compatible models
        'validDrivers':          ['Agilent.Multimeter.m_3441XA', 
                                  'BK_Precision.Multimeter.m_DMM']
    }