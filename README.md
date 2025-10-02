# Huron_Automation
Script (.py) and ArcGIS Python Toolbox (.pyt) that implements a shoreline detection algorithm (Abdelhady 2022) on a set of images, mosaics the shorelines together, and outputs a complete shp file shoreline. Completed with the Troy Lab at Purdue University.

To use **Huron_Automation_Script.py**, open the script in an IDE. Edit the following five lines of code:
```
"# TYPE LOCAL PATH FOR SHORELINE DETECTION TOOLBOX (Abdelhady 2022) HERE"
shoreline_toolbox = r"C:\Users\your_path\ShorelineDetection.atbx"

"# TYPE PATH FOR INPUT TESTING DATA HERE"
Test_Code_Data = r"C:\Users\your_path\imagery_folder"

"# TYPE ARCGIS PROJECT PATH HERE"
project_path = r"C:\your_path\your_ArcGIS_project"

"# TYPE PROJECT NAME HERE#
project_name = "your_ArcGIS_project"

"# TYPE COUNTER NUMBER HERE to avoid file overwriting"
counter = 0
```

To use **Huron_Automation_Tool.pyt**, open a project in ArcGIS Pro. Click "Add Python Toolbox," and paste the .pyt script inside. To run the tool, double-click the Automation_Huron script, and input the following parameters:

IN-PROGRESS

Will add pictures here to make instructions more clear.
