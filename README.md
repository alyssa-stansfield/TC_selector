# TC_selector
Project with Anna, identifying TCs near Puerto Rico and storing their info

Uses the National Hurricane Center's HURDAT dataset (https://www.nhc.noaa.gov/data/) for 1851-2019. Data downloaded on 7-21-2020 as text file. Used python to convert it to a NetCDF file. 

plot_TCtracks_boxonly.py: Uses Cartopy, Matplotlib, and Shapely python packages. Circle of specified radius is plotted centered at specified point. At this point, we are focusing on Puerto Rico so the circle centers on PR. The tracks of all tropical cyclones (no intensity restrictions) that pass within the circle at any point in their lifetimes are plotted as well. 

The 2 .png files show results for a 200km and 500km circle centered on PR. The number of tracks that are plotted is displayed in the title as "n". 
