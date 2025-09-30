# Name:               Lake Huron Automation
# Date Last Modified: 09/17/2025
# Authors:            Kendahl Hejl, Maggie McLeod, Dr. Cary Troy
# Description:        Script that implements shoreline detection algorithm on a set of images, mosaics the shorelines together,
#                     and outputs a complete shp file shoreline.

import arcpy
from pathlib import Path
import time
start_time = time.time()

# TYPE LOCAL PATH FOR SHORELINE DETECTION TOOLBOX HERE
shoreline_toolbox = r"C:\Users\maggi\Documents\ArcGIS\Shoreline_detection\Shoreline_detection\ShorelineDetection.atbx"

# TYPE PATH FOR INPUT TESTING DATA HERE
Test_Code_Data = r"C:\Users\maggi\Documents\ArcGIS\delete_Shoreline_Data\Planet\Huron\2021\Mosaic_Testing"

# TYPE ARCGIS PROJECT PATH HERE
project_path = r"C:\Users\maggi\Documents\ArcGIS\Projects\Huron_Automation_Testing"

# TYPE PROJECT NAME HERE
project_name = "Huron_Automation_Testing"

# TYPE COUNTER NUMBER HERE to avoid file overwriting
counter = 0


# make intermediate output folders
shorelines_location = project_path + r"\Output_Shorelines" + str(counter)
mosaics_location = project_path + r"\Output_Mosaics" + str(counter)
Path(shorelines_location).mkdir()
Path(mosaics_location).mkdir()

arcpy.ImportToolbox(shoreline_toolbox)
arcpy.env.workspace = Test_Code_Data
# arcpy.env.overwriteOutput = True

def path_to_name(path):
    '''
    Extracts image name from path.
    '''
    raw_string = r'{}'.format(path)
    x = raw_string.split("\\")                 
    end = x[-1]
    y = end.split(".")
    return(y[0])

def Model():
    '''
    Main code goes in this function.
    '''
    # COLLECT AND PREPARE RASTERS FOR SHORELINE DETECTION

    # makes a path object for data folder and recursively searches data folder
    rasters_path_object = Path(Test_Code_Data)
    searched_rasters = rasters_path_object.rglob('*.tif')

    # make list of all rasters to use in the algorithm
    rasters_list = []
    for file in searched_rasters:

        # do not include udm tifs
        name = path_to_name(str(file))
        if "udm" not in name:
            rasters_list.append(file)


    # SHORELINE DETECTION
    # outputs one shoreline shp and one shoreline tif for each input image

    # iterate over rasters
    count = 0
    for raster in rasters_list:
        name = path_to_name(str(raster))
        print(f"iterated {count} time(s), currently on raster {name}.")

        try:
            # shoreline detection toolbox
            arcpy.ShorelineDetection.ShorelineDetection(
            InputSatelliteImage=str(raster),
            OutputLocation=shorelines_location,
            OutputFile=f"shore_{name}",
            GreenBandNumber="2",
            NIRBandNumber="4"
        )
            
        except:
            print(f"Shoreline_detection failed on {name} file")

        print("Shoreline detection complete")
        count += 1


    # PREPARE SHORELINE TIFS FOR MOSAIC

    # make a path object for shoreline output folder
    shores_path_object = Path(shorelines_location)

    # recursively search shoreline output folder for tifs
    searched_shores = shores_path_object.rglob('shore_*.tif')

    # make list and string of all shoreline rasters to use in the mosaic
    shores_list = []
    shores_string = ""
    first_iteration = True
    for file in searched_shores:
        shores_list.append(file)
        if first_iteration == True:
            shores_string = str(file)
        else:
            shores_string = shores_string + ";" + str(file)
        first_iteration = False


    # MOSAIC SHORELINE TIFS

    print("mosaic process starting")
    arcpy.management.MosaicToNewRaster(
        input_rasters=shores_string,
        output_location= mosaics_location,
        raster_dataset_name_with_extension="code_mosaic" + str(counter) + ".tif",
        coordinate_system_for_the_raster='PROJCS["WGS_1984_UTM_Zone_17N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-81.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]',
        pixel_type="32_BIT_SIGNED",
        cellsize="",
        number_of_bands=1,
        mosaic_method="MAXIMUM",
        mosaic_colormap_mode="FIRST"
    )

    # geodatabase filepath (for shoreline shp file)
    shoreline_filepath = f"{project_path}\{project_name}.gdb\code_shoreline{str(counter)}"


    # CONVERT MOSAIC INTO COMPLETE SHORELINE SHP FILE

    # raster to polyline
    print("raster to polyline starting")
    arcpy.conversion.RasterToPolyline(
        in_raster= mosaics_location + "\code_mosaic" + str(counter) + ".tif",
        out_polyline_features= shoreline_filepath,
        background_value="ZERO",
        minimum_dangle_length=0,
        simplify="SIMPLIFY",
        raster_field="Value"
   )

    # clean dangles
    print("clean dangles starting")
    arcpy.edit.TrimLine(
        in_features=shoreline_filepath,
        dangle_length="3 Meters",
        delete_shorts="DELETE_SHORT"
    )

    arcpy.edit.TrimLine(
        in_features=shoreline_filepath,
        dangle_length="6 Meters",
        delete_shorts="DELETE_SHORT"
    )

    arcpy.edit.TrimLine(
        in_features=shoreline_filepath,
        dangle_length="9 Meters",
        delete_shorts="DELETE_SHORT"
    )

if __name__ == '__main__':
    # Global Environment settings
    #with arcpy.EnvManager(scratchWorkspace="C:\\Users\\maggi\\Documents\\ArcGIS\\Projects\\Test_Code\\Test_Code.gdb", workspace=Test_Code_Data):
    with arcpy.EnvManager(workspace=Test_Code_Data):
        Model()

        print("Process finished --- %s seconds ---" % (time.time() - start_time))
