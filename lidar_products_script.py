#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      MLABIADH
#
# Created:     31/01/2020
# Copyright:   (c) MLABIADH 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy
from arcpy import env
from arcpy.sa import*

arcpy.env.overwriteOutput = True

# Set script variables

inputLAS = r'\\bctsdata.bcgov\data\tko_root\GIS_WORKSPACE\MLABIADH\LIDAR\lidar-products-workflow\script\test\inputLAS'
spatialRef = arcpy.SpatialReference(3005) # ESPG Code for NAD83 / BC Albers

MainWorkspace = r'\\bctsdata.bcgov\data\tko_root\GIS_WORKSPACE\MLABIADH\LIDAR\lidar-products-workflow\script\outputs'
#ScratchWorkspace = r'\\bctsdata.bcgov\data\tko_root\GIS_WORKSPACE\MLABIADH\LIDAR\lidar-products-workflow\script\outputs\ScratchWorkspace.gdb'
FinalGDB = r'\\bctsdata.bcgov\data\tko_root\GIS_WORKSPACE\MLABIADH\LIDAR\lidar-products-workflow\script\outputs\FinalOutputs.gdb'

# Check if Spatial Analysis extension is available and activate it.

if arcpy.CheckExtension("Spatial") == "Available":
  arcpy.CheckOutExtension("Spatial")

# Create a LAS dataset

env.workspace = MainWorkspace
arcpy.management.CreateLasDataset(inputLAS, 'lasDataset.lasd', "RECURSION", "",
                                  spatialRef, "COMPUTE_STATS")
print ("lAS Dataset created")

# Extract seperate LAS dataset and raster layers for Ground Returns and Canopy Returns.

ground_returns = r'in_memory\ground_returns'
canopy_returns = r'in_memory\canopy_returns'

arcpy.MakeLasDatasetLayer_management('lasDataset.lasd', ground_returns,
                                     2, 'Last Return', 'INCLUDE_UNFLAGGED',
                                     'EXCLUDE_SYNTHETIC', 'INCLUDE_KEYPOINT',
                                     'EXCLUDE_WITHHELD')

arcpy.MakeLasDatasetLayer_management('lasDataset.lasd', canopy_returns,
                                     '', ['First of Many', 1], 'INCLUDE_UNFLAGGED',
                                     'EXCLUDE_SYNTHETIC', 'INCLUDE_KEYPOINT',
                                     'EXCLUDE_WITHHELD')
env.workspace = FinalGDB
arcpy.conversion.LasDatasetToRaster(ground_returns, "DEM", 'ELEVATION',
                          'BINNING AVERAGE NATURAL_NEIGHBOR', 'FLOAT',
                          'CELLSIZE', '1', '1')

arcpy.conversion.LasDatasetToRaster(canopy_returns, "DSM", 'ELEVATION',
                          'BINNING AVERAGE NATURAL_NEIGHBOR', 'FLOAT',
                          'CELLSIZE', '1', '1')
print ("DEM and DSM created")

# Create DEM derived products: slope, hillshade and Canopy Height model (CHM).

outSlope = Slope("DEM", "DEGREE", 1)
outSlope.save("SLOPE")

outHillshade = Hillshade("DEM", 315, 45, "NO_SHADOWS", 1)
outHillshade.save("HILLSHADE")

outMinus = Minus("DSM", "DEM")
outMinus.save("CHM")

print ("Slope, Hillshade and CHM created")

# Create the Canopy Density model (CDM).
   #Calculate per cell stats for ground and canopy returns
groundStats = r'in_memory\groundStats'
canopyStats = r'in_memory\canopyStats'

arcpy.management.LasPointStatsAsRaster(ground_returns, groundStats,
                                       "POINT_COUNT", "CELLSIZE", 4)
arcpy.management.LasPointStatsAsRaster(canopy_returns, canopyStats,
                                       "POINT_COUNT", "CELLSIZE", 4)

  #Covnvert No-data values to zero
groundStats_convNodata = r'in_memory\groundStats_convNodata'
canopyStats_convNodata = r'in_memory\gcanopyStats_convNodata'

outCon = Con(IsNull(groundStats),0, groundStats)
outCon.save(groundStats_convNodata)

outCon = Con(IsNull(canopyStats),0, canopyStats)
outCon.save(canopyStats_convNodata)

  #Calculate a Total count raster (canopy + ground)
totalCount = r'in_memory\totalCount'
outPlus = Plus(groundStats_convNodata, canopyStats_convNodata)
outPlus.save(totalCount)

  #Convert totalCount to Float
totalCountFloat = r'in_memory\totalCountFloat'
outFloat = Float(totalCount)
outFloat.save(totalCountFloat)

  #Calculate CDM (divide canopy count stats by the total count)
CDM_noData = r'in_memory\CDM_noData'
outDivide = Divide(canopyStats_convNodata, totalCountFloat)
outDivide.save(CDM_noData)

  #Fill No_data cells by interpolating neigboring cells and create a final CDM output
outCon2 = Con(IsNull(CDM_noData), FocalStatistics(CDM_noData, NbrRectangle(3, 3, "CELL"), "MEAN", "DATA"), CDM_noData)
outCon2.save("CDM")

print ("CDM created")

# Delete intermediate products
arcpy.Delete_management("in_memory")

print ("Intermediate data deleted")
