
from django.core.management.base import BaseCommand, CommandError
import pickle
import requests
from django.conf import settings


class Command(BaseCommand):
    help = "Creates a file (considered_gpcrs.data) with a list of all GPCRs considered in GPCRdb. USed so that we don't need to query GPCRdb every time a user goes to the page."
    def handle(self, *args, **options):
        famgpcrdb=requests.get('https://gpcrdb.org/services/proteinfamily/',verify=False).json()
        gpcrclassif=[]
        c=-1
        f=-1
        sf=-1
        p=-1
        for e in sorted(famgpcrdb, key=lambda x: x["slug"]): 
            slug=e["slug"]
            mye={}
            mye["name"]=e["name"]
            mye["slug"]=e["slug"]
            mye["has_sim"]=False
            mye["children"]=[]
            if len(slug)==3:#class
                if slug=="000":
                    continue
                elif not (slug.startswith("0") ):
                    continue
                gpcrclassif.append(mye)
                c+=1
                f=-1
                sf=-1
                p=-1
            elif len(slug)==7:#fam
                gpcrclassif[c]["children"].append(mye)
                f+=1
                sf=-1
                p=-1
            elif len(slug)==11:#subfam
                gpcrclassif[c]["children"][f]["children"].append(mye)
                sf+=1
                p=-1
            elif len(slug)==15:#prot
                mye["children"]={}
                gpcrclassif[c]["children"][f]["children"][sf]["children"].append(mye)
                p+=1

        with open(settings.MEDIA_ROOT + "Precomputed/Summary_info/considered_gpcrs.data", 'wb') as filehandle:  
            # store the data as binary data stream
            pickle.dump(gpcrclassif, filehandle)
