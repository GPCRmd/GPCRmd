from django.core.management.base import BaseCommand, CommandError
from covid19.models import *
from django.db.models import F
from covid19.views import load_mutfunc_mutationeffect_data,write_variantscore_data,write_variantscore_data_values
import argparse
import os
import pickle
import csv
import re
from django.conf import settings

class Command(BaseCommand):
    help = "For each dyn and traj, creates a file with the parameter values of each variant."
    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrite all results.',
        )
        parser.add_argument(
           '--dyn',
            dest='specify_dyn',
            nargs='*',
            action='store',
            type=int,
            default=False,
            help='Specify dynamics id(s) for which the matrix will be precomputed. '
        )
    def handle(self, *args, **options):
        def load_precomputed_parameters(dyn_id,traj_id):
            impact_per_variant_path_pre=settings.MEDIA_ROOT + "Precomputed/covid19/variant_impact/summary"
            impact_per_variant_path=os.path.join(impact_per_variant_path_pre,"dyn_%s_traj_%s.data"%(dyn_id,traj_id))
            if os.path.isfile(impact_per_variant_path):
                with open(impact_per_variant_path,"rb") as fh:
                    impact_per_variant=pickle.load(fh)
                    return impact_per_variant
            else:
                print("Dyn %s Traj %s - Data not found."%(dyn_id,traj_id))
                return False



        def create_variant_scores_file(dyn_id,traj_id,overwrite):
            mut_impact_data=load_precomputed_parameters(dyn_id,traj_id)
            if not mut_impact_data:
                return False
            mutfunc_o=CovidMutfuncData.objects.filter(id_final_protein__covidmodel__coviddynamics__id=dyn_id)
            mutfunc_data=load_mutfunc_mutationeffect_data(mutfunc_o)

            #merge  mutfunc_data with our data on precomputed parameters 
            for finprot,protdata in mut_impact_data.items():
                for protpos,posdata in protdata.items():
                    posvars=posdata["variants"]
                    for varname, vardict in posvars.items():
                        try:
                            vardict["mutfunc"]=mutfunc_data[finprot][protpos][varname]
                        except KeyError:
                            pass

            out_path=settings.MEDIA_ROOT + "Precomputed/covid19/impact_scores_result"
            if not os.path.isdir(out_path):
                os.mkdir(out_path)
            out_file=os.path.join(out_path,"dyn_%s_traj_%s.csv"%(dyn_id,traj_id))
            if not  os.path.isfile(out_file) or overwrite:
                dyn=CovidDynamics.objects.get(id=dyn_id)
                with open(out_file, "w", newline="") as csv_file:
                    writer = csv.writer(csv_file, delimiter=',')
                    all_notes=[
                        ["#System name: %s"% dyn.dyn_name],
                        ["#Time-dependent data is not mutation-dependent - it's the same for all variants in a given position."],
                        ["#Time-dependent data is calculated for each trajectory frame. Here we provide the average value and the SD. RMSF is an exception: it is calculated for each residue atom, not frame, and here we provide average and SD of atom RMSF"],
                        ["#Data labeled as 'mutfunc' is obtained from sars.mutfunc.com (Alistair Dunham, Gwendolyn M Jang, Monita Muralidharan, Danielle Swaney & Pedro Beltrao. 2021. A missense variant effect prediction and annotation resource for SARS-CoV-2. bioRxiv: 2021.02.24.432721 doi: https://doi.org/10.1101/2021.02.24.432721)"],
                        ["#Annotation is not a numeric value, but can be interesting to take a look in case there is information on the functional impact"]
                        ]

                    write_variantscore_data(writer,all_notes,mut_impact_data,ptm_binary=True)

        overwrite=options["overwrite"]
        specify_dyn=options["specify_dyn"]

        if specify_dyn:
            alldyn=CovidDynamics.objects.filter(is_published=True, id__in=specify_dyn)
        else:
            alldyn=CovidDynamics.objects.filter(is_published=True)
        for dyn in sorted(alldyn,key=lambda x:x.id):
            dyn_id=dyn.id
            traj_files=dyn.covidfilesdynamics_set.filter(type=2)
            for traj in traj_files:
                traj_id=traj.id_files.id
                print("-- Dyn %s Traj %s --" %(dyn_id,traj_id))
                create_variant_scores_file(dyn_id,traj_id,overwrite)

