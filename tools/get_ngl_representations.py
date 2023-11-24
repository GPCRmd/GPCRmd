#Script to generate all the representations and shapes from pickle of Adrian Morales

# Imports
import pandas as pd
import glob
import os
 
# Get data
path = "/GPCRmd/media/files/Figures/ACN/*pickle"
files = glob.glob(path)

# Create file to store statements

# Read data
for f in files: 
    with open(f"ngl_statements_{os.path.basename(f)}.txt", "w") as file_in: 
        info_pick = pd.read_pickle(f)
        for ind, val in enumerate(info_pick["state"]["_ngl_msg_archive"]):
            method = val["methodName"]
            if "add" in method: #['addRepresentation', 'addShape']
                if "Rep" in method: #o.addRepresentation( "cartoon", {sele: "1-999", color: "white"} ); 
                    style = str(val["args"][0])
                    sele = str(val["kwargs"]["sele"])
                    color = str(val["kwargs"]["color"])
                    file_in.write('o.addRepresentation( "' +
                                        style + '", {sele: "' +
                                        sele + '", color: "' +
                                        color + '"} ); \n')
                elif "Sha" in method: #shape.addCylinder([ 0, 2, 7 ], [ 0, 0, 9 ], [ 1, 1, 0 ], 0.5);
                    pos1 = str(val["args"][1][0][1])
                    pos2 = str(val["args"][1][0][2])
                    color = str(val["args"][1][0][3])
                    radius = str(val["args"][1][0][4])
                    file_in.write('shape.addCylinder(' +
                                        pos1 + ',' +
                                        pos2 + ',' +
                                        color.replace("(", "[").replace(")", "]") + ',' +
                                        radius + '); \n')