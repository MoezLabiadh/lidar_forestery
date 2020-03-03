This directory has the following two scripts:
*********************
1. export_lidar_data.py
*********************
This script takes an AOI and finds all available orthophotos and LAZ tiles associated with
acquired LiDAR. Files will be copied to a specified workspace. A text file
with the number of tiles intersected for each field team and the filepath to
each tile will also be created in this same directory.
Script will take awhile to run if extensive AOI coverage.
If file directories or field names changed, script will need to be updated.

*********************
2. lidar_products_script.py
*********************
This script transforms LIDAR raw point clouds into forestery derived products, namely terrain and canopy models (DEM, Slope, Canopy height, Canopy density). 
