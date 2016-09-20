from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from common.models import WebResource, WebLink
from protein.models import Protein
from drugs.models import Drugs

from optparse import make_option
import logging
import csv
import os
import pandas as pd

class Command(BaseCommand):
    help = 'Build Drug Data'

    def add_arguments(self, parser):
        parser.add_argument('--filename', action='append', dest='filename',
            help='Filename to import. Can be used multiple times')

    logger = logging.getLogger(__name__)

        # source file directory
    drugdata_data_dir = os.sep.join([settings.DATA_DIR, 'drug_data'])

    def handle(self, *args, **options):
        if options['filename']:
            filenames = options['filename']
        else:
            filenames = False
        
        try:
            self.purge_drugs()
            self.create_drug_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_drugs(self):
        try:
            Drugs.objects.all().delete()
        except Drugs.DoesNotExist:
            self.logger.warning('Drugs mod not found: nothing to delete.')

    def create_drug_data(self, filenames=False):
        self.logger.info('CREATING DRUGDATA')

        # read source files
        if not filenames:
            filenames = os.listdir(self.drugdata_data_dir)

        for filename in filenames:

            filepath = os.sep.join([self.drugdata_data_dir, filename])

            data = pd.read_csv(filepath, header=0, encoding = "ISO-8859-1")

            for index, row in enumerate(data.iterrows()):
                drugname = data[index:index+1]['Drug Name'].values[0]
                entry_name = data[index:index+1]['EntryName'].values[0]

                drugtype = data[index:index+1]['Drug Class'].values[0]
                indication = data[index:index+1]['Indication(s)'].values[0]
                novelty = data[index:index+1]['Target_novelty'].values[0]
                approval = data[index:index+1]['Approval'].values[0]
                status = data[index:index+1]['Status'].values[0]

                # fetch protein
                try:
                    p = Protein.objects.get(entry_name=entry_name)
                except Protein.DoesNotExist:
                    self.logger.warning('Protein not found for entry_name {}'.format(entry_name))
                    print('error', entry_name)
                    continue

                drug, created = Drugs.objects.get_or_create(name=drugname, drugtype=drugtype, indication=indication, novelty=novelty, approval=approval, status=status)
                drug.target.add(p)
                drug.save()

                # target_list = drug.target.all()
                # print('drug',target_list)
                # drug_list = p.drugs_set.all()
                # print('drug_list',drug_list)

        self.logger.info('COMPLETED CREATING DRUGDATA')