import numpy as np
import xarray as xr
import Ngl
from math import sin, cos, sqrt, atan2, radians


track_file = "/global/cscratch1/sd/alyssas/Basin.NA.ibtracs_all.v03r10.nc" #input file: IBTrACS file with all storms in N. Atlantic basin
DS1 = xr.open_dataset(track_file)
clons = DS1.lon_for_mapping.values
clats = DS1.lat_for_mapping.values
season = DS1.season.values
vmax = DS1.source_wind.values*0.514 #convert from knots to m/s
MSLP = DS1.source_pres.values
time = DS1.source_time.values
storm_type = DS1.nature_for_mapping.values #classification of storm type - 0 is tropical


nstorms = len(season)
ntimes = len(clons[0,:])
print (nstorms, ntimes)


#plotting
wks_type = 'png' #output file as .png
output_name = 'ibtracs_TCtracks_all'
wks = Ngl.open_wks(wks_type,output_name)
res = Ngl.Resources()
lineres = Ngl.Resources()

#turn off drawing for individual plots,since we will panel them later
res.nglDraw = False
res.nglFrame = False
panel_plots = []#list to hold indiviudal plots before paneling

#map details
res.mpDataSetName = "Earth..2"
res.mpDataBaseVersion = "MediumRes"
res.mpLimitMode = "Corners" #how you want to specify limits of map
res.mpLeftCornerLonF = float(-100) #Left Longitude Limit
res.mpRightCornerLonF = float(-25) #Right Longitude Limit
res.mpLeftCornerLatF = float(10) #Lower Latitude Limit
res.mpRightCornerLatF = float(45) #Upper Latitude Limit

res.mpAreaMaskingOn = True #turn masking on
res.mpFillOn = True
res.mpOceanFillColor = -1 #don't fill ocean
res.mpLandFillColor = "Tan" #land is transparent
res.mpInlandWaterFillColor = -1 
res.mpOutlineBoundarySets = "National"
#res.mpOutlineBoundarySets = "USStates" #turn on US State boundary lines
#res.mpUSStateLineThicknessF = 5#thicken US state boundary lines
res.mpPerimOn = True
res.mpGridAndLimbOn = False


linethicknesses = [2.0,4.0,5.2,7.6,9.2,10.4]

#res.tiMainFontHeightF = 0.015
#res.tiYAxisString = 'IBTrACS'
map1 = Ngl.map(wks,res)

actual_storm_count = 0
seasons_list = []
landfall_lats = []
landfall_lons = []
landfall_regions = []

maj_hurr_count = 0
for i in range(nstorms):
            #empty arrays for holding storm data, want to plot storm if makes landfall in US and not plot if it doesn't
            storm_lats = []
            storm_lons = []
            storm_winds = []
            for j in range(ntimes):
                    storm_lats.append(clats[i,j])
                    storm_lons.append(clons[i,j])
                    storm_winds.append(np.nanmax(vmax[i,j,:]))
                    #location of TC center of this storm at this time
                    thislat = clats[i,j]
                    thislon = clonsi,j]
                    if landfall == False: #if you haven't already found a point of landfall, try to find it for this storm
                            for k in range(NE_listlen):
                                    if Ngl.gc_inout(thislat, thislon, NE_shape_lats[k], NE_shape_lons[k]) != 0:
                                            print "TC makes landfall in Northeast"
                                            landfall = True #set landfall to True
                                            NE_landfalls += 1
                                            seasons_list.append(seasons_cut[i])
                                            landfall_lats.append(thislat)
                                            landfall_lons.append(thislon)
                                            landfall_regions.append("Northeast")

            if landfall == True:
                    #If storm does make landfall, plot it's track
                    for a in range(len(storm_lats)):
                            if np.isfinite(storm_winds[a]) == True:
                                    if storm_winds[a] < 17.:
                                            lineres.gsLineColor = "blue"
                                            lineres.gsLineThicknessF = linethicknesses[0]
                                    elif storm_winds[a] >= 17. and storm_winds[a] < 33.:
                                            lineres.gsLineColor = "green3"
                                            lineres.gsLineThicknessF = linethicknesses[1]
                                    elif storm_winds[a] >= 33. and storm_winds[a] < 43:
                                            lineres.gsLineColor = "yellow2"
                                            lineres.gsLineThicknessF = linethicknesses[2]
                                    elif storm_winds[a] >= 43 and storm_winds[a] < 49:
                                            lineres.gsLineColor = "orange"
                                            lineres.gsLineThicknessF = linethicknesses[3]
                                    elif storm_winds[a] >= 49 and storm_winds[a] < 58:
                                            lineres.gsLineColor = "darkorange3"
                                            lineres.gsLineThicknessF = linethicknesses[4]
                                    else:
                                            maj_hurr_count += 1
                                            lineres.gsLineColor = "red"
                                            lineres.gsLineThicknessF = linethicknesses[5]

                                    if j != 0:
                                            pline = Ngl.add_polyline(wks,map1,[storm_lons[a],storm_lons[a-1]],[storm_lats[a],storm_lats[a-1]],lineres)
panel_plots.append(map1)


#np.savetxt("ibtracs_landfallinfo.csv", np.column_stack((landfall_lats, landfall_lons, seasons_list, landfall_regions)),  fmt="%s", delimiter=",")

"""
lgres                    = Ngl.Resources()
lgres.lgAutoManage       = False
lgres.vpWidthF = 0.80
lgres.vpHeightF          = 0.12

lgres.lgOrientation = "Horizontal"

lgres.lgMonoItemType        = False                 #indicates that we wish to set the item types individually
lgres.lgMonoMarkerIndex     = False
lgres.lgMonoLineThickness   = False
lgres.lgMonoMarkerSize      = True

lgres.lgLabelFontHeightF      = 0.020
lgres.lgLabelConstantSpacingF = 0.0


lgres.lgItemCount        = 6
lgres.lgItemTypes        = ["Markers","Markers","Markers","Markers","Markers","Markers"]
lgres.lgMarkerIndexes    = [16,      16,      16,      16,      16,      16]
lgres.lgMarkerSizeF = 0.02
lgres.lgMarkerColors = ["blue", "green3", "yellow2", "orange", "darkorange3", "red"]
legend_labels = ["TD", "TS", "Cat 1", "Cat 2", "Cat 3", "Cat 4/5"]

legend = Ngl.legend_ndc(wks,lgres.lgItemCount,legend_labels,0.10,0.25,lgres)
"""


"""
#panel the plots and plot
panelres = Ngl.Resources()
panelres.nglPanelLabelBar = False
#panelres.nglPanelFigureStrings = ["IBTrACS"] #put label inside plot
panelres.nglPanelFigureStrings = ["Obs"]
panelres.nglPanelFigureStringsJust = "TopRight"
panelres.nglPanelFigureStringsFontHeightF = 0.025
Ngl.panel(wks,panel_plots[0:1],[1,1],panelres)
"""
Ngl.end()
