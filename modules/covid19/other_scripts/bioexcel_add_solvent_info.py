import requests
import math
import urllib
import os
import mdtraj as md

from covid19.models import *
from modules.dynadb.models import DyndbFileTypes



allprojects=requests.get('https://bioexcel-cv19.bsc.es/api/rest/v1/projects').json()

num_proj=allprojects["totalCount"]

solvent_types_d={val:sid for sid,val in CovidDynamics.solvent_types}


i=2 #The 1st ID is 2, for some reason
while i <= num_proj+1:
    projid_base="MCV1900000"
    projid= projid_base[:- len(str(i))] + str(i)
    proj_query=requests.get('https://bioexcel-cv19.bsc.es/api/rest/v1/projects/%s' % projid)
    if proj_query:
        this_proj=proj_query.json()
        if this_proj["published"]:
            print("ID: ",projid)
            dbdynli=CovidDynamics.objects.filter(extracted_from_db="BioExcel",extracted_from_db_entry=projid)
            if dbdynli:
                dbdyn=dbdynli[0]

                proj_meta=this_proj['metadata']
                wat_model=proj_meta["WAT"]
                db_wat_model=solvent_types_d["None"]
                if wat_model:
                    wat_model=wat_model.upper()
                    if wat_model in solvent_types_d:
                        db_wat_model=solvent_types_d[wat_model]
                    else:
                        if wat_model=="CHARMM TIP3P":
                            db_wat_model=solvent_types_d["TIP3P"]
                        else:
                            print("Unknown water model for %s : %s"%(projid,wat_model))
                            db_wat_model=solvent_types_d["Other"]
                    water_is_filtered=True
                    if proj_meta["SOL"]:
                        water_is_filtered=False
                else:
                    db_wat_model=solvent_types_d["None"]
                    water_is_filtered=False
                dbdyn.solvent_type=db_wat_model
                dbdyn.solvent_is_filtered=water_is_filtered
                dbdyn.save()

    i+=1
# check if any BioExcel simulation is still Unknown
nosolventdata=CovidDynamics.objects.filter(extracted_from_db="BioExcel",solvent_type=solvent_types_d["Unknown"])
for dyn in nosolventdata:
    dyn.solvent_type=solvent_types_d["None"]
    dyn.save()