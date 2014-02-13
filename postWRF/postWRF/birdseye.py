import pdb
import matplotlib as M
M.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as N

from defaults import Defaults
from figure import Figure
import utils
import scales

class BirdsEye(Figure):
    def __init__(self,config,wrfout):
        self.C = config
        self.W = wrfout
        self.D = Defaults()
        self.p2p = self.C.output_root
   
    def plot_data(self,data,mplcommand,fname,pt,V=0):
        # INITIALISE
        self.fig = plt.figure()
        self.fig = self.figsize(8,8,self.fig)     # Create a default figure size if not set by user
        self.bmap,x,y = self.basemap_setup()
        
        if mplcommand == 'contour':
            if not V:
                self.bmap.contour(x,y,data)
            else:
                self.bmap.contour(x,y,data,V)
            
   
        # LABELS, TITLES etc
        """
        Change these to hasattr!
        """
        #if self.C.plot_titles:
        title = utils.string_from_time('title',pt,tupleformat=0)
        plt.title(title)
        #if self.C.plot_colorbar:
        plt.colorbar(orientation='horizontal')

        # SAVE FIGURE
        datestr = utils.string_from_time('output',pt,tupleformat=0)
        self.fname = self.create_fname(fname) # No da variable here
        self.save(self.fig,self.p2p,self.fname)
        self.fig.clf()
    
    def plot2D(self,va,pt,lv,da=0,na=0):
        # INITIALISE
        #en = self.W.path
        self.fig = plt.figure()
        self.fig = self.figsize(8,8,self.fig)     # Create a default figure size if not set by user
        self.bmap,x,y = self.basemap_setup()
        
        # Get indices for time, level, lats, lons
        # TIME
        time_idx = self.W.get_time_idx(pt)
        
        # LEVEL
        if lv == 2000:
            lv_idx = 0
            lv_na = 'sfc' # For naming purposes
        elif isinstance(lv,int):
            lv_idx = 0 # Interpolation file will only have the only level
            lv_na = str(lv) + 'hPa'
            nc_path = self.W.path
            fpath = self.W.interp_to_p(self.C,nc_path,va,lv)
            # Execute p_interp here and reassign self.W to new file
            self.W = WRFOut(fpath)
        else:
            print("Non-pressure levels not supported yet.")
            raise Exception
        
        # LAT/LON
        lat_sl, lon_sl = self.get_limited_domain(da)
        
        # FETCH DATA
        PS = {'t': time_idx, 'lv': lv_idx, 'la': lat_sl, 'lo': lon_sl} 
        data = self.W.get(va,PS)
        
        la_n = data.shape[-2]
        lo_n = data.shape[-1]

        # COLORBAR, CONTOURING
        cm, clvs = scales.get_cm(va,lv)
        # pdb.set_trace()
        if cm:
            self.bmap.contourf(x,y,data.reshape((la_n,lo_n)),clvs,cmap=cm)
        elif isinstance(clvs,N.ndarray):
            self.bmap.contourf(x,y,data.reshape((la_n,lo_n)),clvs,cmap=plt.cm.jet)
        else:
            self.bmap.contourf(x,y,data.reshape((la_n,lo_n)))
        
        # LABELS, TITLES etc
        if self.C.plot_titles:
            title = utils.string_from_time('title',pt)
            plt.title(title)
        if self.C.colorbar:
            plt.colorbar(orientation='horizontal')

        # SAVE FIGURE
        datestr = utils.string_from_time('output',pt)
        if not na:
            # Use default naming scheme
            na = (va,lv_na,datestr)
        else:
            # Come up with scheme...
            print("Coming soon: ability to create custom filenames")
            raise Exception
        self.fname = self.create_fname(*na) # No da variable here
        self.save(self.fig,self.p2p,self.fname)
        plt.close()

    def basemap_setup(self):
        # Fetch settings
        basemap_res = getattr(self.C,'basemap_res',self.D.basemap_res)
        
        width_m = self.W.dx*(self.W.x_dim-1)
        height_m = self.W.dy*(self.W.y_dim-1)

        m = Basemap(
            projection='lcc',width=width_m,height=height_m,
            lon_0=self.W.cen_lon,lat_0=self.W.cen_lat,lat_1=self.W.truelat1,
            lat_2=self.W.truelat2,resolution=basemap_res,area_thresh=500
            )
        m.drawcoastlines() 
        m.drawstates()
        m.drawcountries()

        # Draw meridians etc with wrff.lat/lon spacing
        # Default should be a tenth of width of plot, rounded to sig fig

        x,y = m(self.W.lons,self.W.lats)
        return m, x, y

    
