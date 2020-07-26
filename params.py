
class Species_Params:
    def __init__(self, **kwargs):
        self.sp = {
        'PSPECIES' : 'FINE-SILT'       ,
        'PDECAY'  : '-9.9'    ,
        'PWETA_GAS': '-9.0000002E-10',
        'PWETB_GAS' : '-9.900000'    ,
        'PCRAIN_AERO' :  '1.000000' ,
        'PCSNOW_AERO' : '1.000000'    ,
        'PCCN_AERO'   : '0.9000000'    ,
        'PIN_AERO'   : '0.1000000'    ,
        'PRELDIFF':  '-9.900000'    ,
        'PHENRY'  : '-9.0000002E-10',
        'PF0' : '-9.000000'    ,
        'PDENSITY' :  '1400.000'    ,
        'PDQUER' : '2.0E-06',
        'PDSIGMA' : '1.250'    ,
        'PDRYVEL' :'-9.990'    ,
        'PWEIGHTMOLAR' :  '-9.900000'    ,
        'POHCCONST' : '-9.0000002E-10',
        'POHDCONST':  '-9.9'   ,
        'POHNCONST':  '2.0' }
        for k, o in kwargs.items():
            self.sp[k] = o
    
    
    @property
    def species_Params(self):
        return self.sp
            
            
class Outgrid:
    def __init__(self,**kwargs):
        self.og ={ 
             'OUTLON0' :'60.00000'    ,
             'OUTLAT0' :'30.00000'    ,
             'NUMXGRID' :    '680',
             'NUMYGRID' :'320',
             'DXOUT' : '0.1000000'    ,
             'DYOUT' :  '0.1000000'    ,
             'OUTHEIGHTS':'100.0000    ,   500.0000    ,   1000.000    ,   5000.000'    
        }
        for k, o in kwargs.items():
            self.og[k] = o
    @property
    def outgrid(self):
        return self.og

class Releases:
    def __init__(self, **kwargs):
        self.r = {'PARTS':'50000', 
                  'Z1':'100',
                  'Z2': '100',
                  'ZKIND': '1',
                  'MASS' : '1.0000E8'
                 }

        for k, o in kwargs.items():
            self.r[k] = o
    @property
    def IDATE1(self):
        return self.r['IDATE1']
    @IDATE1.setter
    def IDATE1(self, bdate):
        self.r['IDATE1'] = bdate
    @property
    def ITIME1(self):
        return self.r['ITIME1']
    @ITIME1.setter
    def ITIME1(self, etime):
        self.r['ITIME1'] = etime
    @property
    def IDATE2(self):
        return self.r['IDATE2']
    @IDATE2.setter
    def IDATE2(self, bdate):
        self.r['IDATE2'] = bdate
    @property
    def ITIME2(self):
        return self.r['ITIME2']
    @ITIME2.setter
    def ITIME2(self, btime):
        self.r['ITIME2'] = btime
    
    @property
    def LON1(self):
        return self.r['LON1']
    @LON1.setter
    def LON1(self, lon):
        self.r['LON1'] = lon
    @property
    def LAT1(self):
        return self.r['LAT1']
    
    @LAT1.setter
    def LAT1(self, lat):
        self.r['LAT1'] = lat
        
    @property
    def LON2(self):
        return self.r['LON2']
    
    @LON2.setter
    def LON2(self, lon):
        self.r['LON2'] = lon
    
    @property
    def LAT2(self):
        return self.r['LAT2']
    
    @LAT2.setter
    def LAT2(self, lat):
        self.r['LAT2'] = lat
    
    @property
    def comment(self):
        return self.r['COMMENT']
    @comment.setter
    def comment(self, comment):
        self.r['COMMENT'] = comment
    @property
    def release(self):
        return self.r
        
    
class Command:
    def __init__(self, **kwargs):
        self.c = {
             'LDIRECT': '1',
             'IBDATE': '20190309',
             'IBTIME': '060000',
             'IEDATE': '20190310',
             'IETIME': '120000',
             'LOUTSTEP':       '3600',
             'LOUTAVER':       '3600',
             'LOUTSAMPLE':       '900',
             'ITSPLIT':  '99999999',
             'LSYNCTIME':        '900',
             'CTL' : '-5.0000000'    ,
             'IFINE':          '4',
             'IOUT':    '1',
             'IPOUT':          '0',
             'LSUBGRID' :          '0',
             'LCONVECTION' :          '0',
             'LAGESPECTRA':          '0',
             'IPIN':          '0',
             'IOUTPUTFOREACHRELEASE' :          '0',
             'IFLUX':          '0',
             'MDOMAINFILL':          '0',
             'IND_SOURCE':          '1',
             'IND_RECEPTOR':          '1',
             'MQUASILAG':          '0',
             'NESTED_OUTPUT':          '0',
             'LINIT_COND':          '0',
             'SURF_ONLY':          '0',
             'CBLFLAG':        '0',
             'OHFIELDS_PATH':          '../../flexin/',
        }
        
        for k, o in kwargs.items():
            self.c[k] = o
    @property
    def command(self):
        return self.c
    @property
    def IBDATE(self):
        return self.c['IBDATE']
    @IBDATE.setter
    def IBDATE(self, bdate):
        self.c['IBDATE'] = bdate
    
    @property
    def IEDATE(self, edate):
        return self.c['IEDATE']
    @IEDATE.setter
    def IEDATE(self, edate):
        self.c['IEDATE'] = edate
     
    
    @property
    def IETIME(self):
        return self.c['IETIME']
    @IETIME.setter
    def IETIME(self, etime):
        self.c['IETIME'] = etime
        
        
    @property
    def IBTIME(self):
        return self.c['IBTIME']
    @IBTIME.setter
    def IBTIME(self, btime):
        self.c['IBTIME'] = btime
        
    
class sites:
    def __init__(self, lon, lat, comment):
        self.lon = lon
        self.lat = lat
        self.comment = comment
    
    
    @property
    def LON(self):
        return self.lon
    
    @property
    def LAT(self):
        return self.lat
    
    @property
    def COMMENT(self):
        return self.comment
    
    
    