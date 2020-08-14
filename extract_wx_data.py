import numpy as np
import xarray as xr
import pandas as pd
import Ngl
import cartopy.geodesic
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import shapely
from itertools import repeat


#function for vectorizing the slicing of strings in an array
def slicer(start=None, stop=None, step=1):
    return np.vectorize(lambda x: x[start:stop:step], otypes=[str])

#function to flatten a list
def list_flat(a):
    return sum(a, [])



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


#extract the years, months, dates, and hours into separate arrays
hurdat_years = slicer(0,4)(dates_str)
hurdat_months = slicer(4,6)(dates_str)
hurdat_days = slicer(6,8)(dates_str)
hurdat_hours = slicer(0,2)(hours_str)

#fix the formatting of some of the hour elements
hurdat_hours[hurdat_hours=="0."] = "00"
hurdat_hours[hurdat_hours=="30"] = "03"
hurdat_hours[hurdat_hours=="40"] = "04"
hurdat_hours[hurdat_hours=="50"] = "05"
hurdat_hours[hurdat_hours=="60"] = "06"
hurdat_hours[hurdat_hours=="70"] = "07"
hurdat_hours[hurdat_hours=="80"] = "08"
hurdat_hours[hurdat_hours=="90"] = "09"




#wx station data - one csv file for now
fields = ["Station_ID", "Date_Time", "wind_speed_set_1", "wind_gust_set_1", "precip_accum_set_1"] #specify the data columns that we need
df_raw = pd.read_csv("CSAP4_RAWS.csv", usecols=fields, skiprows=10) #read in the datafile, but only the fields specified above and skip the header info in the first 10 rows
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

out_precip = []
out_wind = []
out_gusts = []
out_years = []
out_months = []
out_days = []
out_hours = []
out_stations = []


for m in storms:
    storm_times = times_in_range[m]
    storm_year = hurdat_years[m,storm_times]
    storm_month = hurdat_months[m,storm_times]
    storm_day = hurdat_days[m,storm_times]
    storm_hour = hurdat_hours[m,storm_times]

    for n in range(len(storm_times)): #for each time that this storm was within circle, extract wind and precip data
        storm_idx = np.where((station_years == float(storm_year[n])) & (station_months==float(storm_month[n])) & (station_days == float(storm_day[n])) & (station_hours==float(storm_hour[n])))[0] #match up date/times between the 2 HURDAT and wx station datasets
        if np.isfinite(storm_idx) == True:
            if n!= 0:
                storm_idx_prev = np.where((station_years == float(storm_year[n-1])) & (station_months==float(storm_month[n-1])) & (station_days == float(storm_day[n-1])) & (station_hours==float(storm_hour[n-1])))[0]
                out_precip.append(list(precip[storm_idx_prev[0]:storm_idx[0]]))
                out_wind.append(list(wind_speed[storm_idx_prev[0]:storm_idx[0]]))
                out_gusts.append(list(wind_gust[storm_idx_prev[0]:storm_idx[0]]))
                #out_stations.append(station_name*len(wind_gust[storm_idx_prev[0]:storm_idx[0]]))
                out_years.append(list(station_years[storm_idx_prev[0]:storm_idx[0]]))
                out_months.append(list(station_months[storm_idx_prev[0]:storm_idx[0]]))
                out_days.append(list(station_days[storm_idx_prev[0]:storm_idx[0]]))
                out_hours.append(list(station_hours[storm_idx_prev[0]:storm_idx[0]]))

list_len = len(list_flat(out_wind))
out_stations = [station_name] * list_len
print (np.shape(out_stations), np.shape(list_flat(out_wind)))

#writing output file using pandas
out_dict = {'station':out_stations, 'year':list_flat(out_years), 'month':list_flat(out_months), 'day':list_flat(out_days), 'hour':list_flat(out_hours), 'precip':list_flat(out_precip), 'wind_speed':list_flat(out_wind), 'wind_gust':list_flat(out_gusts)}
df_out = pd.DataFrame(out_dict, columns=['station','year','month','day','hour','precip','wind_speed','wind_gust'])
df_out.to_csv('output_test.csv')
