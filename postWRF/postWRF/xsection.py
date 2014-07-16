"""Create cross-sections through WRF data.

This can be time-height or distance-height.
The height can be pressure, model, geometric, or geopotential

The output can be saved to a pickle file.
This can be useful for creating composites

Input lat/lon can be either specified or from x,y co-ords
calculated from manually clicking on a map with overlaid
data (reflectivity, etc).
"""

# Imports
import numpy as N
from figure import Figure

import WEM.utils as utils

class CrossSection(Figure):

    def __init__(self,config,wrfout,latA=0,lonA=0,latB=0,lonB=0):
        super(CrossSection,self).__init__(config,wrfout)

        if latA and lonA and latB and lonB:
            print("Using user-defined lat/lon transects.")
        else:
            print("Please click start and end points.")
            latA, lonA, latB, lonB = self.popup_transect()

        self.latA = latA
        self.lonA = lonA
        self.latB = latB
        self.lonB = lonB
        

    def popup_transect(self):
        """
        Pops up window for user to select start and
        end point for the cross-section.

        Optional: this map can be overlaid with data
        to better guide the decision.

        Optional: the transect can be saved as an image
        with/without the overlaid data, useful for publication.
        """

    def get_xy(self,lat,lon):
        """
        Return x and y coordinates for given lat/lon.

        exactlat, exactlon      :   exact coordinates of closest x/y
        """
        x,y,exactlat,exactlon = utils.getXY(self.W.lats1D,self.W.lons1D,lat,lon)
        return x,y

    def get_height(self,x,y,z,pts):
        """
        Return terrain heights along cross-section
        
        TODO: What's the diff between the outputs?

        Inputs:
        x       :   x indices, as int
        y       :   y imdices, as int
        z       :   z indices, as int
        pts     :   number of points along the x-sec

        Outputs:
        terrain_z   :   terrain height
        heighthalf  :   who knows?

        Assuming t=0
        """
        # TODO: change API of W.get()
        geopot = self.W.get('geopot',[0,z,y,x])
        dryairmass = self.W.get('dryairmass',[0,y,x])
        znw = self.W.get('ZNW',[0,z])
        znu = self.W.get('ZNU',[0,z])

        heighthalf = N.zeros((len(z),pts))

        for i in range(pts):
            pfull = dryairmass[i] * znw+self.P_top
            phalf = dryairmass[i] * znu+self.P_top
            for k in range(len(z)):
                heighthalf[k,i] = interp(geopot[:,i],pfull[:],phalf[k])/mc.g

        terrain_z = geopot[0,:]/mc.g
        # TODO: import metconstants as mc
        return heighthalf, terrain_z

    def plot_xs(self,v,t):
        """
        Inputs:
        v   :   variable to plot, from this list:
                parawind,perpwind,wind,U,V,W,T,RH,


        """
        tidx = self.W.get_time_idx(t)

        xA, yA = self.get_xy(self.latA,self.lonA)
        xB, yB = self.get_xy(self.latB,self.lonB)
        hyp_pts = int(N.hypot(xB-xA,yB-yA))
        xx = N.linspace(xA,xB,hyp_pts)
        yy = N.linspace(yA,yB,hyp_pts)
        xint = xx.astype(int)
        yint = yy.astype(int)
        angle = N.arctan((yy[-1]-yy[0])/(xx[-1]-xx[0])) # In radians

        # Get terrain heights
        terrain_z, heighthalf = self.get_height(xx,yy,self.W.z_dim,hyp_pts)
        
        # Set up plot
        # Length of x-section in km
        xs_len = (1/1000.0) * N.sqrt((-1.0*hyp_pts*self.W.dy*N.cos(angle))**2 +
                                    (hyp_pts*self.W.dy*N.sin(angle))**2)
        
        # Generate ticks along cross-section
        xticks = N.arange(0,xs_len,xs_len/hyp_pts)
        xlabels = [r"%3.0f" %t for t in xticks]
        grid = N.swapaxes(N.repeat(N.array(xticks).reshape(hyp_pts,1),self.W.z_dim,axis=1),0,1)

        # Plotting
        if nc.dx != nc.dy:
            print("Square domains only here")
        else:
            # TODO: define zmin, zmax, dz
            fig.axis([0,(hyp_pts*self.W.dx/1000.0)-1,zmin,zmax+dz])

        # Logic time
        # First, check to see if v is in the list of computable or default
        # variables within WRFOut (self.W)
        # If not, maybe it can be computed here.
        # If not, raise Exception.

        # TODO: vailable_vars in WRFOut to check this
        ps = {'t':tidx, 'la':yint, 'la':xint}
        
        if v in self.W.available_vrbls:
            data = self.W.get(v,ps)
        elif v is 'parawind':
            u = self.W.get('U',ps)
            v = self.W.get('V',ps)
            data = N.cos(angle)*u - N.sin(angle)*v
            clvs = u_wind_levels
            extends = 'both'
            CBlabel = r'Wind Speed (ms$^{-1}$)'

        elif v is 'perpwind':
            u = self.W.get('U',ps)
            v = self.W.get('V',ps)
            # Note the negative here. I think it's alright? TODO
            data = -N.cos(angle)*v + N.sin(angle)*u
            clvs = u_wind_levels
            extends = 'both'
            CBlabel = r'Wind Speed (ms$^{-1}$)'

        else:
            print("Unsupported variable",v)
            raise Exception

        fig.plot(xticks,terrain_z,color='k')
        fig.fill_between(xticks,terrain_z,0,facecolor='lightgrey')

        # What is this? TODO
        labeldelta = 15

        fig.set_yticks(N.arange(zmin,zmax+dz,dz))
        fig.set_xlabel("Distance along cross-section (km)")
        fig.set_ylabel("Height above sea level (m)")

        fpath = self.get_fpath()
        fname = self.get_fname()
        self.save(fig,fpath,fname)
        plt.close()

        # Save a colorbar
        # Only if one doesn't exist
        self.just_one_colorbar()

    def just_one_colorbar(self,fpath):
        """docstring for just_one_colorbar"""
        try:
            with open(fpath): pass
        except IOError:
            self.create_colorbar(fpath)

    
