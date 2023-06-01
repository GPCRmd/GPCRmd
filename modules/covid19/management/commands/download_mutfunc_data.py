from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
from covid19.models import *
import os
import urllib
import pandas as pd
import re
import math
from django.conf import settings

class Command(BaseCommand):
    help = "Download data from Mutfunc (sars.mutfunc.com) and saves it in the database."

    def handle(self, *args, **options):
        def mutfuncname_to_dbname(mutfuncname):
            if "orf" in mutfuncname:
                nameparts=re.match("(orf)(\d+)(\w*)",mutfuncname)
                orf=re.match("(orf)(\d+)(\w*)",mutfuncname).group(1)
                orfnum=re.match("(orf)(\d+)(\w*)",mutfuncname).group(2)
                orfletter=re.match("(orf)(\d+)(\w*)",mutfuncname).group(3)
                prot_name="%s%s%s"%(orf.upper(),orfnum,orfletter)
            elif mutfuncname=="nc":
                prot_name="N"
            elif mutfuncname=="s":
                prot_name="Spike"
            else:
                prot_name=mutfuncname.upper()
            return prot_name

        def nantoNone(myval):
            try:
                if math.isnan(myval):
                    return None
            except:
                pass
            return myval



        base_path=settings.MEDIA_ROOT + "Precomputed/covid19/tmp_mutfunc/"
        if not os.path.isdir(base_path):
            os.mkdir(base_path)
        mutfunc_base_url="ftp://ftp.ebi.ac.uk/pub/databases/mutfunc/sars/"

        mutfunc_file="summary.tsv"
        outfile_path=os.path.join(base_path,mutfunc_file)
        mutfunc_file_url=os.path.join(mutfunc_base_url,mutfunc_file)

        urllib.request.urlretrieve(mutfunc_file_url, outfile_path)

        summary_df=pd.DataFrame.from_csv(outfile_path, sep='\t', header=0,index_col=None)

        for index,row in summary_df.iterrows():
            mutfuncname=row["name"]
            prot_name=mutfuncname_to_dbname(mutfuncname)
            finprot_obj_li=CovidFinalProtein.objects.filter(name=prot_name)
            if finprot_obj_li: #We do not include proteins that were not in the DB (currently ORF10 and ORF14)
                #prot_db_muts=CovidMutations.objects.filter(id_sequence__covidsequencedgene__id_final_protein=finprot_obj_li)
                finprot_obj=finprot_obj_li[0] #There is only 1 entry per protein name

                freqval=nantoNone(row["freq"])
                if freqval is None:
                    freqpermille=None  
                else:
                    freqpermille=freqval*1000

                #save data
                mutfunc_mut_obj,created_mutfunc_mut_obj=CovidMutfuncData.objects.get_or_create(
                    id_final_protein=finprot_obj,
                    mutfunc_name=mutfuncname,
                    uniprot=nantoNone(row["uniprot"]),
                    position=nantoNone(row["position"]),
                    wt=nantoNone(row["wt"]),
                    mut=nantoNone(row["mut"]),
                    freq=freqval,
                    freqpermille=freqpermille,
                    ptm=nantoNone(row["ptm"]),
                    sift_score=nantoNone(row["sift_score"]),
                    sift_median=nantoNone(row["sift_median"]),
                    template=nantoNone(row["template"]),
                    relative_surface_accessibility=nantoNone(row["relative_surface_accessibility"]),
                    foldx_ddg=nantoNone(row["foldx_ddg"]),
                    mut_escape_mean=nantoNone(row["mut_escape_mean"]),
                    mut_escape_max=nantoNone(row["mut_escape_max"]),
                    annotation=nantoNone(row["annotation"]),
                    )
                mutfuncInt_mut_obj,created_mutfuncInt_mut_obj=CovidMutfuncDataInterface.objects.get_or_create(
                    id_mutfunc_data=mutfunc_mut_obj,
                    int_uniprot=nantoNone(row["int_uniprot"]),
                    interaction_energy=nantoNone(row["interaction_energy"]),
                    diff_interface_residues=nantoNone(row["diff_interface_residues"]),
                    int_name=nantoNone(row["int_name"]),
                    int_template=nantoNone(row["int_template"]),
                    diff_interaction_energy=nantoNone(row["diff_interaction_energy"]),
                )



