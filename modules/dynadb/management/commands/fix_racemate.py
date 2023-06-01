from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings

from modules.dynadb.molecule_properties_tools import open_molecule_file,generate_inchi,generate_smiles,generate_inchikey,generate_png
from modules.dynadb.molecule_download import retreive_compound_sdf_pubchem

from modules.dynadb.models import DyndbMolecule, DyndbCompound
from django.db.models import F

import re
import sys

class Command(BaseCommand):
    help = "Fixes duplicated molecules due to racemate compounds with 3D SDF files."
    
    
    
    def add_arguments(self, parser):
        parser.add_argument(
           '--inchikey',
            nargs='*',
            action='store',
            dest='inchikey',
            default=False,
            help="InChIKey of the molecule stereospecific molecule to replace.",
        )
        parser.add_argument(
           '--inchi',
            nargs='*',
            action='store',
            dest='inchi',
            default=False,
            help="InChI of the molecule stereospecific molecule to replace.",
        )
        parser.add_argument(
           '--molecule-id',
            nargs='*',
            action='store',
            dest='molecule-id',
            default=False,
            help="ID of the molecule stereospecific molecule to replace.",
        )
        parser.add_argument(
            '--check-compound',
            action='store_true',
            dest='check-compound',
            default=False,
            help="Provide a link for checking if the compound is a racemate.",
        )
    
            
    
    def handle(self, *args, **options):
        if len(args) > 0:
            raise ValueError('Invalid argument "%s".' % (' '.join(args)))
        incomp_options = {'inchikey','inchi','molecule-id'}
        options_sum = 0
        for opt in incomp_options:
            if options[opt] != False:
                options_sum += 1
        if options_sum > 1:
            raise ValueError("Only one option of the following ones can be used at the same time: %s" % (', '.join([ ''.join(('--',opt)) for opt in incomp_options])))
        elif options_sum == 0:
            raise ValueError("Use one option of the following ones: %s" % (', '.join(["--help"]+[ ''.join(('--',opt,' ',opt,'1',' ',opt,'2')) for opt in incomp_options])))
        
        #Retrieve coliding STD molecule
        
        
        
        if options['inchikey']:
            running_inchikey = True
            field_name = 'inchikey'
            q_dup_mol = DyndbMolecule.objects.values('id','id_compound',field_name)
            q_dup_mol = q_dup_mol.filter(**{field_name+"__in": options['inchikey']})
            inchikeys = [r['inchikey'] for r in q_dup_mol]
            u_inchikeys = set(inchikeys)
            ids = u_inchikeys
            dup_inchikeys = []
            if len(inchikeys) > len(u_inchikeys):
                inchikeys_dict = {}
                for inchikey in u_inchikeys:
                    inchikeys_dict[inchikey] = 0
                for inchikey in inchikeys:
                    inchikeys_dict[inchikey] += 1
                
                for inchikey in inchikeys_dict:
                    if inchikeys_dict[inchikey] > 1:
                        dup_inchikeys.append(inchikey)
            id_name = 'InChIKey'
             
            
        else:
            running_inchikey = False
            if options['inchi']:
                field_name = 'inchi'
                q_dup_mol = DyndbMolecule.objects.values('id','id_compound',field_name)
                reinchi = re.compile(r'^(InChI=)?')
                inchis = []
                for inchi in options['inchi']:
                    inchis.append(reinchi.sub(inchi,count=1))
                ids = inchis
                q_dup_mol = q_dup_mol.filter(**{field_name+"__in": ids})
                id_name = 'InChI'
                
            elif options['molecule-id']:
                ids = options['molecule-id']
                ids = [int(i) for i in ids]
                field_name = 'id'
                q_dup_mol = DyndbMolecule.objects.values('id','id_compound')
                q_dup_mol = q_dup_mol.filter(pk__in=options['molecule-id'])
                id_name = 'ID'
        q_ids = [q_id[field_name] for q_id in q_dup_mol] 
        i = 0
        for in_id in ids:
            if in_id not in q_ids:
                 self.stdout.write(self.style.NOTICE("%s %s: Not found.") % (id_name,str(in_id)))
                 continue
            if running_inchikey:
                if in_id in dup_inchikeys:
                 self.stdout.write(self.style.NOTICE("%s %s: duplicated molecule. Skipping.") % (id_name,str(in_id)))
                 continue
            mol_id = q_dup_mol[i]['id']
            compound_id = q_dup_mol[i]['id_compound']
            i += 1
            if options['check-compound']:
                print("%s %s: Check compound at: https://submission.gpcrmd.org/dynadb/compound/id/%i/" % (id_name,str(in_id),compound_id))
                continue
            
            
            q_compound = DyndbCompound.objects.filter(pk=compound_id).values('pubchem_cid','std_id_molecule')
            cid = q_compound[0]['pubchem_cid']
            mol_id2 = q_compound[0]['std_id_molecule']
            if mol_id != mol_id2:
                self.stdout.write(self.style.NOTICE("%s %s: molecule is not the standard form of its compound. Skipping.") % (id_name,str(in_id)))
            #get SDF path
            q_molecule_files = DyndbMolecule.objects.filter(pk=mol_id,dyndbfilesmolecule__type=0) #Select type Molecule (SDF)
            q_molecule_files = q_molecule_files.annotate(filepath=F('dyndbfilesmolecule__id_files__filepath')).values_list('filepath',flat=True)
            sdf_path = q_molecule_files[0]
            #Download pubchem 2D sdf (looking trought compound) and replace SDF.
            retreive_compound_sdf_pubchem('cid',cid,outputfile=sdf_path,in3D=False)
            self.stdout.write(self.style.SUCCESS("%s %s: SDF downloaded at %s.") % (id_name,str(in_id),sdf_path))
            #recompute inchi, inchikey and smiles
            with open(sdf_path,'rb') as f:
                mol = open_molecule_file(f,logfile=sys.__stderr__,filetype='sdf')
            inchi,code,msg = generate_inchi(mol,FixedH=True)
            if code < 2:
                self.stdout.write(self.style.WARNING("%s %s SDF to InChI: %s") % (id_name,str(in_id),msg))
            elif inchi == '' or code > 1:
                    self.stdout.write(self.style.NOTICE("%s %s SDF to InChI: %s") % (id_name,str(in_id),msg))
                    self.stdout.write(self.style.NOTICE("%s %s SDF to InChI: cannot generate InChI. Skipping.") % (id_name,str(in_id)))
                    continue
            inchikey = generate_inchikey(inchi)
            smiles = generate_smiles(mol,logfile=sys.__stderr__)
            #save molecule
            q_mol = DyndbMolecule.objects.filter(pk=mol_id)
            q_mol.update(inchi=inchi,inchikey=inchikey,smiles=smiles,update_timestamp=timezone.now(),last_update_by_dbengine=settings.DATABASES['default']['USER'])
            self.stdout.write(self.style.SUCCESS("%s %s: molecule ID %i FIXED.") % (id_name,str(in_id),mol_id))
         
        
