from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection
from django.utils.text import slugify
from django.db import IntegrityError

from build.management.commands.base_build import Command as BaseBuild
from protein.models import (Protein, ProteinConformation, ProteinState, ProteinAnomaly, ProteinAnomalyType,
    ProteinSegment)
from residue.models import ResidueGenericNumber, ResidueNumberingScheme, Residue
from common.models import WebLink, WebResource, Publication
from structure.models import (Structure, StructureType, StructureSegment, StructureStabilizingAgent,PdbData,
    Rotamer, StructureSegmentModeling, StructureCoordinates, StructureCoordinatesDescription, StructureEngineering,
    StructureEngineeringDescription, Fragment)
from construct.functions import *
#from structure.functions import BlastSearch
from Bio.PDB import PDBParser,PPBuilder
from Bio import pairwise2

from structure.assign_generic_numbers_gpcr import GenericNumbering
from ligand.models import Ligand, LigandType, LigandRole, LigandProperities
from interaction.models import *
from interaction.views import runcalculation,parsecalculation

import logging
import os
import re
import yaml
import time
from collections import OrderedDict
import json
from urllib.request import urlopen
from Bio.PDB import parse_pdb_header


## FOR VIGNIR ORDERED DICT YAML IMPORT/DUMP
_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
def dict_constructor(loader, node):
    return OrderedDict(loader.construct_pairs(node))

def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

yaml.add_representer(OrderedDict, represent_ordereddict)
yaml.add_constructor(_mapping_tag, dict_constructor)

class Command(BaseBuild):
    help = 'Reads source data and creates pdb structure records'
    
    def add_arguments(self, parser):
        parser.add_argument('-p', '--proc',
            type=int,
            action='store',
            dest='proc',
            default=1,
            help='Number of processes to run')
        parser.add_argument('-f', '--filename',
            action='append',
            dest='filename',
            help='Filename to import. Can be used multiple times')
        parser.add_argument('-u', '--purge',
            action='store_true',
            dest='purge',
            default=False,
            help='Purge existing records')

    # source file directory
    structure_data_dir = os.sep.join([settings.DATA_DIR, 'structure_data', 'structures'])
    pdb_data_dir = os.sep.join([settings.DATA_DIR, 'structure_data', 'pdbs'])

    # read source files
    filenames = os.listdir(structure_data_dir)

    ### USE below to fix seg ends 
    xtal_seg_end_file = os.sep.join([settings.DATA_DIR, 'structure_data', 'annotation', 'mod_xtal_segends.yaml'])
    with open(xtal_seg_end_file, 'r') as f:
        xtal_seg_ends = yaml.load(f)

    s = ProteinSegment.objects.all()
    segments = {}
    for segment in s:
        segments[segment.slug] = segment

    #Must delete all these first for bulk to work
    PdbData.objects.all().delete()


    def handle(self, *args, **options):
        # delete any existing structure data
        if options['purge']:
            try:
                self.purge_structures()
            except Exception as msg:
                print(msg)
                self.logger.error(msg)

        # where filenames specified?
        if options['filename']:
            self.filenames = options['filename']

        try:
            self.logger.info('CREATING STRUCTURES')
            # run the function twice (once for representative structures, once for non-representative)
            iterations = 2
            for i in range(1,iterations+1):
                self.prepare_input(options['proc'], self.filenames, i)

            self.logger.info('COMPLETED CREATING STRUCTURES')
        except Exception as msg:
            print(msg)
            self.logger.error(msg)
    
    def purge_structures(self):
        Structure.objects.all().delete()

    def create_rotamers(self, structure, pdb_path):
        wt_lookup = {} #used to match WT seq_number to WT residue record
        pdbseq = {} #used to keep track of pdbseq residue positions vs index in seq
        ref_positions = {} #WT postions in alignment
        mapped_seq = {} # index in contruct, tuple of AA and WT [position,AA]

        preferred_chain = structure.preferred_chain

        if len(preferred_chain.split(','))>1: #if A,B
            preferred_chain = preferred_chain.split(',')[0]


        AA = {'ALA':'A', 'ARG':'R', 'ASN':'N', 'ASP':'D',
     'CYS':'C', 'GLN':'Q', 'GLU':'E', 'GLY':'G',
     'HIS':'H', 'ILE':'I', 'LEU':'L', 'LYS':'K',
     'MET':'M', 'PHE':'F', 'PRO':'P', 'SER':'S',
     'THR':'T', 'TRP':'W', 'TYR':'Y', 'VAL':'V'}


        s = PDBParser(PERMISSIVE=True, QUIET=True).get_structure('ref', pdb_path)[0]
        chain = s[preferred_chain] #select only one chain (avoid n-mer receptors)
        ppb=PPBuilder()
        seq = ''
        i = 1

        check_1000 = 0
        for pp in ppb.build_peptides(chain): #remove >1000 pos (fusion protein / gprotein)
            for res in pp:
                id = res.id
                if id[1]<600: 
                    check_1000 += 1
                    #need check_1000 to catch structures where they lie in 1000s (4LDE, 4LDL, 4LDO, 4N4W, 4QKX)
                if id[1]>1000 and check_1000>200: 
                    chain.detach_child(id)

        for pp in ppb.build_peptides(chain): 
            seq += str(pp.get_sequence()) #get seq from fasta (only chain A)
            for residue in pp:
                residue_id = residue.get_full_id()
                chain = residue_id[2]
                if chain not in pdbseq:
                    pdbseq[chain] = {}
                pos = residue_id[3][1]
                pdbseq[chain][pos] = [i,AA[residue.resname]]
                i += 1

        parent_seq_protein = str(structure.protein_conformation.protein.parent.sequence)
        # print(structure.protein_conformation.protein.parent.entry_name)
        rs = Residue.objects.filter(protein_conformation__protein=structure.protein_conformation.protein.parent).prefetch_related('display_generic_number','generic_number','protein_segment')

        if structure.pdb_code.index.upper() in self.xtal_seg_ends:
            seg_ends = self.xtal_seg_ends[structure.pdb_code.index.upper()]
        else:
            seg_ends = []
            # print('No SEG ENDS info for {}'.format(structure.pdb_code.index))
            self.logger.info('No SEG ENDS info for {}'.format(structure.pdb_code.index))


        parent_seq = ""
        for r in rs: #required to match WT position to a record (for duplication of GN values)
            wt_lookup[r.sequence_number] = r
            parent_seq += r.amino_acid

        if parent_seq != parent_seq_protein:
            print('Residues sequence differ from sequence in protein',structure.protein_conformation.protein.parent.entry_name,structure.pdb_code.index)

        if len(wt_lookup)==0:
            print("No residues for",structure.protein_conformation.protein.parent.entry_name)
            return None

        #align WT with structure seq -- make gaps penalties big, so to avoid too much overfitting
        pw2 = pairwise2.align.localms(parent_seq, seq, 2, -4, -4, -.1)

        gaps = 0
        unmapped_ref = {}
        for i, r in enumerate(pw2[0][0], 1): #loop over alignment to create lookups (track pos)
            # print(i,r,pw2[0][1][i-1]) #print alignment for sanity check
            if r == "-":
                gaps += 1
            if r != "-":
                ref_positions[i] = [i-gaps,r]
            elif r == "-":
                ref_positions[i] = [None,'-']

            if pw2[0][1][i-1]=='-':
                unmapped_ref[i-gaps] = '-'

        gaps = 0
        for i, r in enumerate(pw2[0][1], 1): #make second lookup
            if r == "-":
                gaps += 1
            if r != "-":
                mapped_seq[i-gaps] = [r,ref_positions[i]]


        pdb = structure.pdb_data.pdb
        protein_conformation=structure.protein_conformation
        temp = ''
        check = 0
        errors = 0
        mismatch_seq = 0
        match_seq = 0
        not_matched = 0
        matched_by_pos = 0
        aa_mismatch = 0
        generic_change = 0
        generic_change_from = []

        pdblines_temp = pdb.splitlines()
        pdblines = []
        for line in pdblines_temp: #Get rid of all odd records
            if line.startswith('ATOM'):
                pdblines.append(line)
        pdblines.append('') #add a line to not "run out"
        rotamer_bulk = []
        rotamer_data_bulk = []
        residues_bulk = []
        for i,line in enumerate(pdblines):
            if line.startswith('ATOM'): 
                chain = line[21]
                if preferred_chain and chain!=preferred_chain: #If perferred is defined and is not the same as the current line, then skip
                    pass
                else:   
                    nextline = pdblines[i+1]
                    residue_number = line[22:26].strip()
                    if (check==0 or nextline[22:26].strip()==check) and nextline.startswith('TER')==False and nextline.startswith('ATOM')==True: #If this is either the begining or the same as previous line add to current rotamer
                        temp += line + "\n"
                        #print('same res',pdb.splitlines()[i+1])
                    else: #if this is a new residue
                        #print(pdb.splitlines()[i+1][22:26].strip(),check)
                        temp += line + "\n"
                        if int(check.strip())<2000:
                            residue = Residue()
                            residue.sequence_number = int(check.strip())
                            residue.amino_acid = AA[residue_name.upper()]
                            residue.protein_conformation = protein_conformation

                            # print(residue.sequence_number,residue.amino_acid) #sanity check
                            try:
                                seq_num_pos = pdbseq[chain][residue.sequence_number][0]
                            except:
                                #print('failed residue',pdb_path,residue.sequence_number)
                                temp = "" #start new line for rotamer
                                check = pdblines[i+1][22:26].strip()
                                continue
                            if seq_num_pos in mapped_seq:
                                if mapped_seq[seq_num_pos][1][0]==None:
                                    #print('no match found') #sanity check
                                    #print(residue.sequence_number,residue.amino_acid) #sanity check
                                    residue.display_generic_number = None
                                    residue.generic_number = None
                                    residue.protein_segment = None
                                    not_matched +=1
                                else:
                                    wt_r = wt_lookup[mapped_seq[seq_num_pos][1][0]]
                                    if residue.sequence_number!=wt_r.sequence_number and residue.amino_acid!=wt_r.amino_acid and residue.sequence_number in wt_lookup: #if pos numbers not work -- see if the pos number might be in WT and unmapped
                                        if wt_lookup[residue.sequence_number].amino_acid==residue.amino_acid:
                                            if residue.sequence_number in unmapped_ref: #WT was not mapped, so could be it
                                               # print(residue.sequence_number,residue.amino_acid) #sanity check
                                                #print('wrongly matched, better match on pos+aa',residue.sequence_number,residue.amino_acid,wt_r.sequence_number,wt_r.amino_acid)
                                                wt_r = wt_lookup[residue.sequence_number]
                                                matched_by_pos +=1
                                                match_seq += 1
                                            else:
                                                mismatch_seq += 1
                                                ### REPLACE seq number with WT to fix odd PDB annotation. FIXME kinda dangerous, but best way to ensure consistent GN numbering
                                                residue.sequence_number = wt_r.sequence_number
                                                #print('could have been matched, but already aligned to another position',residue.sequence_number,residue.amino_acid,wt_r.sequence_number,wt_r.amino_acid)
                                        else:
                                            # print('WT pos not same AA, mismatch',residue.sequence_number,residue.amino_acid,wt_r.sequence_number,wt_r.amino_acid)
                                            mismatch_seq += 1
                                            aa_mismatch += 1
                                    elif residue.sequence_number!=wt_r.sequence_number:
                                        #print('WT pos not same pos, mismatch',residue.sequence_number,residue.amino_acid,wt_r.sequence_number,wt_r.amino_acid)
                                        mismatch_seq += 1
                                        ### REPLACE seq number with WT to fix odd PDB annotation. FIXME kinda dangerous, but best way to ensure consistent GN numbering
                                        residue.sequence_number = wt_r.sequence_number
                                    if residue.amino_acid!=wt_r.amino_acid:
                                        #print('aa mismatch',residue.sequence_number,residue.amino_acid,wt_r.sequence_number,wt_r.amino_acid)
                                        aa_mismatch += 1

                                    else:
                                        match_seq += 1
                                    if wt_r.generic_number is not None:
                                        residue.display_generic_number = wt_r.display_generic_number
                                        residue.generic_number = wt_r.generic_number 
                                    else:
                                        residue.display_generic_number = None
                                        residue.generic_number = None
                                        #print('no GN')
                                    residue.protein_segment = wt_r.protein_segment
                                    # print('aa ',residue.sequence_number,residue.amino_acid,wt_r.sequence_number,wt_r.amino_acid)
                                    if len(seg_ends):
                                        if residue.protein_segment.slug=='TM1':
                                            if seg_ends['1b']!='-' and seg_ends['1e']!='-':
                                                if residue.sequence_number<seg_ends['1b']:
                                                    residue.protein_segment = self.segments['N-term']
                                                elif residue.sequence_number>seg_ends['1e']:
                                                    residue.protein_segment = self.segments['ICL1']
                                        elif residue.protein_segment.slug=='ICL1':
                                            if seg_ends['i1b']!='-' and seg_ends['i1e']!='-':
                                                if residue.sequence_number<seg_ends['i1b'] and residue.sequence_number<=seg_ends['1e']:
                                                    residue.protein_segment = self.segments['TM1']
                                                elif residue.sequence_number>seg_ends['i1e']:
                                                    residue.protein_segment = self.segments['TM2']
                                        elif residue.protein_segment.slug=='TM2':
                                            if seg_ends['2b']!='-' and seg_ends['2e']!='-':
                                                if residue.sequence_number<seg_ends['2b']:
                                                    residue.protein_segment = self.segments['ICL1']
                                                elif residue.sequence_number>seg_ends['2e']:
                                                    residue.protein_segment = self.segments['ECL1']
                                        elif residue.protein_segment.slug=='ECL1':
                                            if seg_ends['e1b']!='-' and seg_ends['e1e']!='-' and seg_ends['2e']!='-':
                                                if residue.sequence_number<seg_ends['e1b'] and residue.sequence_number<=seg_ends['2e']:
                                                    residue.protein_segment = self.segments['TM2']
                                                elif residue.sequence_number>seg_ends['e1e']:
                                                    residue.protein_segment = self.segments['TM3']
                                        elif residue.protein_segment.slug=='TM3':
                                            if seg_ends['3b']!='-' and seg_ends['3e']!='-':
                                                if residue.sequence_number<seg_ends['3b']:
                                                    residue.protein_segment = self.segments['ECL1']
                                                elif residue.sequence_number>seg_ends['3e']:
                                                    residue.protein_segment = self.segments['ICL2']
                                        elif residue.protein_segment.slug=='ICL2':
                                            if seg_ends['i2b']!='-' and seg_ends['i2e']!='-':
                                                if residue.sequence_number<seg_ends['i2b']:
                                                    residue.protein_segment = self.segments['TM3']
                                                elif residue.sequence_number>seg_ends['i2e'] and residue.sequence_number>=seg_ends['4b']:
                                                    residue.protein_segment = self.segments['TM4']
                                        elif residue.protein_segment.slug=='TM4':
                                            if seg_ends['4b']!='-' and seg_ends['4e']!='-':
                                                if residue.sequence_number<seg_ends['4b']:
                                                    residue.protein_segment = self.segments['ICL2']
                                                elif residue.sequence_number>seg_ends['4e']:
                                                    residue.protein_segment = self.segments['ECL2']
                                        elif residue.protein_segment.slug=='ECL2':
                                            if seg_ends['e2b']!='-' and seg_ends['e2e']!='-' and seg_ends['4e']!='-':
                                                if residue.sequence_number<seg_ends['e2b'] and residue.sequence_number<=seg_ends['4e']:
                                                    residue.protein_segment = self.segments['TM4']
                                                elif residue.sequence_number>seg_ends['e2e'] and residue.sequence_number>=seg_ends['5b']:
                                                    residue.protein_segment = self.segments['TM5']
                                        elif residue.protein_segment.slug=='TM5':
                                            if seg_ends['5b']!='-' and seg_ends['5e']!='-':
                                                if residue.sequence_number<seg_ends['5b']:
                                                    residue.protein_segment = self.segments['ECL2']
                                                elif residue.sequence_number>seg_ends['5e']:
                                                    residue.protein_segment = self.segments['ICL3']
                                        elif residue.protein_segment.slug=='TM6':
                                            if seg_ends['6b']!='-' and seg_ends['6e']!='-':
                                                if residue.sequence_number<seg_ends['6b']:
                                                    residue.protein_segment = self.segments['ICL3']
                                                elif residue.sequence_number>seg_ends['6e']:
                                                    residue.protein_segment = self.segments['ECL3']
                                        elif residue.protein_segment.slug=='TM7':
                                            if seg_ends['7b']!='-' and seg_ends['7e']!='-':
                                                if residue.sequence_number<seg_ends['7b']:
                                                    residue.protein_segment = self.segments['ECL3']
                                                elif residue.sequence_number>seg_ends['7e']:
                                                    residue.protein_segment = self.segments['ICL4']
                                        elif residue.protein_segment.slug=='H8':
                                            if seg_ends['8b']!='-' and seg_ends['8e']!='-':
                                                if residue.sequence_number<seg_ends['8b']:
                                                    residue.protein_segment = self.segments['ICL4']
                                                elif residue.sequence_number>seg_ends['8e']:
                                                    residue.protein_segment = self.segments['C-term']

                                        residue.sequence_number = int(check.strip())
                                        #HAVE TO RESET SO IT FITS FOR INTERACTION SCRIPT

                                        if residue.protein_segment != wt_r.protein_segment:
                                            residue.display_generic_number = None
                                            residue.generic_number = None
                                            generic_change += 1
                                            # print(residue.protein_segment.slug[0:2])
                                            if residue.protein_segment.slug[0:2]=="TM":
                                                print(structure.protein_conformation.protein.entry_name,residue.amino_acid,residue.sequence_number, wt_r.sequence_number,residue.protein_segment,wt_r.protein_segment)

                                                # FIX ME
                                                # self.logger.info('No SEG ENDS info for {}'.format(structure.protein_conformation.protein.entry_name,residue.amino_acid,residue.sequence_number, wt_r.sequence_number,residue.protein_segment,wt_r.protein_segment))
                                                pass

                            else:
                                #print('wierd error') #sanity check
                                residue.display_generic_number = None
                                residue.generic_number = None
                                residue.protein_segment = None

                            #print('inserted',residue.sequence_number) #sanity check
                            # residue.save()
                            residues_bulk.append(residue)
                            #rotamer_data, created = PdbData.objects.get_or_create(pdb=temp)
                            rotamer_data_bulk.append(PdbData(pdb=temp))
                            # rotamer, created = Rotamer.objects.get_or_create(residue=residue, structure=structure, pdbdata=rotamer_data)
                            #rotamer_bulk.append(Rotamer(residue=residue, structure=structure, pdbdata=rotamer_data))

                        temp = "" #start new line for rotamer
                        check = pdblines[i+1][22:26].strip()
                    
                    check = pdblines[i+1][22:26].strip()
                chain = line[21]
                residue_name = line[17:20].title() #use title to get GLY to Gly so it matches

        bulked_res = Residue.objects.bulk_create(residues_bulk)
        bulked_rot = PdbData.objects.bulk_create(rotamer_data_bulk)

        rotamer_bulk = []
        for i,res in enumerate(bulked_res):
            rotamer_bulk.append(Rotamer(residue=res, structure=structure, pdbdata=bulked_rot[i]))

        Rotamer.objects.bulk_create(rotamer_bulk)
        # 
        # for i in bulked:
        #     print(i.pk)
        # print("WT",structure.protein_conformation.protein.parent.entry_name,"length",len(parent_seq),structure.pdb_code.index,'length',len(seq),len(mapped_seq),'mapped res',str(mismatch_seq+match_seq+aa_mismatch),'pos mismatch',mismatch_seq,'aa mismatch',aa_mismatch,'not mapped',not_matched,' mapping off, matched on pos,aa',matched_by_pos,"generic_segment_changes",generic_change)
        return None

    def main_func(self, positions, iteration):
        # filenames
        if not positions[1]:
            filenames = self.filenames[positions[0]:]
        else:
            filenames = self.filenames[positions[0]:positions[1]]

        for source_file in filenames:
            source_file_path = os.sep.join([self.structure_data_dir, source_file])
            # if source_file != "2RH1.yaml":
            #     continue
            if os.path.isfile(source_file_path) and source_file[0] != '.':
                with open(source_file_path, 'r') as f:
                    sd = yaml.load(f)
                    # is this a representative structure (will be used to guide structure-based alignments)?
                    representative = False
                    if 'representative' in sd and sd['representative']:
                        representative = True

                    # only process representative structures on first iteration
                    if not representative and iteration == 1:
                        continue

                    # skip representative structures on second iteration
                    if representative and iteration == 2:
                        continue

                    # is there a construct?
                    if 'construct' not in sd:
                        self.logger.error('No construct specified, skipping!')
                        continue

                    self.logger.info('Reading file {}'.format(source_file_path))
                    # print('{}'.format(sd['pdb']))
                    # read the yaml file

                    # does the construct exists?
                    try:
                        con = Protein.objects.get(entry_name=sd['construct'])
                    except Protein.DoesNotExist:
                        self.logger.error('Construct {} does not exists, skipping!'.format(sd['construct']))
                        continue

                    # create a structure record
                    try:
                        s = Structure.objects.get(protein_conformation__protein=con)
                    except Structure.DoesNotExist:
                        s = Structure()
                        s.representative = representative

                    # protein state
                    if 'state' not in sd:
                        self.logger.warning('State not defined, using default state {}'.format(
                            settings.DEFAULT_PROTEIN_STATE))
                        state = settings.DEFAULT_STATE.title()
                    else:
                        state = sd['state']
                    state_slug = slugify(state)
                    try:
                        ps, created = ProteinState.objects.get_or_create(slug=state_slug, defaults={'name': state})
                        if created:
                            self.logger.info('Created protein state {}'.format(ps.name))
                    except IntegrityError:
                        ps = ProteinState.objects.get(slug=state_slug)
                    s.state = ps

                    # protein conformation
                    try:
                        s.protein_conformation = ProteinConformation.objects.get(protein=con)
                    except ProteinConformation.DoesNotExist:
                        self.logger.error('Protein conformation for construct {} does not exists'.format(con))
                        continue
                    if s.protein_conformation.state is not state:
                        ProteinConformation.objects.filter(protein=con).update(state=ps)

                    # get the PDB file and save to DB
                    sd['pdb'] = sd['pdb'].upper()
                    if not os.path.exists(self.pdb_data_dir):
                        os.makedirs(self.pdb_data_dir)
                    
                    pdb_path = os.sep.join([self.pdb_data_dir, sd['pdb'] + '.pdb'])
                    if not os.path.isfile(pdb_path):
                        self.logger.info('Fetching PDB file {}'.format(sd['pdb']))
                        url = 'http://www.rcsb.org/pdb/files/%s.pdb' % sd['pdb']
                        pdbdata_raw = urlopen(url).read().decode('utf-8')
                        with open(pdb_path, 'w') as f:
                            f.write(pdbdata_raw)
                    else:
                        with open(pdb_path, 'r') as pdb_file:
                            pdbdata_raw = pdb_file.read()
                    
                    pdbdata, created = PdbData.objects.get_or_create(pdb=pdbdata_raw)
                    s.pdb_data = pdbdata

                    # UPDATE HETSYN with its PDB reference instead + GRAB PUB DATE, PMID, DOI AND RESOLUTION
                    hetsyn = {}
                    hetsyn_reverse = {}
                    for line in pdbdata_raw.splitlines():
                        if line.startswith('HETSYN'): 
                            m = re.match("HETSYN[\s]+([\w]{3})[\s]+(.+)",line) ### need to fix bad PDB formatting where col4 and col5 are put together for some reason -- usually seen when the id is +1000
                            if (m):
                                hetsyn[m.group(2).strip()] = m.group(1).upper()
                                hetsyn_reverse[m.group(1)] = m.group(2).strip().upper()
                        if line.startswith('HETNAM'): 
                            m = re.match("HETNAM[\s]+([\w]{3})[\s]+(.+)",line) ### need to fix bad PDB formatting where col4 and col5 are put together for some reason -- usually seen when the id is +1000
                            if (m):
                                hetsyn[m.group(2).strip()] = m.group(1).upper()
                                hetsyn_reverse[m.group(1)] = m.group(2).strip().upper()
                        if line.startswith('REVDAT   1'):
                            sd['publication_date'] = line[13:22]
                        if line.startswith('JRNL        PMID'):
                            sd['pubmed_id'] = line[19:].strip()
                        if line.startswith('JRNL        DOI'):
                            sd['doi_id'] = line[19:].strip()

                    if len(hetsyn) == 0:
                        self.logger.info("PDB file contained NO hetsyn")

                    with open(pdb_path,'r') as header:
                        header_dict = parse_pdb_header(header)
                    sd['publication_date'] = header_dict['release_date']
                    sd['resolution'] = str(header_dict['resolution']).strip()
                    sd['structure_method'] = header_dict['structure_method']

                    # structure type
                    if 'structure_method' in sd and sd['structure_method']:
                        structure_type = sd['structure_method'].capitalize()
                        structure_type_slug = slugify(sd['structure_method'])
                        
                        try:
                            st, created = StructureType.objects.get_or_create(slug=structure_type_slug,
                                defaults={'name': structure_type})
                            if created:
                                self.logger.info('Created structure type {}'.format(st))
                        except IntegrityError:
                            st = StructureType.objects.get(slug=structure_type_slug)
                        s.structure_type = st
                    else:
                        self.logger.warning('No structure type specified in PDB file {}'.format(sd['pdb']))

                    matched = 0
                    if 'ligand' in sd and sd['ligand']:
                        if isinstance(sd['ligand'], list):
                            ligands = sd['ligand']
                        else:
                            ligands = [sd['ligand']]
                        for ligand in ligands:
                            if 'name' in ligand:
                                if ligand['name'].upper() in hetsyn:
                                    self.logger.info('Ligand {} matched to PDB records'.format(ligand['name']))
                                    matched = 1
                                    ligand['name'] = hetsyn[ligand['name'].upper()]
                                elif ligand['name'].upper() in hetsyn_reverse:
                                    matched = 1

                    if matched==0 and len(hetsyn)>0:
                        self.logger.info('No ligand names found in HET in structure {}'.format(sd['pdb']))

                    # REMOVE? can be used to dump structure files with updated ligands
                    # yaml.dump(sd, open(source_file_path, 'w'), indent=4)

                    # pdb code
                    if 'pdb' in sd:
                        try:
                            web_resource = WebResource.objects.get(slug='pdb')
                        except:
                            # abort if pdb resource is not found
                            raise Exception('PDB resource not found, aborting!')
                        s.pdb_code, created = WebLink.objects.get_or_create(index=sd['pdb'],
                            web_resource=web_resource)
                    else:
                        self.logger.error('PDB code not specified for structure {}, skipping!'.format(sd['pdb']))
                        continue

                    # insert into plain text fields
                    if 'preferred_chain' in sd:
                        s.preferred_chain = sd['preferred_chain']
                    else:
                        self.logger.warning('Preferred chain not specified for structure {}'.format(sd['pdb']))
                    if 'resolution' in sd:
                        s.resolution = float(sd['resolution'])
                    else:
                        self.logger.warning('Resolution not specified for structure {}'.format(sd['pdb']))
                    if 'publication_date' in sd:
                        s.publication_date = sd['publication_date']
                    else:
                        self.logger.warning('Publication date not specified for structure {}'.format(sd['pdb']))

                    # publication
                    try:                     
                        if 'doi_id' in sd:
                            try:
                                s.publication = Publication.objects.get(web_link__index=sd['doi_id'])
                            except Publication.DoesNotExist as e:
                                p = Publication()
                                try:
                                    p.web_link = WebLink.objects.get(index=sd['doi_id'], web_resource__slug='doi')
                                except WebLink.DoesNotExist:
                                    wl = WebLink.objects.create(index=sd['doi_id'],
                                        web_resource = WebResource.objects.get(slug='doi'))
                                    p.web_link = wl
                                p.update_from_doi(doi=sd['doi_id'])
                                p.save()
                                s.publication = p
                        elif 'pubmed_id' in sd:
                            try:
                                s.publication = Publication.objects.get(web_link__index=sd['pubmed_id'])
                            except Publication.DoesNotExist as e:
                                p = Publication()
                                try:
                                    p.web_link = WebLink.objects.get(index=sd['pubmed_id'],
                                        web_resource__slug='pubmed')
                                except WebLink.DoesNotExist:
                                    wl = WebLink.objects.create(index=sd['pubmed_id'],
                                        web_resource = WebResource.objects.get(slug='pubmed'))
                                    p.web_link = wl
                                p.update_from_pubmed_data(index=sd['pubmed_id'])
                                p.save()
                                s.publication = p
                    except:
                        self.logger.error('Error saving publication'.format(ps.name))

                    # save structure before adding M2M relations
                    s.save()

                    #Delete previous interaction data to prevent errors.
                    ResidueFragmentInteraction.objects.filter(structure_ligand_pair__structure=s).delete()
                    StructureLigandInteraction.objects.filter(structure=s).delete()
                    #Remove previous Rotamers/Residues to prepare repopulate
                    Fragment.objects.filter(structure=s).delete()
                    Rotamer.objects.filter(structure=s).all().delete()
                    Residue.objects.filter(protein_conformation=s.protein_conformation).all().delete()

                    # endogenous ligand(s)
                    default_ligand_type = 'Small molecule'
                    if representative and 'endogenous_ligand' in sd and sd['endogenous_ligand']:
                        if isinstance(sd['endogenous_ligand'], list):
                            endogenous_ligands = sd['endogenous_ligand']
                        else:
                            endogenous_ligands = [sd['endogenous_ligand']]
                        for endogenous_ligand in endogenous_ligands:
                            if endogenous_ligand['type']:
                                lt, created = LigandType.objects.get_or_create(slug=slugify(endogenous_ligand['type']),
                                    defaults={'name': endogenous_ligand['type']})
                            else:
                                lt, created = LigandType.objects.get_or_create(slug=slugify(default_ligand_type),
                                    defaults={'name': default_ligand_type})
                            ligand = Ligand()

                            if 'iupharId' not in endogenous_ligand:
                                endogenous_ligand['iupharId'] = 0

                            ligand = ligand.load_by_gtop_id(endogenous_ligand['name'], endogenous_ligand['iupharId'],
                                lt)
                            try:
                                s.protein_conformation.protein.parent.endogenous_ligands.add(ligand)
                            except IntegrityError:
                                self.logger.info('Endogenous ligand for protein {}, already added. Skipping.'.format(
                                    s.protein_conformation.protein.parent))

                    # ligands
                    peptide_chain = ""
                    if 'ligand' in sd and sd['ligand'] and sd['ligand']!='None':
                        if isinstance(sd['ligand'], list):
                            ligands = sd['ligand']
                        else:
                            ligands = [sd['ligand']]
                        for ligand in ligands:
                            l = False
                            peptide_chain = ""
                            if 'chain' in ligand:
                                peptide_chain = ligand['chain']
                                ligand['name'] = 'pep'
                            if ligand['name'] and ligand['name'] != 'None': # some inserted as none.

                                # use annoted ligand type or default type
                                if ligand['type']:
                                    lt, created = LigandType.objects.get_or_create(slug=slugify(ligand['type']),
                                        defaults={'name': ligand['type']})
                                else:
                                    lt, created = LigandType.objects.get_or_create(
                                        slug=slugify(default_ligand_type), defaults={'name': default_ligand_type})

                                # set pdb reference for structure-ligand interaction
                                pdb_reference = ligand['name']

                                # use pubchem_id
                                if 'pubchemId' in ligand and ligand['pubchemId'] and ligand['pubchemId'] != 'None':
                                    # create ligand
                                    l = Ligand()


                                    # update ligand by pubchem id
                                    ligand_title = False
                                    if 'title' in ligand and ligand['title']:
                                        ligand_title = ligand['title']
                                    l = l.load_from_pubchem('cid', ligand['pubchemId'], lt, ligand_title)


                                # if no pubchem id is specified, use name
                                else:
                                    # use ligand title, if specified
                                    if 'title' in ligand and ligand['title']:
                                        ligand['name'] = ligand['title']

                                    # create empty properties
                                    lp = LigandProperities.objects.create()
                                    
                                    # create the ligand
                                    try:
                                        l, created = Ligand.objects.get_or_create(name=ligand['name'], canonical=True,
                                            defaults={'properities': lp, 'ambigious_alias': False})
                                        if created:
                                            self.logger.info('Created ligand {}'.format(ligand['name']))
                                        else:
                                            pass
                                    except IntegrityError:
                                        l = Ligand.objects.get(name=ligand['name'], canonical=True)

                                    # save ligand
                                    l.save()
                            else:
                                continue

                            # structure-ligand interaction
                            if l and ligand['role']:
                                role_slug = slugify(ligand['role'])
                                try:
                                    lr, created = LigandRole.objects.get_or_create(slug=role_slug,
                                    defaults={'name': ligand['role']})
                                    if created:
                                        self.logger.info('Created ligand role {}'.format(ligand['role']))
                                except IntegrityError:
                                    lr = LigandRole.objects.get(slug=role_slug)

                                i, created = StructureLigandInteraction.objects.get_or_create(structure=s,
                                    ligand=l, ligand_role=lr, annotated=True,
                                    defaults={'pdb_reference': pdb_reference})
                                if i.pdb_reference != pdb_reference:
                                    i.pdb_reference = pdb_reference
                                    i.save()


                    
                    # structure segments
                    if 'segments' in sd and sd['segments']:
                        for segment, positions in sd['segments'].items():
                            # fetch (create if needed) sequence segment
                            try:
                                protein_segment = ProteinSegment.objects.get(slug=segment)
                            except ProteinSegment.DoesNotExist:
                                self.logger.error('Segment {} not found'.format(segment))
                                continue

                            struct_seg, created = StructureSegment.objects.update_or_create(structure=s,
                                protein_segment=protein_segment, defaults={'start': positions[0], 'end': positions[1]})
                    # all representive structures should have defined segments
                    elif representative:
                        self.logger.warning('Segments not defined for representative structure {}'.format(sd['pdb']))

                    # structure segments for modeling
                    if 'segments_in_structure' in sd and sd['segments_in_structure']:
                        for segment, positions in sd['segments_in_structure'].items():
                            # fetch (create if needed) sequence segment
                            try:
                                protein_segment = ProteinSegment.objects.get(slug=segment)
                            except ProteinSegment.DoesNotExist:
                                self.logger.error('Segment {} not found'.format(segment))
                                continue

                            struct_seg_mod, created = StructureSegmentModeling.objects.update_or_create(structure=s,
                                protein_segment=protein_segment, defaults={'start': positions[0], 'end': positions[1]})

                    # structure coordinates
                    if 'coordinates' in sd and sd['coordinates']:
                        for segment, coordinates in sd['coordinates'].items():
                            # fetch (create if needed) sequence segment
                            try:
                                protein_segment = ProteinSegment.objects.get(slug=segment)
                            except ProteinSegment.DoesNotExist:
                                self.logger.error('Segment {} not found'.format(segment))
                                continue

                            # fetch (create if needed) coordinates description
                            try:
                                description, created = StructureCoordinatesDescription.objects.get_or_create(
                                    text=coordinates)
                                if created:
                                    self.logger.info('Created structure coordinate description {}'.format(coordinates))
                            except IntegrityError:
                                description = StructureCoordinatesDescription.objects.get(text=coordinates)

                            sc = StructureCoordinates()
                            sc.structure = s
                            sc.protein_segment = protein_segment
                            sc.description = description
                            sc.save()

                    # structure engineering
                    if 'engineering' in sd and sd['engineering']:
                        for segment, engineering in sd['engineering'].items():
                            # fetch (create if needed) sequence segment
                            try:
                                protein_segment = ProteinSegment.objects.get(slug=segment)
                            except ProteinSegment.DoesNotExist:
                                self.logger.error('Segment {} not found'.format(segment))
                                continue

                            # fetch (create if needed) engineering description
                            try:
                                description, created = StructureEngineeringDescription.objects.get_or_create(
                                    text=engineering)
                                if created:
                                    self.logger.info('Created structure coordinate description {}'.format(engineering))
                            except IntegrityError:
                                description = StructureEngineeringDescription.objects.get(text=engineering)

                            se = StructureEngineering()
                            se.structure = s
                            se.protein_segment = protein_segment
                            se.description = description
                            se.save()

                    # protein anomalies
                    scheme = s.protein_conformation.protein.residue_numbering_scheme
                    if 'bulges' in sd and sd['bulges']:
                        pa_slug = 'bulge'
                        try:
                            pab, created = ProteinAnomalyType.objects.get_or_create(slug=pa_slug, defaults={
                                'name': 'Bulge'})
                            if created:
                                self.logger.info('Created protein anomaly type {}'.format(pab))
                        except IntegrityError:
                            pab = ProteinAnomalyType.objects.get(slug=pa_slug)
                        
                        for segment, bulges in sd['bulges'].items():
                            for bulge in bulges:
                                try:
                                    gn, created = ResidueGenericNumber.objects.get_or_create(label=bulge,
                                        scheme=scheme, defaults={'protein_segment': ProteinSegment.objects.get(
                                        slug=segment)})
                                    if created:
                                        self.logger.info('Created generic number {}'.format(gn))
                                except IntegrityError:
                                    gn =  ResidueGenericNumber.objects.get(label=bulge, scheme=scheme)

                                try:
                                    pa, created = ProteinAnomaly.objects.get_or_create(anomaly_type=pab,
                                        generic_number=gn)
                                    if created:
                                        self.logger.info('Created protein anomaly {}'.format(pa))
                                except IntegrityError:
                                    pa, created = ProteinAnomaly.objects.get(anomaly_type=pab, generic_number=gn)

                                s.protein_anomalies.add(pa)
                    if 'constrictions' in sd and sd['constrictions']:
                        pa_slug = 'constriction'
                        try:
                            pac, created = ProteinAnomalyType.objects.get_or_create(slug=pa_slug, defaults={
                                'name': 'Constriction'})
                            if created:
                                self.logger.info('Created protein anomaly type {}'.format(pac))
                        except IntegrityError:
                            pac = ProteinAnomalyType.objects.get(slug=pa_slug)
                        
                        for segment, constrictions in sd['constrictions'].items():
                            for constriction in constrictions:
                                try:
                                    gn, created = ResidueGenericNumber.objects.get_or_create(label=constriction,
                                        scheme=scheme, defaults={'protein_segment': ProteinSegment.objects.get(
                                        slug=segment)})
                                    if created:
                                        self.logger.info('Created generic number {}'.format(gn))
                                except IntegrityError:
                                    gn =  ResidueGenericNumber.objects.get(label=constriction, scheme=scheme)

                                try:
                                    pa, created = ProteinAnomaly.objects.get_or_create(anomaly_type=pac,
                                        generic_number=gn)
                                    if created:
                                        self.logger.info('Created protein anomaly {}'.format(pa))
                                except IntegrityError:
                                    pa, created = ProteinAnomaly.objects.get(anomaly_type=pac, generic_number=gn)

                                s.protein_anomalies.add(pa)
                    
                    # stabilizing agents, FIXME - redesign this!
                    # fusion proteins moved to constructs, use this for G-proteins and other agents?
                    aux_proteins = []
                    if 'signaling_protein' in sd and sd['signaling_protein'] and sd['signaling_protein'] != 'None':
                        aux_proteins.append('signaling_protein')
                    if 'auxiliary_protein' in sd and sd['auxiliary_protein'] and sd['auxiliary_protein'] != 'None':
                        aux_proteins.append('auxiliary_protein')
                    for index in aux_proteins:
                        if isinstance(sd[index], list):
                            aps = sd[index]
                        else:
                            aps = [sd[index]]
                        for aux_protein in aps:
                            aux_protein_slug = slugify(aux_protein)[:50]
                            try:
                                sa, created = StructureStabilizingAgent.objects.get_or_create(
                                    slug=aux_protein_slug, defaults={'name': aux_protein})
                            except IntegrityError:
                                sa = StructureStabilizingAgent.objects.get(slug=aux_protein_slug)
                            s.stabilizing_agents.add(sa)

                    # save structure
                    s.save()

                
                    try:
                        current = time.time()
                        self.create_rotamers(s,pdb_path)
                        end = time.time()
                        diff = round(end - current,1)
                        self.logger.info('Create resides/rotamers done for {}. {} seconds.'.format(
                                    s.protein_conformation.protein.entry_name, diff))
                    except Exception as msg:
                        print(msg)
                        print('ERROR WITH ROTAMERS {}'.format(sd['pdb']))
                        self.logger.error('Error with rotamers for {}'.format(sd['pdb']))
                    
                    try:
                        current = time.time()
                        mypath = '/tmp/interactions/results/' + sd['pdb'] + '/output'
                        # if not os.path.isdir(mypath):
                        #     #Only run calcs, if not already in temp
                        runcalculation(sd['pdb'],peptide_chain)

                        parsecalculation(sd['pdb'],False)
                        end = time.time()
                        diff = round(end - current,1)
                        self.logger.info('Interaction calculations done for {}. {} seconds.'.format(
                                    s.protein_conformation.protein.entry_name, diff))
                    except Exception as msg:
                        print(msg)
                        print('ERROR WITH INTERACTIONS {}'.format(sd['pdb']))
                        self.logger.error('Error parsing interactions output for {}'.format(sd['pdb']))

                    try:
                        current = time.time()
                        #protein = Protein.objects.filter(entry_name=s.protein_conformation).get()
                        d = fetch_pdb_info(sd['pdb'],con)
                        #delete before adding new
                        #Construct.objects.filter(name=d['construct_crystal']['pdb_name']).delete()
                        add_construct(d)
                        end = time.time()
                        diff = round(end - current,1)
                        self.logger.info('construction calculations done for {}. {} seconds.'.format(
                                    s.protein_conformation.protein.entry_name, diff))
                    except Exception as msg:
                        print(msg)
                        print('ERROR WITH CONSTRUCT FETCH {}'.format(sd['pdb']))
                        self.logger.error('ERROR WITH CONSTRUCT FETCH for {}'.format(sd['pdb']))


                    # print('{} done'.format(sd['pdb']))
