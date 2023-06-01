from django.core.management.base import BaseCommand, CommandError
import os
import re
import json
from django.conf import settings

def fp_dict(path):
    json_file=open(path)
    json_str = json_file.read()
    json_data = json.loads(json_str)
    return json_data

def get_cont_type(self,jsonfile,n1,n2):
    if(len(n1.split("x")) != 2):
        self.stdout.write(self.style.ERROR("GPCR num %s not understood in %s." % (n1 , jsonfile)))
        return False
    chain1=n1.split("x")[0]
    chain2=n2.split("x")[0]
    if (chain1==chain2):
        group="1"
        info="Intra"
    else:
        group="2"
        info="Inter"
    return (info)

def addContTypetoEdges(self,jsonfile,myfp):
    cont_li=myfp["edges"];
    for cont_info in cont_li:
        n1=cont_info["name1"]
        n2=cont_info["name2"]
        (info)=get_cont_type(self,jsonfile,n1,n2)
        if (info):
            cont_info["helixpos"]=info
        else:
            break

class Command(BaseCommand):
    help = "Add information at the JSON files of the Flare Plots"
    def add_arguments(self, parser):
        parser.add_argument(
            "-type",
            dest="info_type",
            nargs="*",
            choices=["helixpos"], #Add more options if I want to add other types of info tot he FP
            action="store",
            default="helixpos",
            help="Type of information to be added to the flare plot."
        )

        parser.add_argument(
           '-dyn',
            dest='dyn_id',
            nargs='*',
            action='store',
            default=False,
            help='Specify id(s) of dynamics for which a json file will be modified'
        )

    def handle(self, *args, **options):
        hb_json_path=settings.MEDIA_ROOT + "Precomputed/flare_plot/hbonds"
        if not os.path.isdir(hb_json_path):
            self.stdout.write(self.style.ERROR("No json files found."))
            return    
        for myfile in os.listdir(hb_json_path):
            isjsonfile=re.match("^\d*_trj_(\d*)_\w*.json$",myfile);
            if isjsonfile:
                jsonfile=isjsonfile.group(0)
                dynrestrict=options['dyn_id']
                if dynrestrict:
                    dyn_id=isjsonfile.group(1)
                    if dyn_id not in dynrestrict:
                        continue
                fp_path=os.path.join(hb_json_path, jsonfile)
                myfp=fp_dict(fp_path)
                addContTypetoEdges(self,jsonfile,myfp)
                with open(fp_path,"w") as of:
                    json.dump(myfp, of)
                self.stdout.write(self.style.NOTICE("%s modified") % (jsonfile))
                    
                
            
            
