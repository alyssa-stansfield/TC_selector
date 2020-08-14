import numpy as np
import xarray as xr
import Ngl
import cartopy.geodesic
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import shapely

track_file = "hurdat_full_202007.nc" #input file: IBTrACS file with all storms in N. Atlantic basin
DS1 = xr.open_dataset(track_file, decode_times=False)
clons = DS1.clon.values
clats = DS1.clat.values
vmax = DS1.wind.values
MSLP = DS1.pres.values
time = DS1.time.values

nstorms = len(clons[:,0])
ntimes = len(clons[0,:])


#defining the circle polygon
lat = 18.20
lon = -66.66
radius_in_meters = 200000
n_points = 360
resolution = '50m'

circle_points = cartopy.geodesic.Geodesic().circle(lon=lon, lat=lat, radius=radius_in_meters, n_samples=n_points, endpoint=False)
circle_array = np.asarray(circle_points)
circle_lats = circle_array[:,1]
circle_lons = circle_array[:,0]


# Define the projection used to display the circle:
proj = ccrs.Orthographic(central_longitude=lon, central_latitude=lat)
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, projection=proj)
ax.set_extent([lon-20, lon+20, lat-10, lat+10])
ax.imshow(np.tile(np.array([[cfeature.COLORS['water'] * 255]], dtype=np.uint8), [2, 2, 1]), origin='upper', transform=ccrs.PlateCarree(), extent=[-180, 180, -180, 180])
ax.add_feature(cfeature.NaturalEarthFeature('physical', 'land', resolution, edgecolor='black', facecolor=cfeature.COLORS['land']))
ax.add_feature(cfeature.NaturalEarthFeature('cultural', 'admin_0_countries', resolution, edgecolor='black', facecolor='none'))
geom = shapely.geometry.Polygon(circle_points)
ax.add_geometries((geom,), crs=cartopy.crs.PlateCarree(), facecolor='red', edgecolor='none', linewidth=0, alpha=0.3)

storm_in_range = []
for i in range(nstorms):
    for j in range(ntimes):
        if Ngl.gc_inout(clats[i,j], clons[i,j], circle_lats, circle_lons) == 1: #if track crosses inside circle
            storm_in_range.append(i)

storms = np.unique(storm_in_range)
print (len(storms))
for m in storms:
    track_lats = clats[m,:]
    track_lons = clons[m,:]
    lats_nonans = track_lats[~np.isnan(track_lats)]
    lons_nonans = track_lons[~np.isnan(track_lons)]
    #plt.plot(lons_nonans,lats_nonans,linestyle='--',linewidth=0.5,color="blue",transform=ccrs.PlateCarree(),)

plt.title(str(int(radius_in_meters)/1000) + "km circle, n = " + str(len(storms)))
fig.tight_layout()
plt.savefig('200kmcircle_with_tracks.png')
