"""Take config settings and run plotting scripts.

Classes:
C = Config = configuration settings set by user, passed from user script
D = Defaults = used when user does not specify a non-essential item
W = Wrfout = wrfout file
F = Figure = a superclass of figures
    mp = Birdseye = a lat--lon slice through data with basemap
    xs = CrossSection = distance--height slice through data with terrain 

"""

import os
import matplotlib as M
M.use('Agg')
import matplotlib.pyplot as plt
import collections
import fnmatch
import pdb

from wrfout import WRFOut
from axes import Axes
from figure import Figure
from birdseye import BirdsEye
import scales
from defaults import Defaults
import utils

class PyWRFEnv:
    def __init__(self,config):
        self.C = config

        # Set defaults if they don't appear in user's settings
        self.D = Defaults()
        
        self.font_prop = getattr(self.C,'font_prop',self.D.font_prop)
        self.usetex = getattr(self.C,'usetex',self.D.usetex)
        self.dpi = getattr(self.C,'dpi',self.D.dpi)
        self.plot_titles = getattr(self.C,'plot_titles',self.D.plot_titles) 

        # Set some general settings
        M.rc('text',usetex=self.usetex)
        M.rc('font',**self.font_prop)
        M.rcParams['savefig.dpi'] = self.dpi

    def wrfout_files_in(self,folder,dom='notset',init_time='notset'):
        w = 'wrfout' # Assume the prefix
        if init_time=='notset':
            suffix = '*'
            # We assume the user has wrfout files in different folders for different times
        else:
            try:
                it = self.string_from_time('wrfout',init_time)
            except:
                print("Not a valid wrfout initialisation time; try again.")
                raise Error
            suffix = '*' + it

        if dom=='notset':
            # Presume all domains are desired.
            prefix = w + '_d'
        elif (dom == 0) | (dom > 8):
            print("Domain is out of range. Choose number between 1 and 8 inclusive.")
            raise IndexError
        else:
            dom = 'd{0:02d}'.format(dom)
            prefix = w + '_' + dom

        wrfouts = []
        for root,dirs,files in os.walk(folder):
            for fname in fnmatch.filter(files,prefix+suffix):
                wrfouts.append(os.path.join(root, fname))
        return wrfouts

    def dir_from_naming(self,*args):
        l = [str(a) for a in args]
        path = os.path.join(self.C.output_root,*l)
        return path

    def string_from_time(self,usage,t,dom=0,strlen=0,conven=0):
        str = utils.string_from_time(usage=usage,t=t,dom=dom,strlen=strlen,conven=conven)
        return str

    def plot_variable2D(self,va,pt,en,lv,p2p,na=0,da=0):
        """Plot a longitude--latitude cross-section (bird's-eye-view).
        Use Basemap to create geographical data
        
        ========
        REQUIRED
        ========

        va = variable(s)
        pt = plot time(s)
        nc = ensemble member(s)
        lv = level(s) 
        p2p = path to plots

        ========
        OPTIONAL
        ========

        da = smaller domain area(s), needs dictionary || DEFAULT = 0
        na = naming scheme for plot files || DEFAULT = get what you're given

        """
        va = self.get_sequence(va)
        pt = self.get_sequence(pt,SoS=1)
        en = self.get_sequence(en)
        lv = self.get_sequence(lv)
        da = self.get_sequence(da)

        perms = self.make_iterator(va,pt,en,lv,da)
        
        # Find some way of looping over wrfout files first, avoiding need
        # to create new W instances
        # print("Beginning plotting of {0} figures.".format(len(list(perms))))
        #pdb.set_trace() 

        for x in perms:
            va,pt,en,lv,da = x
            W = WRFOut(en)    # wrfout file class using path
            F = BirdsEye(self.C,W,p2p)    # 2D figure class
            F.plot2D(va,pt,en,lv,da,na)  # Plot/save figure
            pt_s = utils.string_from_time('title',pt)
            print("Plotting from file {0}: \n variable = {1}" 
                  " time = {2}, level = {3}, area = {4}.".format(en,va,pt_s,lv,da))
        
    def make_iterator(self,va,pt,en,lv,da):   
        for v in va:
            for p in pt:
                for e in en:
                    for l in lv:
                        for d in da:
                            yield v,p,e,l,d
    
    def get_sequence(self,x,SoS=0):
        """ Returns a sequence (tuple or list) for iteration.

        SoS = 1 enables the check for a sequence of sequences (list of dates)
        """


        if SoS:
            y = x[0]
        else:
            y = x

        if isinstance(y, collections.Sequence) and not isinstance(y, basestring):
            return x
        else:
            return [x]
        
   
    def plot_cross_section(self,var,latA,lonA,latB,lonB):
        xs = CrossSection()
        xs.plot(var,latA,lonA,latB,lonB)
        
    def compute_diff_energy(
            self,ptype,energy,files,t_int,upper=None,lower=None):
        """
        This method computes difference kinetic energy (DKE)
        or different total energy (DTE, including temp)
        between two WRFout files for a given depth of the 
        atmosphere, at given time intervals
        
        Inputs:
        
        ptype   :   'sum_z' or 'sum_xyz'
        energy  :   'kinetic' or 'total'
        upper   :   upper limit of vertical integration
        lower   :   lower limit of vertical integration
        files   :   abs paths to two wrfout files
        t_int   :   time interval between computations
        
        Outputs:
        
        data    :   time series or list of 2D arrays
        
        ptype 'sum_z' integrates vertically between lower and
        upper hPa and creates a time series.
        
        ptype 'sum_xyz' integrates over the 3D space (again between
        the upper and lower bounds) and creates 2D arrays.
        """
        
        if ptype == 'sum_z':
            pass
        elif ptype == 'sum_xyz':
        

        
        return DTE

    def DKE_xyz(nc0,nc1,t_idx):
        """
        Computation for difference kinetic energy (DKE).
        Sums DKE over the 3D space, returns a time series.
        
        Destaggering is not enabled as it introduces
        computational cost that is of miniscule value considering
        the magnitudes of output values.

        Inputs:
        
        nc0     :   netCDF file
        nc1     :   netCDF file
        t_idx   :   times indices to difference
        
        Outputs:
        
        data    :   time series.
        """
        # Wind data
        U0 = nc0.variables['U']
        V0 = nc0.variables['V']
        U1 = nc1.variables['U']
        V1 = nc1.variables['V']

        xlen = U0.shape[2]

        DKE = []
        for n,t in enumerate(t_idx):
            print("Finding DKE at time {0} of {1}.".format(n,len(t)))
            DKE_hr = 0   # Sum up all DKE for the 3D space
            for i in range(xlen):
                DKE_hr += N.sum(0.5*((U0[t,:,:,i]-U1[t,:,:,i])**2 +
                                (V0[t,:,:-1,i]-V1[t,:,:-1,i])**2))
            print("DTE at this time: {0}".format(DKE_hr)
            DKE.append(DKE_hr)
        return DKE 

    def DKE_z(nc0,nc1,t_idx,lower,upper):
        """
        Computation for difference kinetic energy (DKE).
        Sums DKE over all levels between lower and upper,
        for each grid point, and returns a 2D array.
        
        Destaggering is not enabled as it introduces
        computational cost that is of miniscule value considering
        the magnitudes of output values.
        
        Method finds levels nearest lower/upper hPa and sums between
        them inclusively.
                
        Inputs:
        
        nc0     :   netCDF file
        nc1     :   netCDF file
        t_idx   :   times indices to difference
        lower   :   lowest level, hPa
        upper   :   highest level, hPa
        
        Outputs:
        
        data    :   2D array.
        """
        
        # Speed up script by only referencing data, not 
        # loading it to a variable yet
        
        # WIND
        U0 = nc0.variables['U']
        V0 = nc0.variables['V']
        U1 = nc1.variables['U']
        V1 = nc1.variables['V']

        # PERT and BASE PRESSURE
        P0 = nc0.variables['P']
        PB0 = nc0.variables['PB']
        P1 = nc1.variables['P']
        PB1 = nc1.variables['PB']

        xlen = U0.shape[2] # 1 less than in V
        ylen = V0.shape[3] # 1 less than in U
        zlen = U0.shape[1] # identical in U & V
        
        # Generator for lat/lon points
        def latlon(nlats,nlons):
            for i in nlats:
                for j in nlons:
                    yield i,j
                
        gridpts = latlon((xlen,ylen))
        
        DKE = []
        for n,t in enumerate(t_idx): 
            DKE2D = N.zeros(xlen,ylen)
            for gridpt in gridpts:
                i,j = gridpt
                
                # Find closest level to 'lower', 'upper'
                P_col = P0[t,:,i,j] + PB0[t,:,i,j]
                if lower:
                    low_idx = util.closest(P_col,lower)
                else:
                    low_idx = None
                if upper:
                    upp_idx = util.closest(P_col,upper)
                else:
                    upp_idx = None
                
                zidx = slice(low_idx,upp_idx+1) 
                
                # Integrate over all those points
                DKE2D[i,j] = N.sum(0.5*((U0[t,zidx,i,j]-U1[t,zidx,i,j])**2 +
                                (V0[t,zidx,i-1,j]-V1[t,zidx,i,j])**2))
            DKE.append(DKE2D)
        
        return DKE
        