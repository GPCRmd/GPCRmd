from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.text import slugify
from django.db import IntegrityError

from protein.models import Protein, ProteinConformation
from residue.models import Residue
from structure.models import Structure
from construct.models import (Construct,Crystallization,CrystallizationLigandConc,ChemicalType,Chemical,ChemicalConc,ChemicalList,
CrystallizationMethods,CrystallizationTypes,ChemicalListName,ContributorInfo,ConstructMutation,ConstructInsertion,ConstructInsertionType,
ConstructDeletion,ConstructModification,CrystalInfo,ExpressionSystem,Solubilization,PurificationStep,Purification)
from construct.functions import add_construct, fetch_pdb_info

from ligand.models import Ligand, LigandType, LigandRole
from ligand.functions import get_or_make_ligand

from optparse import make_option
import logging
import csv
import os
import json
import datetime

class Command(BaseCommand):
    help = 'Build construct data'

    def add_arguments(self, parser):
        parser.add_argument('--filename', action='append', dest='filename',
            help='Filename to import. Can be used multiple times')

    logger = logging.getLogger(__name__)

        # source file directory
    construct_data_dir = os.sep.join([settings.DATA_DIR, 'structure_data','construct_data'])

    def handle(self, *args, **options):
        if options['filename']:
            filenames = options['filename']
        else:
            filenames = False
        
        try:
            self.purge_construct_data()
            self.create_construct_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)


    def purge_construct_data(self):
        Construct.objects.all().delete()
        Crystallization.objects.all().delete()
        ChemicalConc.objects.all().delete()
        Chemical.objects.all().delete()
        ChemicalType.objects.all().delete()
        ChemicalList.objects.all().delete()
        CrystallizationLigandConc.objects.all().delete()
        CrystallizationMethods.objects.all().delete()
        CrystallizationTypes.objects.all().delete()
        ChemicalListName.objects.all().delete()
        ContributorInfo.objects.all().delete()
        ConstructMutation.objects.all().delete()
        ConstructDeletion.objects.all().delete()
        ConstructInsertion.objects.all().delete()
        ConstructInsertionType.objects.all().delete()
        ConstructModification.objects.all().delete()
        CrystalInfo.objects.all().delete()
        ExpressionSystem.objects.all().delete()
        Solubilization.objects.all().delete()
        Purification.objects.all().delete()
        PurificationStep.objects.all().delete()

    def create_construct_data(self, filenames=False):
        self.logger.info('ADDING EXPERIMENTAL CONSTRUCT DATA')

        # read source files
        if not filenames:
            filenames = os.listdir(self.construct_data_dir)

        for filename in filenames:
            if filename[-4:]!='json':
                continue
            filepath = os.sep.join([self.construct_data_dir, filename])
            with open(filepath) as json_file:
                d = json.load(json_file)

                add_construct(d)

        structures = Structure.objects.all()

        for s in structures:
            pdbname = str(s)
            try:
                protein = Protein.objects.filter(entry_name=pdbname.lower()).get()
                d = fetch_pdb_info(pdbname,protein)
                add_construct(d)
            except:
                print(pdbname,'failed')



        self.logger.info('COMPLETED CREATING EXPERIMENTAL CONSTRUCT DATA')