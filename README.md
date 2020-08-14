# TC_selector
Project with Anna, identifying TCs in historical dataset that passed near Puerto Rico and storing their info. as well as data from weather stations in Puerto Rico.

Uses the National Hurricane Center's HURDAT dataset (https://www.nhc.noaa.gov/data/) for 1851-2019. Data downloaded on 7-21-2020 as text file. Used python to convert it to a NetCDF file. 

plot_TCtracks_boxonly.py: Uses numpy, Cartopy, Matplotlib, Ngl, and Shapely python packages. Circle of specified radius is plotted centered at specified point. At this point, we are focusing on Puerto Rico so the circle centers on PR. The tracks of all tropical cyclones (no intensity restrictions) that pass within the circle at any point in their lifetimes are plotted as well. 

The 2 .png files show results for a 200km and 500km circle centered on PR. The number of tracks that are plotted is displayed in the title as "n". 

extract_wx_data.py: Uses numpy, pandas, Cartopy, Matplotlib, Ngl, and Shapely python packages. Reads in HURDAT data and weather station data (RAWS or NWS). Identifies TCs that passed within a specified circle around Puerto Rico and extracts wind and precipitation data from the wx station from those times when TC was close. Only works with 1 station data file for now.

The 2 CSV files are Puerto Rico weather station data from the RAWS dataset. 
