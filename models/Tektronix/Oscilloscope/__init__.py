from .. import m_Tektronix

import time
from struct import unpack
import csv

import numpy

class m_OscilloscopeBase(m_Tektronix):
    # Model Constants
    
    validControllers = ['c_VISA']
    
    deviceType = 'Oscilloscope'
    view = 'Tektronix.v_Oscilloscope'
    
    # Device Specific constants
    validWaveforms = ['CH1', 'CH2', 'CH3', 'CH4', 'REF1', 'REF2', 'REF3', 'REF4', 'MATH1', 'MATH2', 'MATH3', 'MATH4']
    validTriggerTypes = ['EDGE', 'TRANSITION']
    validCursorTypes = ['HBARS', 'VBARS', 'SCREEN', 'WAVEFORM', 'XY']

    def onLoad(self):
        m_Tektronix.onLoad(self)
        
        # Configure scope
        self.write('HEADER OFF')
        resp = str(self.ask('HEADER?')).strip()
        if resp != '0':
            time.sleep(2.0)
            self.write('HEADER OFF')
            
        self.data = {}
        
    def defaultSetup(self):
        self.write("FAC")
        
        # TODO: Make this not a static delay
        time.sleep(1.0)
        
        # Verify headers are off
        self.write('HEADER OFF')
        resp = str(self.ask('HEADER?')).strip()
        if resp != '0':
            time.sleep(2.0)
            self.write('HEADER OFF')
        
    def getEnabledWaveforms(self):
        en_ch = []
        
        for ch in m_OscilloscopeBase.validWaveforms:
            resp = self.ask('SELECT:' + ch + '?')
            if int(resp):
                en_ch.append(ch)
        
        return en_ch
    
    def setAcquisitionSetup(self, **kwargs):
        """
        Valid values for 'State': OFF, ON, RUN, STOP, SINGLE
        From the Tektronix Documentation:
        
        
        SAMple specifies that the displayed data point value is the first sampled value
        that is taken during the acquisition interval. In sample mode, all waveform data
        has 8 bits of precision. You can request 16 bit data with a CURVe query but the
        lower-order 8 bits of data will be zero. SAMple is the default mode.
        
        PEAKdetect specifies the display of high-low range of the samples taken from a
        single waveform acquisition. The high-low range is displayed as a vertical column
        that extends from the highest to the lowest value sampled during the acquisition
        interval. PEAKdetect mode can reveal the presence of aliasing or narrow spikes.
        
        HIRes specifies Hi Res mode where the displayed data point value is the
        average of all the samples taken during the acquisition interval. This is a form
        of averaging, where the average comes from a single waveform acquisition. The number 
        of samples taken during the acquisition interval determines the number of
        data values that compose the average.
        
        AVErage specifies averaging mode, in which the resulting waveform shows an
        average of SAMple data points from several separate waveform acquisitions. The
        instrument processes the number of waveforms you specify into the acquired
        waveform, creating a running exponential average of the input signal. The number
        of waveform acquisitions that go into making up the average waveform is set or
        queried using the ACQuire:NUMEnv command.
        
        WFMDB (Waveform Database) mode acquires and displays a waveform pixmap. A
        pixmap is the accumulation of one or more acquisitions.
        
        ENVelope specifies envelope mode, where the resulting waveform shows the
        PEAKdetect range of data points from several separate waveform acquisitions.
        The number of waveform acquisitions that go into making up the envelope
        waveform is set or queried using the ACQuire:NUMEnv command.
        
        The instrument acquires data after each trigger event using Sample mode; it then
        determines the pix map location of each sample point and accumulates it with
        stored data from previous acquisitions.
        A Pix map is a two dimensional array. The value at each point in the array is
        a counter that reflects the hit intensity. Infinite and noninfinite persist display
        modes affect how pix maps are accumulated. Zoom, Math, FastAcq, FastFrame,
        XY, Roll, and Interpolated Time (IT) Sampling Mode are conflicting features to
        WFMDB acqMode. Turning on one of them generally turns the other one off.
        Selection of some standard masks (for example, eye masks, which require option
        MTM) changes the acquisition mode to WFMDB.
        """
        
        if 'State' in kwargs:
            if kwargs['State'] == 'SINGLE':
                self.write("ACQ:STOPAFTER SEQUENCE")
                self.write("ACQ:STATE 1")
            else:
                self.write('ACQ:STOPAFTER RUNSTOP')
                self.write('ACQ:STATE ' + str(kwargs['State']))
                
        if 'FastAcq' in kwargs:
            self.write('FASTACQ:STATE ' + str(kwargs['FastAcq']))
            
        if 'MagniVu' in kwargs:
            self.write('ACQ:MAGNIVU ' + str(kwargs['MagniVu']))
        
        if 'Mode' in kwargs:
            
            if kwargs['Mode'] == 'Sample':
                self.write('ACQ:MODE SAMPLE')
                
            elif kwargs['Mode'] == 'PeakDetect':
                self.write('ACQ:MODE PEAK')
                
            elif kwargs['Mode'] == 'HighResolution':
                self.write('ACQ:MODE HIRES')
                
            elif kwargs['Mode'] == 'Average':
                self.write('ACQ:MODE AVERAGE')
                if 'Number' in kwargs:
                    self.write('ACQ:NUMAVG ' + str(kwargs['Number']))
                
            elif kwargs['Mode'] == 'WaveformDB':
                self.write('ACQ:MODE WFMDB')
                
            elif kwargs['Mode'] == 'Envelope':
                self.write('ACQ:MODE ENV')
                if 'Number' in kwargs:
                    self.write('ACQ:NUMENV ' + str(kwargs['Number']))
                
        if 'RollMode' in kwargs:
            self.write('HOR:ROLL ' + str(kwargs['RollMode']))
        
        if 'SamplingMode' in kwargs:
            if kwargs['SamplingMode'] == 'RealTime':
                self.write('ACQ::SAMPLINGMODE RT')
            elif kwargs['SamplingMode'] == 'Equivalent':
                self.write('ACQ::SAMPLINGMODE ET')
            elif kwargs['SamplingMode'] == 'Interpolate':
                self.write('ACQ::SAMPLINGMODE IT')
                
    def setCursorSetup(self, **kwargs):
        if 'Type' in kwargs and kwargs['Type'] in m_OscilloscopeBase.validCursorTypes:
            if 'Display' in kwargs:
                self.write('CURS:STATE ' + str(kwargs['Display']))
            if 'Mode' in kwargs:
                self.write('CURS:MODE ' + str(kwargs['Mode']))
            if 'Type' in kwargs:
                self.write('CURS:FUNC ' + str(kwargs['Type']))
            if 'LineStyle' in kwargs:
                self.write('CURS:LINESTYLE ' + str(kwargs['LineStyle']))
            if 'Source1' in kwargs and kwargs['Source1'] in m_OscilloscopeBase.validWaveforms:
                self.write('CURS:SOURCE1 ' + kwargs['Source1'])
            if 'Source2' in kwargs and kwargs['Source2'] in m_OscilloscopeBase.validWaveforms:
                self.write('CURS:SOURCE2 ' + kwargs['Source2'])
                    
            # Cursor Types
            # Horizontal Bars
            if kwargs['Type'] == 'HBARS':  
                if 'Pos1' in kwargs:
                    self.write('CURS:HBARS:POS1 ' + str(float(kwargs['Pos1'])))
                if 'Pos2' in kwargs:
                    self.write('CURS:HBARS:POS2 ' + str(float(kwargs['Pos2'])))   
            # Vertical Bars
            elif kwargs['Type'] == 'VBARS':
                if 'Pos1' in kwargs:
                    self.write('CURS:VBARS:POS1 ' + str(float(kwargs['Pos1'])))
                if 'Pos2' in kwargs:
                    self.write('CURS:VBARS:POS2 ' + str(float(kwargs['Pos2']))) 
            # Screen
            elif kwargs['Type'] == 'SCREEN':
                if 'X1' in kwargs:
                    self.write('CURS:SCREEN:XPOSITION1 ' + str(float(kwargs['X1'])))
                if 'X2' in kwargs:
                    self.write('CURS:SCREEN:XPOSITION2 ' + str(float(kwargs['X2']))) 
                if 'Y1' in kwargs:
                    self.write('CURS:SCREEN:YPOSITION1 ' + str(float(kwargs['Y1'])))
                if 'Y2' in kwargs:
                    self.write('CURS:SCREEN:YPOSITION2 ' + str(float(kwargs['Y2']))) 
                if 'Style' in kwargs:
                    self.write('CURS:SCREEN:STYLE ' + str(float(kwargs['Style'])))
            # Waveform
            elif kwargs['Type'] == 'WAVEFORM':
                if 'Pos1' in kwargs:
                    self.write('CURS:WAVE:POS1 ' + str(float(kwargs['Pos1'])))
                if 'Pos2' in kwargs:
                    self.write('CURS:WAVE:POS2 ' + str(float(kwargs['Pos2'])))   
                if 'Style' in kwargs:
                    self.write('CURS:WAVEFORM:STYLE ' + str(float(kwargs['Style'])))
            elif kwargs['Type'] == 'XY':
                # TODO
                pass
                    
        else:
            self.logger.error('Must specify cursor Type')
            return False
    
        return True
    
        # TODO: Make this not a static delay
        time.sleep(1.0)
    
    def setHorizontalSetup(self, **kwargs):
        if 'Mode' in kwargs:
            self.write('HOR:MODE ' + kwargs['Mode'])
        if 'SampleRate' in kwargs:
            self.write('HOR:MODE:SAMPLERATE ' + str(float(kwargs['SampleRate'])))
        if 'Scale' in kwargs:
            self.write('HOR:MODE:SCALE ' + str(float(kwargs['Scale'])))
        if 'Position' in kwargs:
            self.write('HOR:POS ' + str(float(kwargs['Position'])))
        # TODO: Implement:
        # Units
        # Delay
        # Record Length
        # Roll Mode
        
    def setVerticalSetup(self, **kwargs):
        if 'Waveform' in kwargs:
            if kwargs['Waveform'] not in m_OscilloscopeBase.validWaveforms:
                return False
            
            # Channel Config
            if kwargs['Waveform'][0:2] == 'CH':
                ch = kwargs['Waveform']
                
                if 'Display' in kwargs:
                    self.write('SELECT:' + ch + ' ' + kwargs['Display'])
                if 'Label' in kwargs:
                    self.write(ch + ':LABEL:NAME ' + '"' + kwargs['Label'] + '"')
                if 'Position' in kwargs:
                    self.write(ch + ':POS ' + str(float(kwargs['Position'])))
                if 'Scale' in kwargs:
                    self.write(ch + ':SCALE ' + str(float(kwargs['Scale'])))
                if 'Coupling' in kwargs:
                    self.write(ch + ':COUP ' + str(kwargs['Coupling']))
                if 'Deskew' in kwargs:
                    self.write(ch + ':DESKEW ' + str(kwargs['Deskew']))
                if 'Bandwidth' in kwargs:
                    self.write(ch + ':BAND ' + str(kwargs['Bandwidth']))
            
            # Reference Config
            if kwargs['Waveform'][0:3] == 'REF':
                pass
            
    def getProbeInformation(self, **kwargs):
        output = {}
        
        if 'Channel' in kwargs and kwargs['Channel'] in m_OscilloscopeBase.validWaveforms:
            output['Type'] = self.ask(kwargs['Channel'] + ':PROBE:ID:TYPE?')
            output['Serial'] = self.ask(kwargs['Channel'] + ':PROBE:ID:SER?')
            output['Range'] = self.ask(kwargs['Channel'] + ':PROBE:RANGE?')
            output['Resistance'] = self.ask(kwargs['Channel'] + ':PROBE:RES?')
            output['Units'] = self.ask(kwargs['Channel'] + ':PROBE:UNITS?')
            
        return output
            
    def setTriggerSetup(self, **kwargs):
        if 'Type' in kwargs and kwargs['Type'] in m_OscilloscopeBase.validTriggerTypes:
            if kwargs['Type'] == 'EDGE':
                if 'Source' in kwargs and kwargs['Source'] in m_OscilloscopeBase.validWaveforms:
                    self.write('TRIG:A:EDGE:SOURCE ' + kwargs['Source'])
                if 'Slope' in kwargs:
                    self.write('TRIG:A:EDGE:SLOPE ' + kwargs['Slope'])
                if 'Level' in kwargs:
                    self.write('TRIG:A:LEVEL:' + kwargs['Source'] + ' ' + str(kwargs['Level']))
        
                    
    def setSearchSetup(self, **kwargs):
        """
        Parameters
        -Search (int) search number between 1-8
        
        Returns True if success or False if failure
        """
        if 'Search' in kwargs and int(kwargs['Search']) in range(1,8):
            if 'Type' in kwargs and kwargs['Type'] in m_OscilloscopeBase.validTriggerTypes:
                if 'Enable' in kwargs:
                    self.write('SEARCH:SEARCH' + str(kwargs['Search']) + ':STATE ' + kwargs['Enable'])
                    # TODO: Is this the right place for this?
                    self.write("SEARCH:MARKALL ON")
                
                self.write('SEARCH:SEARCH' + str(kwargs['Search']) + ':TRIG:A:TYPE ' + kwargs['Type'])
                
                # Trigger Types
                # Transition
                if kwargs['Type'] == 'TRANSITION':
                    if 'Source' in kwargs and kwargs['Source'] in m_OscilloscopeBase.validWaveforms:
                        self.write('SEARCH:SEARCH' + str(kwargs['Search']) + ':TRIG:A:PULSE:SOURCE ' + str(kwargs['Source']))
                    if 'Delta' in kwargs:
                        self.write('SEARCH:SEARCH' + str(kwargs['Search']) + ':TRIG:A:TRAN:DELTATIME ' + str(kwargs['Delta']))
                    if 'HighThreshold' in kwargs:
                        self.write('SEARCH:SEARCH' + str(kwargs['Search']) + ':TRIG:A:TRAN:THR:HIGH:' + str(kwargs['Source']) + ' ' + str(kwargs['HighThreshold']))
                    if 'LowThreshold' in kwargs:
                        self.write('SEARCH:SEARCH' + str(kwargs['Search']) + ':TRIG:A:TRAN:THR:LOW:' + str(kwargs['Source']) + ' ' + str(kwargs['LowThreshold']))
                    if 'Slope' in kwargs:
                        self.write('SEARCH:SEARCH' + str(kwargs['Search']) + ':TRIG:A:TRAN:POL:' + str(kwargs['Source']) + ' ' + str(kwargs['Slope']))
                    if 'Transition' in kwargs:
                        self.write('SEARCH:SEARCH' + str(kwargs['Search']) + ':TRIG:A:TRAN:WHEN ' + str(kwargs['Transition']))
                
            else:
                self.logger.error('Must specify valid Search Type')
                return False
        else:
            self.logger.error('Must specify Search between 1-8')
            return False
        
        # TODO: Make this not a static delay
        time.sleep(5.0)
        
        return True
        
    
    def getSearchMarks(self, **kwargs):
        """
        Returns a list of mark locations
        """
        # TODO: More graceful way of doing this
        if self.waitUntilReady(1.0, 10.0):
            
            if 'Search' in kwargs and int(kwargs['Search']) in range(1,8):
                self.logger.debug('Looking for matches')
                
                matches = int(self.ask('SEARCH:SEARCH' + str(int(kwargs['Search'])) + ':TOTAL?'))
                total_marks = int(self.ask("MARK:TOTAL?"))
                
                hor_scale = float(self.ask('HOR:MODE:SCALE?'))
                hor_pos = float(self.ask('HOR:POS?'))
                
                all_marks = []
                search_marks = []
                
                if matches > 0:
                    self.logger.debug("Expecting %i marks", matches)
                    # Convert the search marks to user marks
                    self.write('SEARCH:SEARCH' + str(kwargs['Search']))
                    
                    # Seek Forward
                    for dir in ['NEXT', 'PREV']:
                        for i in range(1,total_marks+1):
                            if  len(search_marks) < matches:
                                mark_start = float(str(self.ask('MARK:SELECTED:START?')).strip())
                                
                                if mark_start not in all_marks:
                                    mark_owner = str(self.ask('MARK:SELECTED:OWNER?')).strip()
                                    seek_owner = 'SEARCH' + str(kwargs['Search'])
                                    if mark_owner == seek_owner:
                                        # Convert from percentage to time
                                        mark_start = (mark_start - hor_pos) * (hor_scale / 10.0)
                                        
                                        search_marks.append(mark_start)
                                        self.logger.debug("Search Mark Found at " + str(mark_start))
                                        
                                all_marks.append(mark_start)
                                
                                self.logger.debug("Mark Seek " + dir)
                                self.write('MARK ' + dir)
                                
                                time.sleep(1.0)
                                
                        # Exit out of zoom mode
                        self.write("ZOOM:MODE OFF")
                        
                        time.sleep(1.0)
                else:
                    self.logger.debug('No matches found')
                    
                return search_marks
            
            else:
                self.logger.error('Must specify Search between 1-8')
                return False
        else:
            self.logger.error("Unable to get marks while oscilloscope is busy")
            return False

        
    def singleAcquisition(self):
        self.logger.info('Entering Single Acquisition Mode')
        self.setAcquisitionSetup(State='SINGLE')
        
    def statusBusy(self):
        """
        Queries the scope to find out if it is busy
        """
        if int(self.ask('BUSY?')):
            self.logger.debug('Instrument is busy')
            return True
        else:
            self.logger.debug('Instrument is ready')
            return False
        
    def waitUntilReady(self, interval, timeout):
        """
        Poll <interval> seconds until instrument is ready or <timeout> seconds have passed
        """
        try:
            lapsed = 0.0
            while lapsed < timeout:
                if not self.statusBusy():
                    return True
                time.sleep(interval)
                lapsed += interval
                
            self.logger.debug('Instrument was not ready before timeout occurred')
            return False
        except:
            self.logger.exception("An error occurred in waitUntilReady()")
            
    def getWaveform(self, **kwargs):
        if not self.waitUntilReady(1.0, 10.0):
            self.logger.error("Unable to export waveform while oscilloscope is busy")
            return False
        
        self.logger.debug('Starting waveform transfer')
        self.data = {}
        
        # Get the list of enabled waveforms before we begin
        enabledWaveforms = self.getEnabledWaveforms()
        
        # Get time and trigger data
        x_scale = float(self.ask("WFMOUTPRE:XINCR?"))
        hor_scale = float(self.ask("HOR:MODE:SCALE?"))
        sample_rate = float(self.ask("HOR:MODE:SAMPLERATE?"))
        samples = int(sample_rate * hor_scale * 10)
        trigger_sample = int(self.ask("WFMOUTPRE:PT_OFF?"))
        
        self.data['Time'] = numpy.arange(-1 * trigger_sample, samples - trigger_sample) * x_scale
        
        self.logger.debug("Time Scale: %f", x_scale)
        self.logger.debug("Trigger position: %i", trigger_sample)
        self.logger.debug("Sample Rate: %f", sample_rate)
        self.logger.debug("Horizontal Scale: %f", hor_scale)
        self.logger.info("Expecting %i samples", samples)
        
        for ch in enabledWaveforms:
            self.write("DATA:SOURCE %s" % ch)
            self.write("DATA:ENC SRP")
            self.write("DATA:START 1")
            self.write("DATA:STOP %i" % samples)
            
            # Get scale factors for each channel
            y_scale = float(self.ask("WFMOUTPRE:YMULT?"))
            y_zero = float(self.ask("WFMOUTPRE:YZERO?"))
            y_offset = float(self.ask("WFMOUTPRE:YOFF?"))
            
            # Get the number of bytes per data point
            data_width = int(self.ask("WFMOUTPRE:BYT_NR?"))
            
            # Collect and process data
            self.logger.info("Processing Data for %s....", ch)
            self.write("CURVE?")
            data_raw = self.read_raw()
            
            headerlen = 2 + int(data_raw[1])
            header = data_raw[:headerlen]
            data = data_raw[headerlen:-1]
            elems = len(data) / data_width
            
            if data_width == 2:
                data = numpy.array(unpack('%sH' % elems, data))
            elif data_width == 1:
                data = numpy.array(unpack('%sB' % elems, data))
            else:
                self.logger.error('Unhandled data width in getWaveform')
                
            data_scaled = (data - y_offset) * y_scale + y_zero
            
            self.data[ch] = data_scaled

        
    def waveformExport(self, **kwargs):
        return self.exportWaveform(**kwargs)
        
    def exportWaveform(self, **kwargs):
        """
        Possible parameters:
        -Waveforms (list)
        -Filename (str)
        
        returns True if success
        """
        
        # Refresh waveform data
        if self.data == {}:
            self.getWaveform()
        
        # Write data in columns in the CSV file
        if 'Filename' in kwargs:
            filename = kwargs['Filename']
            # Verify file extension
            if filename[-3:] != "csv":
                filename = filename + '.csv'
            try:
                # Open Data file
                f_telem = open(filename, 'wb')
                csvfile = csv.writer(f_telem)
                self.logger.debug("Opened file: %s", filename)
                
                intersect = set(self.validWaveforms).intersection(set(self.data.keys()))
                
                # Add an extra column for a time index
                header = ['Time'] + list(intersect)
                # Write header
                csvfile.writerow(header)
                
                # Write each row
                time = self.data['Time']
                for index in range(0, len(time)):
                    row = [time[index]]
                    for ch in intersect:
                        row.append(self.data[ch][index])
                    csvfile.writerow(row)
                f_telem.close()
                
            except:
                self.logger.exception("Unable to export data to %s" % filename)
                
                return False
                    
        return True
                
    def saveScreenshot(self, **kwargs):
        """
        Parameters:
        -Filename (str): Relative or absolute filename
        -Format (str): BMP, JPEG, PCX, PNG, TIFF
        -Palette (str): COLOR, INKSAVER, BLACKANDWHITE
        
        Returns true if success or false if failure
        """
        
        if 'Filename' in kwargs and 'Format' in kwargs:
            
            temp_filename = kwargs['Filename'] + '.' + kwargs['Format']
            self.write("EXPORT:FILENAME " + '"' + temp_filename + '"')
            self.write("EXPORT:FORMAT " + kwargs['Format'])
            
            if 'Palette' in kwargs:
                self.write("EXPORT:PALETTE " + kwargs['Palette'])
                
            self.write("EXPORT START")
            
            # TODO: Make this not a static delay
            time.sleep(2.0)
            
            remote_filename = self.ask("EXPORT:FILENAME?")
            self.logger.debug('Saved remote screenshot at %s', remote_filename)
            
            return remote_filename
            
        else:
            self.logger.error("Save Screenshot needs parameters Filename and Format")
            
    def lock(self):
        self.write('LOCK ALL')
        
    def unlock(self):
        self.write('UNLOCK ALL')
    