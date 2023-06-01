from django.core.management.base import BaseCommand, CommandError
import pickle
import os
import re
import seaborn as sns
import datetime
import pandas as pd
from covid19.models import *
from django.db.models import CharField,TextField as V, F
from django.conf import settings

class Command(BaseCommand):
    help = "Transforms newick format to dictionary for the homepage phyl tree."
    def add_arguments(self, parser):
        parser.add_argument(
           '-i',
            dest='input_nwk',
            action='store',
            default=settings.MEDIA_ROOT + 'Covid19Data/Data/gisaid_timetree.nwk',
            help='Path to input file, which is the newick file'
        )
        parser.add_argument(
           '-m',
            dest='input_metadata',
            action='store',
            default=settings.MEDIA_ROOT + 'Covid19Data/Data/gisaid_metadata.tsv',
            help='Path to metadata file in TSV format'
        )
#        parser.add_argument(
#            '--only_add_mut_data',
#            action='store_true',
#            dest='only_add_mut_data',
#            default=False,
#            help='Do not generate the input files again, just use them to add data on GISAID mutations from the database',
#        )
    def handle(self, *args, **options):


        def fix_metadata(strain_data):
            none_list=["","unknown","unknowne","unkown","?","not applicable"]
            sex_val=strain_data["Sex"]
            if sex_val.isnumeric():
                if strain_data["Age"] in none_list:
                    strain_data["Age"]=float(sex_val)
                strain_data["Sex"]=""
            elif sex_val=="Woman":
                strain_data["Sex"]="Female"
            for (datalabel,dataval) in strain_data.items():
                if type(dataval)==str and dataval.lower() in none_list:
                    strain_data[datalabel]=""
                if datalabel=="S1 mutations":
                    if dataval:
                        strain_data[datalabel]=str(dataval)
                    else:
                        strain_data[datalabel]="0"

            return strain_data

        def nwk_to_dict(newick,metadata):
            newick=newick.replace(" ","").replace("'","")
                                 #"(B:6.0,(A:5.0,C:3.0,E:-4.0)Ancestor1:5.0,D:11.0);"
            tokens = re.findall(r"([^:;,()\s]*)(?:\s*:\s*([-\d.e]+)\s*)?([,);])|(\S)", newick+";")
            def recurse(nextid = 0, parentid = -1): # one node
                thisid = nextid;
                children = []

                name, length, delim, ch = tokens.pop(0)
                genbank_accession=""
                date=""
                country=""
                if ch == "(":
                    while ch in "(,":
                        node, ch, nextid = recurse(nextid+1, thisid)
                        children.append(node)
                    name, length, delim, ch = tokens.pop(0)
                if length:
                    if float(length)<0:
                        length=0
                    if float(length)>1000:
                        length=0

                node_d={"id": thisid, "name": name, "length": float(length) if length else '', 
                        "parentid": parentid, "children": children , "is_terminal": False if children else True }

                if name:
                    if name in metadata.index: #This is for GSAID trees
                        strain_data=metadata.loc[name]
                        strain_data=fix_metadata(strain_data)
                        for (datalabel,dataval) in strain_data.items():
                            datalabel=datalabel.lower().replace(" ","_")
                            if datalabel=="collection_data":
                                datalabel="date"
                            node_d[datalabel]=dataval
                    elif  "||" in name:#this if for NCBI trees
                        (genbank_accession,x,country,state,date)=name.split("|")
                        node_d["genbank_accession"]=genbank_accession
                        node_d["country"]=country
                        node_d["date"]=date
                return node_d, delim, nextid

            return recurse()[0]       



        def split_date_obj(date):
            datespl=date.split("-")
            (year,month)=datespl[:2]
            if len(datespl)>2:
                day=datespl[2]
            else:
                day=1
            dateobj = datetime.datetime(int(year),int(month),int(day))
            return dateobj


        def get_all_values(el,val_list,all_values={}):
            for myvar in val_list:
                if myvar=="collection_data":
                    myvar="date"
                if myvar not in all_values:
                    all_values[myvar]=set()
                el_val=el.get(myvar)
                if el_val:
                    all_values[myvar].add(el_val)
            if el["children"]:
                for e in el["children"]:
                    all_values=get_all_values(e,val_list,all_values)
            return all_values


        def get_max_min_date(date_li):
            mindate=None
            maxdate=None
            for mydatestr in date_li:
                dateobj=split_date_obj(mydatestr)
                if (not mindate) or dateobj < mindate:
                    mindate=dateobj
                if (not maxdate) or dateobj > maxdate:
                    maxdate=dateobj
            return (mindate,maxdate)

        def date_to_num(date,mindate):
            if not date:
                return ""
            dateobj=split_date_obj(date)
            dateval=(dateobj - mindate).days
            if dateval <0:
                raise Exception("Error obtaining date value")
            return dateval

        def incorporate_datevalue_extnode(el,mindate,colormap_date):
            if el.get("date"):
                mydate=el["date"]
                mydate=mydate.replace("'","")
                dateval=date_to_num(mydate,mindate)
                el["datevalue"]=dateval
                el["color_date"]=colormap_date[dateval]
            if el["children"]:
                for e in el["children"]:
                    incorporate_datevalue_extnode(e,mindate,colormap_date)


        def incorporate_mutation_data(el,genomes_d):
            isolate_id=el.get("gisaid_epi_isl")
            if isolate_id:
                isolate_muts_d=genomes_d.get(isolate_id)
                count_muts=0
                if isolate_muts_d:
                    count_muts=sum([len(prot_muts) for prot_muts in isolate_muts_d.values()])
                    el["mutation_data"]=isolate_muts_d
                el["mutations"]=count_muts
            el_children=el.get("children")
            if el_children:
                for e in el_children:
                    incorporate_mutation_data(e,genomes_d)

        def transform_to_categorical(varvals,group_range,sep_zero=False):
            if sep_zero:
                start_val=1
            else:
                start_val=0
            pre_categ_groups=list(range(start_val,int(max(varvals)),group_range))
            categ_groups=[(categ,categ+(group_range-1)) for categ in pre_categ_groups]
            colormap_categ=sns.color_palette("inferno_r",n_colors=len(categ_groups)).as_hex()
            all_categs=list(range(0,int(max(varvals))+1))
            categ_colors={}
            for mycateg in all_categs:
                for i,(mincateg,maxcateg) in enumerate(categ_groups):
                    if mycateg>= mincateg and mycateg<=maxcateg:
                        categ_colors[mycateg]=colormap_categ[i]
            if sep_zero:
                categ_colors[0]="#FFFFFF"
            return categ_colors

 
        def get_color_schemes(phyl_dict):
            val_list=['age', 'gisaid_clade', 'clade', 'country', 'country_of_exposure', 'admin_division', 'division_of_exposure', 'host', 'originating_lab', 'pango_lineage', 'region', 'sex', 'submitting_lab', 'collection_data', 'author', 'region_of_exposure', "emerging_lineage", "mutations"]
            all_values=get_all_values(phyl_dict,val_list)
            colors_dict={}
            for (varname,varvals) in all_values.items():
                if varname =="date":
                    (mindate,maxdate)=get_max_min_date(varvals)
                    date_diff=(maxdate - mindate).days +1
                    colormap_date=sns.color_palette("Spectral",n_colors=date_diff).as_hex()
                    incorporate_datevalue_extnode(phyl_dict,mindate,colormap_date)
                    date_colors={}
                    date_colorsli=[]
                    for i,mydate in enumerate(sorted(varvals)):
                        mydate=mydate.replace("'","")
                        dateval=date_to_num(mydate,mindate)
                        date_colors[mydate]=colormap_date[dateval]
                        date_colorsli.append({"color":colormap_date[dateval],"value":mydate,"pos":i})
                    colors_dict[varname]=date_colors
                    colors_dict["date_list"]=date_colorsli
                    
                elif varname=="age":
                    colors_dict[varname]=transform_to_categorical(varvals,10)
                elif varname=="mutations":
                    colors_dict[varname]=transform_to_categorical(varvals,5,True)
                else:
                    any_not_number=[e for e in varvals if not str(e).isnumeric()]
                    if any_not_number:
                        varvals=sorted(varvals)
                    else:
                        varvals=sorted(varvals,key=lambda x:float(x))
                    mycolormap=sns.color_palette("Spectral",n_colors=len(varvals)).as_hex()
                    colors_dict[varname]={myval:mycolormap[i] for i,myval in enumerate(varvals)}
            return colors_dict


        def load_mutation_data():
            #start_time = time.time()
            seqgeneobj=CovidSequencedGene.objects.filter(id_sequence__is_wt=False)
            myseqgene=seqgeneobj.annotate(genename=F("id_final_protein__name"))
            myseqgene=myseqgene.annotate(isolateid=F("id_isolate__isolate_id"))
            myseqgene=myseqgene.annotate(mut_pos=F("id_sequence__seq_mutations__resid"))
            myseqgene=myseqgene.annotate(mut_from=F("id_sequence__seq_mutations__resletter_from"))
            myseqgene=myseqgene.annotate(mut_to=F("id_sequence__seq_mutations__resletter_to"))
            genomes_vals=myseqgene.values("genename","isolateid","mut_pos","mut_from","mut_to").iterator()
            genomes_d={}
            for thisgenome in genomes_vals:
                if thisgenome["mut_pos"]:
                    isolateid=thisgenome["isolateid"]
                    if isolateid not in genomes_d:
                        genomes_d[isolateid]={}
                    genename=thisgenome["genename"]
                    if genename not in genomes_d[isolateid]:
                        genomes_d[isolateid][genename]=set()
                    mutname="%s%s%s"%(thisgenome["mut_from"],thisgenome["mut_pos"],thisgenome["mut_to"])
                    genomes_d[isolateid][genename].add(mutname)
            for geno_id,geno in genomes_d.items():
                for prot, protset in geno.items():
                    geno[prot]=list(protset)
            #print( "Time: %.2f seconds" % (time.time() - start_time))
            return genomes_d

        #TO DO: automatize download of input

        phyl_dict=False
        out_path=settings.MEDIA_ROOT + "Covid19Data/Data/tree.data"
        #if not options["only_add_mut_data"]:
        input_nwk=options["input_nwk"]
        input_metadata=options["input_metadata"]
        if not os.path.isfile(input_nwk):
            raise Exception("Input file not found")
        if input_metadata:
            if not os.path.isfile(input_metadata):
                raise Exception("Metadata file not found")
            #metadata=pd.DataFrame.from_csv(input_metadata, sep='\t').dropna(how="all").fillna(value="")
            metadata=pd.read_csv(input_metadata, index_col=0, error_bad_lines=False,sep='\t',quoting=3).dropna(how="all").fillna(value="")
            #metadata=pd.read_table(input_metadata, index_col=0, error_bad_lines=False,sep='\t',quoting=3).dropna(how="all").fillna(value="")
        else:
            print("No metadata file provided.")
            metadata={}


        print("Loading data...")
        genomes_d=load_mutation_data()
        print("Generating plot...")
        with open(input_nwk, 'r') as content_file:
            nwk_str = content_file.read()
            phyl_dict=nwk_to_dict(nwk_str,metadata)

        incorporate_mutation_data(phyl_dict,genomes_d)                


        #Obtain color scheme of all variables in the metadata
        colors_dict=get_color_schemes(phyl_dict)

        print("Saving %s"% out_path)
        with open(out_path,"wb") as out_fileh:
            pickle.dump(phyl_dict,out_fileh)
        self.stdout.write(self.style.NOTICE("File successfully generated."))

        out_path_colors=settings.MEDIA_ROOT + "Covid19Data/Data/colorscales.data"
        print("Saving %s"% out_path_colors)
        with open(out_path_colors,"wb") as out_fileh:
            pickle.dump(colors_dict,out_fileh)


#        print("Obtaining data on isolate mutations...")
#        if not phyl_dict:
#            if os.path.isfile(out_path):
#                with open(out_path, "rb") as fh:
#                    phyl_dict=pickle.load(fh)
#            else:
#                raise Exception("Tree file not found - cannot assign GISAID mutations")


        #create dictionary isolate to mutations:




        #Save as dict and load at home, or iterate tree dict to add mutation list to each isolate

#        out_path_genomes=settings.MEDIA_ROOT + "Covid19Data/Data/home_genome_muts.data"
#        with open(out_path_genomes,"wb") as fh:
#            pickle.dump(genomes_d,fh)


#        #option 2
#        queryset = CovidIsolate.objects.all().iterator()
#        #queryset = CovidIsolate.objects.filter(covidsequencedgene__id_sequence__is_wt=False).iterator()
#        isolate_mutations={}
#        for isolateobj in queryset:
#            #get_isolate_mutations(isolateobj)
#            found_muts=CovidMutatedPos.objects.filter(covidsequence__covidsequencedgene__id_isolate__isolate_id=isolateobj)
#            found_muts=found_muts.annotate(prot_name=F("id_final_protein__name"))
#            found_muts=found_muts.annotate(resletter_from=F("pos_mutations__resletter_from"))
#            found_muts=found_muts.annotate(resletter_to=F("pos_mutations__resletter_to"))
#            found_muts_vals=found_muts.values("resid","resletter_from","resletter_to","prot_name")
#            muts_in_isolate={}
#            for found_mut in found_muts_vals:
#                prot_name=found_mut["prot_name"]
#                mut_name="%s%s%s"%(found_mut["resletter_from"],found_mut["resid"],found_mut["resletter_to"])
#                if prot_name not in muts_in_isolate:
#                    muts_in_isolate[prot_name]=[]
#                muts_in_isolate[prot_name].append(mut_name)
#            isolate_mutations[isolateobj.isolate_id]=muts_in_isolate
