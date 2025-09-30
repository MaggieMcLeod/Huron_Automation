# -*- coding: utf-8 -*-

# Name:               Huron_Automation_Tool
# Date Last Modified: 09/30/2025
# Authors:            Kendahl Hejl, Maggie McLeod, Dr. Cary Troy
# Description:        ArcGIS Python toolbox (.pyt) that implements shoreline detection algorithm on a set of images,
#                     mosaics the shorelines together, and outputs a complete shp file shoreline.

import arcpy
from pathlib import Path
import time
start_time = time.time()


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [Automate_Shoreline]


class Automate_Shoreline:
    " Tool is the main automation code. "
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Automate Shoreline"
        self.description = "Implements shoreline detection algorithm on a set of images, mosaics the shorelines together, and outputs a complete shp file shoreline."

    def getParameterInfo(self):
        """Define the tool parameters."""
        shoreline_toolbox = arcpy.Parameter(name="shoreline_toolbox",
                                            displayName="Shoreline Detection Toolbox File",
                                            direction="Input",
                                            datatype="DEFile",
                                            parameterType="Required")
        
        Test_Code_Data = arcpy.Parameter(name="Test_Code_Data",
                                    displayName="Input Image Data",
                                    direction="Input",
                                    datatype="DEFolder",
                                    parameterType="Required")
        
        counter = arcpy.Parameter(name="counter",
                            displayName="Counter (Prevent overwriting folders)",
                            direction="Input",
                            datatype="String",
                            parameterType="Optional")
    
        
        params = [shoreline_toolbox, Test_Code_Data, counter]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        # Collect and display input parameters
        shoreline_toolbox = parameters[0].valueAsText
        Test_Code_Data = parameters[1].valueAsText
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        project_path = r'{}'.format(aprx.filePath[0:-5])
        project_name = project_path.split("\\")[-1]
        counter = parameters[2].valueAsText

        arcpy.AddMessage(f"Shoreline Toolbox Path: {shoreline_toolbox}")
        arcpy.AddMessage(f"Input Image Data: {Test_Code_Data}")
        arcpy.AddMessage(f"Project Path: {project_path}")
        arcpy.AddMessage(f"Project Name: {project_name}")
        arcpy.AddMessage(f"Counter: {counter}")

        # make intermediate output folders
        delete_char = len(project_name)
        shorelines_location = project_path[0:-delete_char] + r"\Output_Shorelines" + str(counter)
        mosaics_location = project_path[0:-delete_char] + r"\Output_Mosaics" + str(counter)
        Path(shorelines_location).mkdir()
        Path(mosaics_location).mkdir()

        # import shoreline detection toolbox
        arcpy.ImportToolbox(shoreline_toolbox)
        arcpy.env.workspace = Test_Code_Data

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
                arcpy.AddMessage(f"iterated {count} time(s), currently on raster {name}.")

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
                    arcpy.AddMessage(f"Shoreline_detection failed on {name} file")

                arcpy.AddMessage("Shoreline detection complete")
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

            arcpy.AddMessage("mosaic process starting")
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
            shoreline_filepath = f"{project_path[0:-delete_char]}\{project_name}.gdb\code_shoreline{str(counter)}"


            # CONVERT MOSAIC INTO COMPLETE SHORELINE SHP FILE

            # raster to polyline
            arcpy.AddMessage("raster to polyline starting")
            arcpy.conversion.RasterToPolyline(
                in_raster= mosaics_location + "\code_mosaic" + str(counter) + ".tif",
                out_polyline_features= shoreline_filepath,
                background_value="ZERO",
                minimum_dangle_length=0,
                simplify="SIMPLIFY",
                raster_field="Value"
        )

            # clean dangles
            arcpy.AddMessage("clean dangles starting")
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
            return


        Model()
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
