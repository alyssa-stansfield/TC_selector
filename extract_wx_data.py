import numpy as np
import xarray as xr
import pandas as pd
import Ngl
import cartopy.geodesic
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import shapely

track_file = "hurdat_full_202007.nc" #input file: HURDAT file with all storms in N. Atlantic basin - downloaded in July of 2020
DS1 = xr.open_dataset(track_file, decode_times=False)
clons = DS1.clon.values
clats = DS1.clat.values
vmax = DS1.wind.values
MSLP = DS1.pres.values
dates = DS1.dates.values
hours = DS1.hours.values
DS1.close()

nstorms = len(clons[:,0]) #total number of storms in the HURDAT dataset
ntimes = len(clons[0,:]) #number of timesteps per storm

#convert dates and hours arrays into arrays of strings
dates_str = dates.astype(str)
hours_str = hours.astype(str)

#function for vectorizing the slicing of strings in an array
def slicer(start=None, stop=None, step=1):
    return np.vectorize(lambda x: x[start:stop:step], otypes=[str])

#extract the years, months, dates, and hours into separate arrays
hurdat_years = slicer(0,4)(dates_str)
hurdat_months = slicer(4,6)(dates_str)
hurdat_days = slicer(6,8)(dates_str)
hurdat_hours = slicer(0,2)(hours_str)

#fix the formatting of some of the hour elements
hurdat_hours[hurdat_hours=="60"] = "06"
hurdat_hours[hurdat_hours=="0."] = "00"



#wx station data - one csv file for now
fields = ["Station_ID", "Date_Time", "wind_speed_set_1", "wind_gust_set_1", "precip_accum_set_1"] #specify the data columns that we need
df_raw = pd.read_csv("CSAP4_RAWS.csv", usecols=fields) #read in the datafile, but only the fields specified above
df = df_raw.drop(df_raw.index[0])#drop row below column headers that contains the units

#station name - for output file
station_name = df["Station_ID"].iloc[0]

#date/time data
station_years = pd.DatetimeIndex(df['Date_Time']).year.to_numpy()
station_months = pd.DatetimeIndex(df['Date_Time']).month.to_numpy()
station_days = pd.DatetimeIndex(df['Date_Time']).day.to_numpy()
station_hours = pd.DatetimeIndex(df['Date_Time']).hour.to_numpy()

#meteorological data
wind_speed = df["wind_speed_set_1"].to_numpy(dtype="float32") #units = m/s
wind_gust = df["wind_gust_set_1"].to_numpy(dtype="float32") #units = m/s
cprecip = df["precip_accum_set_1"].to_numpy(dtype="float32") #units = mm, cumulative precip
precip = np.diff(cprecip) #calculate hourly precip from cumulative precip


#defining the circle polygon
lat = 18.20 #centered on PR for now
lon = -66.66
radius_in_meters = 500000 #size of circle in meters
n_points = 360
resolution = '50m'

circle_points = cartopy.geodesic.Geodesic().circle(lon=lon, lat=lat, radius=radius_in_meters, n_samples=n_points, endpoint=False)
circle_array = np.asarray(circle_points)
#create circle and extract circle latitude and longitudes into separate arrays
circle_lats = circle_array[:,1]
circle_lons = circle_array[:,0]


#create empty arrays for holding storms indices within circle
storm_in_range = []
times_in_range = []

for i in range(nstorms): #loop through storms
    tmp = []
    for j in range(ntimes): #loop through times
        if Ngl.gc_inout(clats[i,j], clons[i,j], circle_lats, circle_lons) == 1: #if track crosses inside circle
            storm_in_range.append(i) #append the storm index to list
            tmp.append(j) #append the time indices when the storm is within the circle
    times_in_range.append(tmp)
            

storms = np.unique(storm_in_range) #get rid of repeating storms
print (len(storms))


for m in storms:
    #track_lats = clats[m,:]
    #track_lons = clons[m,:]
    #lats_nonans = track_lats[~np.isnan(track_lats)]
    #lons_nonans = track_lons[~np.isnan(track_lons)]
    storm_times = times_in_range[m]
    storm_year = hurdat_years[m,storm_times]
    storm_month = hurdat_months[m,storm_times]
    storm_day = hurdat_days[m,storm_times]
    storm_hour = hurdat_hours[m,storm_times]
    for n in range(len(storm_times)): #for each time that this storm was within circle, extract wind and precip data
        storm_idx = np.where((station_years == float(storm_year[n])) & (station_months==float(storm_month[n])) & (station_days == float(storm_day[n])) & (station_hours==float(storm_hour[n])))[0]
        if np.isfinite(storm_idx) == True:
            print (wind_gust[storm_idx][0])
            print (precip[storm_idx][0])
