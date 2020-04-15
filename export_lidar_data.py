'''
This script takes an AOI and finds all available orthophotos and LAZ tiles associated with
acquired LiDAR. Files will be copied to a specified workspace. A text file
with the number of tiles intersected for each field team and the filepath to
each tile will also be created in this same directory.

Script will take awhile to run if extensive AOI coverage.

If file directories or field names changed, script will need to be updated.

'''

import arcpy, shutil, os, sys
from arcpy import env

# Define Local variables
AOI = sys.argv[1]

# Define workspace
workspace = sys.argv[2]
env.workspace = workspace
env.overwriteOutput = True

imagery_location = r"\\....."
FTKL_utm_imagery_tiles = imagery_location + r"\FTKL\FTKL_Imagery_Products.gdb\FTKL_utm_imagery_tiles"
FTBO_utm_imagery_tiles = imagery_location + r"\FTBO\FTBO_Imagery_Products.gdb\FTBO_utm_imagery_tiles"
FTAR_utm_imagery_tiles = imagery_location + r"\FTAR\FTAR_Imagery_Products.gdb\FTAR_utm_imagery_tiles"
FTEK_utm_imagery_tiles = imagery_location + r"\FTEK\FTEK_Imagery_Products.gdb\FTEK_utm_imagery_tiles"
field_team_lyr = "field_team_lyr"

LAZTiles = r"\\....\LAZ_tiles.shp"
LAZTiles_lyr = "LAZTiles_lyr"
fields = ['filepath' , 'file_name']

# Make list of 4 field teams' imagery tiles
imagery_tiles_TKO = [FTKL_utm_imagery_tiles, FTBO_utm_imagery_tiles, FTAR_utm_imagery_tiles, FTEK_utm_imagery_tiles]

# Create text file to document intersected tiles
txtfile = open("{}\Imagery_List.txt".format(workspace), "w+")
#print ("Created text file")
txtfile.write("The AOI covers the following areas:")
txtfile.write("\n")

#Process: Select Layer By Location
#Determine which imagery tiles intersect with AOI
##print ("Selecting tiles based on AOI location, adding to text list and exporting to workspace")
for field_team in imagery_tiles_TKO:

 # Clear field_team_lyr
 if arcpy.Exists(field_team_lyr):
  arcpy.Delete_management(field_team_lyr)

 # Make feature layer and select by location witH AOI
 arcpy.MakeFeatureLayer_management(field_team, field_team_lyr)
 arcpy.SelectLayerByLocation_management(field_team_lyr, "INTERSECT", AOI, "", "NEW_SELECTION", "NOT_INVERT")

 # Count selected tiles for each field team
 # Write results to text file
 selected_rows = arcpy.GetCount_management(field_team_lyr)
 txtfile.write("\n")
 txtfile.write("{} intersected imagery tiles for {}...".format(selected_rows, field_team[-22:]))
 txtfile.write("\n")

 # Make list of selected features and copie files to workspace
 if selected_rows > 0:
  field = "location"
  with arcpy.da.SearchCursor(field_team_lyr, field) as cursor:
   for row in cursor:
    filepath = row[0].replace("Q:\Imagery", imagery_location)
    txtfile.write(filepath)
    txtfile.write("\n")
    shutil.copy(filepath, workspace)

# Delete temporary Layer file
arcpy.Delete_management(field_team_lyr)

# TIF files are copied. Now the script will start copying LAS files (same process as above).
if arcpy.Exists(LAZTiles_lyr):
 arcpy.Delete_management(LAZTiles_lyr)
			
arcpy.MakeFeatureLayer_management(LAZTiles, LAZTiles_lyr)
arcpy.SelectLayerByLocation_management(LAZTiles_lyr, "INTERSECT", AOI, "", "NEW_SELECTION", "NOT_INVERT")					

selected_rows = arcpy.GetCount_management(LAZTiles_lyr)
txtfile.write("\n")
txtfile.write("{} intersected LAZ tiles...".format(selected_rows))
txtfile.write("\n")

with arcpy.da.SearchCursor(LAZTiles_lyr, fields) as cursor:
 for row in cursor:
  fileLAS = str(row[0]) + "\\" + str(row[1])
  txtfile.write(fileLAS)
  txtfile.write("\n")
  shutil.copy(fileLAS, workspace)
  
arcpy.Delete_management(LAZTiles_lyr)
txtfile.close()
