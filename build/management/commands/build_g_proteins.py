from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from common.models import WebResource, WebLink
from protein.models import Protein, ProteinGProtein,ProteinGProteinPair

from optparse import make_option
import logging
import csv
import os

class Command(BaseCommand):
    help = 'Build G proteins'

    def add_arguments(self, parser):
        parser.add_argument('--filename', action='append', dest='filename',
            help='Filename to import. Can be used multiple times')

    logger = logging.getLogger(__name__)

        # source file directory
    gprotein_data_dir = os.sep.join([settings.DATA_DIR, 'g_protein_data'])

    def handle(self, *args, **options):
        if options['filename']:
            filenames = options['filename']
        else:
            filenames = False
        
        try:
            self.create_g_proteins(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)
    
    def purge_data(self):
        try:
            ProteinGProteinPair.objects.filter().delete()
        except:
            self.logger.warning('Existing data cannot be deleted')

    def create_g_proteins(self, filenames=False):
        self.logger.info('CREATING GPROTEINS')
        self.purge_data()
        # read source files
        if not filenames:
            filenames = [fn for fn in os.listdir(self.gprotein_data_dir) if fn.endswith('.csv')]

        for filename in filenames:
            filepath = os.sep.join([self.gprotein_data_dir, filename])

            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                for row in reader:

                    entry_name = row[4]
                    primary = row[8]
                    secondary = row[9]

                    # fetch protein
                    try:
                        p = Protein.objects.get(entry_name=entry_name)
                    except Protein.DoesNotExist:
                        self.logger.warning('Protein not found for entry_name {}'.format(entry_name))
                        print('error',entry_name)
                        continue

                    primary = primary.replace("G protein (identity unknown)","None") #replace none
                    primary = primary.split(", ")

                    secondary = secondary.replace("G protein (identity unknown)","None") #replace none
                    secondary = secondary.split(", ")

                    if primary=='None' and secondary=='None':
                        print('no data for ',entry_name)
                        continue

                    for gp in primary:
                        if gp in ['None','_-arrestin','Arrestin','G protein independent mechanism']: #skip bad ones
                            continue
                        g = ProteinGProtein.objects.get_or_create(name=gp, sequence = '')[0]
                        gpair = ProteinGProteinPair(protein=p,g_protein=g,transduction='primary')
                        gpair.save()

                    for gp in secondary:
                        if gp in ['None','_-arrestin','Arrestin','G protein independent mechanism', '']: #skip bad ones
                            continue
                        if gp in primary: #sip those that were already primary
                             continue 
                        g = ProteinGProtein.objects.get_or_create(name=gp, sequence = '')[0]
                        gpair = ProteinGProteinPair(protein=p,g_protein=g,transduction='secondary')
                        gpair.save()


        self.logger.info('COMPLETED CREATING G PROTEINS')