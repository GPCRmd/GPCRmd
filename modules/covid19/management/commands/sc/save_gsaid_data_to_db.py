from django.core.management.base import BaseCommand, CommandError
import os
import pandas as pd
from io import StringIO
from covid19.models import *
import datetime
import re
import csv
import tqdm
from django.conf import settings

class Command(BaseCommand):
    help = "Saves info from GSAID to the database."
#    def add_arguments(self, parser):
#        parser.add_argument(
#            '--ignore_publication',
#            action='store_true',
#            dest='ignore_publication',
#            default=False,
#            help='Consider both published and unpublished dynamics.',
#        )

    def handle(self, *args, **options):
        def load_df_row_by_value(df_path,colname,rowval,is_unique=True):
            rowval=str(rowval)
            with open(df_path, 'r') as read_obj:
                csv_reader = csv.reader(read_obj)
                header=False
                colidx=False
                mydf=False
                for row in csv_reader:
                    if header:
                        if row[colidx]==rowval:
                            mydf.loc[len(mydf)]=row
                            if is_unique:
                                return mydf
                    else:
                        header=row
                        colidx=row.index(colname)
                        mydf=pd.DataFrame(columns=header)
            return mydf
            
        def var_to_dfrow(df_path,varname):
            var_to_dfrow={}
            with open(df_path, 'r') as read_obj:
                csv_reader = csv.reader(read_obj)
                header=False
                var_colnum=False
                rownum=0
                for row in csv_reader:
                    if header:
                        param_val=row[var_colnum]
                        var_to_dfrow[param_val]=rownum
                        rownum+=1
                    else:
                        header=row
                        var_colnum=header.index(varname)
            return var_to_dfrow


        gsaid_path=settings.MEDIA_ROOT + "Covid19Data/Data/gisaid/tables"
        data_toni=False

        self.stdout.write(self.style.NOTICE("Loading data..."))
        if data_toni:
            #genes=pd.read_csv( os.path.join( gsaid_path, "genes.csv.xz"))
            genes_path=os.path.join( gsaid_path, "genes.csv.xz")
            seq=pd.read_csv( os.path.join( gsaid_path, "seq_2.csv.xz"),index_col=0)
            #isolates=pd.read_csv( os.path.join( gsaid_path, "isolates.csv.xz"))
            isolates_path=os.path.join( gsaid_path, "isolates.csv.xz")
        else:
            genes_path=os.path.join( gsaid_path, "genes.csv")
            #genes=pd.read_csv( os.path.join( gsaid_path, "genes.csv"))
            seq=pd.read_csv( os.path.join( gsaid_path, "seq_2.csv.xz"),index_col=0)
            #isolates=pd.read_csv( os.path.join( gsaid_path, "isolates.csv"))
            isolates_path=os.path.join( gsaid_path, "isolates.csv")


        #mutations=pd.read_csv( os.path.join( gsaid_path, "mut_list.csv"))

        self.stdout.write(self.style.NOTICE("Reading WT genes..."))
        all_genes={}   
        wt_seq=seq.loc[seq["mutation_description"]=="WT"]
        for i,seqrow in tqdm.tqdm(wt_seq.iterrows(),total=len(wt_seq)):
            seqid=seqrow["seq_idx"]    

            mygene_df=load_df_row_by_value(genes_path,"seq_idx",seqid)
            mygene=mygene_df.iloc[0]

            #mygene=genes.loc[genes["seq_idx"]==seqid].iloc[0]
            nm=mygene["gene"]
            if nm not in all_genes:                                                   
                all_genes[nm]=seqid           

        self.stdout.write(self.style.NOTICE("Saving mutation data..."))

        #ok_genes=genes.loc[( genes["bad"]==False)] #we ignore the "bad" ones

        save_to_db=True
        check=True

        mut_seq=seq.loc[(seq["mutation_description"] != "WT") & (seq["mutation_description"] != "X Too different")& (seq["mutation_description"] != "X Undefined AA")]
        total=len(mut_seq)

        for i,myseq in tqdm.tqdm(mut_seq.iterrows(),total=total):
            seq_idx=myseq["seq_idx"]

            mygene_df=load_df_row_by_value(genes_path,"seq_idx",seq_idx)
            mygene=mygene_df.iloc[0]

            #mygene=genes.loc[(genes["seq_idx"]==seq_idx)].iloc[0]
            if mygene["bad"]:
                continue
            mut_descr = myseq["mutation_description"]
            is_wt=False
            if mut_descr =="WT":
                is_wt=True
            elif mut_descr in {'X Too different', 'X Undefined AA'}:
                #Has unknown residues - Not considered
                continue

            #NSx should be ORFx - change this
            genename=mygene["gene"]
            nsnum=re.match("NS(\d+[a-zA-Z]?)",  genename)
            alt_name=None
            if nsnum:
                alt_name=genename
                genename="ORF" + nsnum.group(1)

            if save_to_db:
                isolate_id=mygene["isolate_id"]
                #myisolate=isolates.loc[isolates["isolate_id"] == isolate_id].iloc[0]

                myisolate_df=load_df_row_by_value(isolates_path,"isolate_id",isolate_id)
                myisolate=myisolate_df.iloc[0]

                (y,m,d)=myisolate["ymd"].split("-")
                if int(m)==0:
                    m=1
                if int(d)==0:
                    d=1
                isolate_date=datetime.date(int(y),int(m),int(d))

                isolateobj, created_isolateobj= CovidIsolate.objects.get_or_create(
                    isolate_name = myisolate["isolate_name"],
                    isolate_date = isolate_date,
                    isolate_id = myisolate["isolate_id"],
                    history = myisolate["history"],
                    tloc = myisolate["tloc"],
                    host = myisolate["host"],
                    originating_lab = myisolate["originating_lab"],
                    submitting_lab = myisolate["submitting_lab"],
                    submitter = myisolate["submitter"],
                    location = myisolate["location"],
                    isolate_type = myisolate["type"]
                )

                seqobj, created_seqobj =CovidSequence.objects.get_or_create(
                    seq = myseq["seq"],
                    is_wt = is_wt
                )


                finalprotobj, created_finalprotobj=CovidFinalProtein.objects.get_or_create(name=genename)
                seqgeneobj,created_seqgeneobj=CovidSequencedGene.objects.get_or_create(
                        id_final_protein=finalprotobj,
                        alt_name=alt_name,
                        id_isolate=isolateobj,
                        id_sequence=seqobj
                )

            if not is_wt:
                #check ----------
                if check:
                    if alt_name:
                        wt_seq_idx=all_genes[alt_name]
                    else:
                        wt_seq_idx=all_genes[genename]
                    wtseqobj=seq.loc[(seq["seq_idx"]==wt_seq_idx)].iloc[0]
                    wtseq=wtseqobj["seq"]
                #-------------------
                mut_li=mut_descr.split(",")
                adj=0
                for mut in mut_li:
                    mutmatch=re.match("([A-Z])(\d+)([A-Z])",  mut)
                    if mutmatch:
                        fromres=mutmatch.group(1)
                        mutpos=int(mutmatch.group(2))
                        tores=mutmatch.group(3)
                        corrected_mutpos=mutpos+adj
                        #check -----
                        if check:
                            checktores=wtseq[corrected_mutpos-1]
                            if checktores!=fromres:
                                raise Exception("No match at gene %s seq_idx %s mut %s" %(genename,myseq["seq_idx"],mut))
                        #---------------------------------
                        if save_to_db:
                            mutobj, created_mutobj=CovidMutations.objects.get_or_create(
                                resid =corrected_mutpos,
                                resletter_from = fromres,
                                resletter_to = tores,
                                id_sequence =seqobj
                                )

                    elif mut.startswith("del"):
                        #print("deletion found at seq %s" % myseq["seq_idx"])
                        mutmatch=re.match("del(\d+)([A-Z]+)",  mut)
                        if mutmatch:
                            mutpos=mutmatch.group(1)
                            fromres=mutmatch.group(2)
                            tores=""
                        else:
                            self.stdout.write(self.style.NOTICE("Error in mutation %s of seq %s" % (mut,myseq["seq_idx"])))
                    elif mut.startswith("ins"):
                        #print("insertion found at seq %s" % myseq["seq_idx"])
                        mutmatch=re.match("ins(\d+)([A-Z]+)",  mut)
                        if mutmatch:
                            mutpos=mutmatch.group(1)
                            fromres=""
                            tores=mutmatch.group(2)
                            adj-=int(mutpos)
                        else:
                            self.stdout.write(self.style.NOTICE("Error in mutation %s of seq %s" % (mut,myseq["seq_idx"])))
                    else:
                        self.stdout.write(self.style.NOTICE("Unknown mutation %s of seq %s" % (mut,myseq["seq_idx"])))
