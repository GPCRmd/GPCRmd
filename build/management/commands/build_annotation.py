from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection
from django.utils.text import slugify
from django.db import IntegrityError
from django.db import transaction

from build.management.commands.base_build import Command as BaseBuild
from residue.models import Residue
from residue.functions import *
from protein.models import Protein, ProteinConformation, ProteinSegment, ProteinFamily

from Bio import pairwise2
from Bio.SubsMat import MatrixInfo as matlist

import logging
import os
import sys
import re
import yaml
from datetime import datetime
import time
from collections import OrderedDict
from itertools import islice
from urllib.request import urlopen, quote
import xlrd
import operator
import traceback
import numbers

class Command(BaseBuild):
    help = 'Reads source data and creates annotations'

    def add_arguments(self, parser):
        parser.add_argument('-p', '--proc',
            type=int,
            action='store',
            dest='proc',
            default=1,
            help='Number of processes to run')
        
    logger = logging.getLogger(__name__)

    # source file directory
    annotation_source_file = os.sep.join([settings.DATA_DIR, 'structure_data', 'Structural_Annotation.xlsx'])
    xtal_seg_end_file = os.sep.join([settings.DATA_DIR, 'structure_data', 'xtal_segends.yaml'])
    generic_numbers_source_dir = os.sep.join([settings.DATA_DIR, 'residue_data', 'generic_numbers'])

    segments = ProteinSegment.objects.filter(partial=False)
    all_segments = {ps.slug: ps for ps in ProteinSegment.objects.all()}  # all segments dict for faster lookups
    schemes = parse_scheme_tables(generic_numbers_source_dir)

    pconfs = ProteinConformation.objects.all().order_by('protein__family')

    pw_aln_error = ['celr3_mouse','celr3_human','gpr98_human']

    def handle(self, *args, **options):
        try:
            self.logger.info('CREATING RESIDUES')
            self.data = self.parse_excel(self.annotation_source_file)

            self.dump_seg_ends()

            # self.analyse_annotation_consistency()

            # run the function twice (second run for proteins without reference positions)

            self.prepare_input(options['proc'], self.pconfs)

            # if (self.check_if_residues()):
            #     self.prepare_input(1, self.pconfs)

            # if (self.check_if_residues()):
            #     self.prepare_input(1, self.pconfs)

            # if (self.check_if_residues()):
            #     self.prepare_input(1, self.pconfs)

            self.logger.info('COMPLETED CREATING RESIDUES')
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def parse_excel(self,path):
        workbook = xlrd.open_workbook(path)
        worksheets = workbook.sheet_names()
        d = {}
        for worksheet_name in worksheets:
            if worksheet_name in d:
                print('Error, worksheet with this name already loaded')
                continue

            d[worksheet_name] = OrderedDict()
            worksheet = workbook.sheet_by_name(worksheet_name)

            num_rows = worksheet.nrows - 1
            num_cells = worksheet.ncols - 1
            curr_row = 0 #skip first, otherwise -1

            headers = []
            for i in range(num_cells):
                h = worksheet.cell_value(0, i)
                if h=="":
                    #replace header with index if empty
                    h = "i_"+str(i)
                if h in headers:
                    # print('already have ',h)
                    h += "_"+str(i)
                # print(h)
                headers.append(worksheet.cell_value(0, i))

            for curr_row in range(1,num_rows+1):
                row = worksheet.row(curr_row)
                key = worksheet.cell_value(curr_row, 0)

                if key=='':
                    #in case there is no key for whatever reason
                    # print("no key!")
                    continue

                d[worksheet_name][key] = OrderedDict()
                temprow = {}
                for curr_cell in range(num_cells):
                    # cell_type = worksheet.cell_type(curr_row, curr_cell)
                    cell_value = worksheet.cell_value(curr_row, curr_cell)
                    # temprow.append(cell_value)
                    d[worksheet_name][key][headers[curr_cell]] = cell_value

                # if curr_row>2: break
        return d

    def dump_seg_ends(self):
        structures = self.data["Xtal_SegEnds_Prot#"]
        pdb_info = {}
        for structure,vals in structures.items():
            if structure.split("_")[-1] == "wt":
                continue
            if structure.split("_")[-1] == "dist":
                continue
            #print(structure)
            pdb_id = structure.split("_")[-1]
            pdb_info[pdb_id] = {}
            for key,val in vals.items():
                if len(key)>3:
                    continue
                if not key:
                    continue
                if key[-1]!="b" and key[-1]!="e":
                    continue

                pdb_info[pdb_id][key] = val

        #print(pdb_info)
        with open(self.xtal_seg_end_file, 'w') as outfile:
            yaml.dump(pdb_info, outfile)

    def analyse_annotation_consistency(self):
        NonXtal = self.data["NonXtal_Bulges_Constr_GPCRdb#"]
        Xtal = self.data["Xtal_Bulges_Constr_GPCRdb#"]
        output = {}
        counting_xtal = {}
        counting_non_xtal = {}
        for entry_protein,vals in NonXtal.items():
            anomalies=[]
            anomalies_xtal=[]
            for key,val in vals.items():
                if "x" in val and "_" not in val:
                    if val.index("x") in [1,2]:
                        anomalies.append(val)
            if vals['Xtal Templ'] in Xtal:
                #print(Xtal[vals['Xtal Templ']])
                for key,val in Xtal[vals['Xtal Templ']].items():
                    if "x" in val and "_" not in val:
                        if val.index("x") in [1,2]:
                            anomalies_xtal.append(val)

            if entry_protein!=vals['Xtal Templ']:
                list1 = list(set(anomalies) - set(anomalies_xtal))
                list2 = list(set(anomalies_xtal) - set(anomalies))
                if list1 or list2:
                    for i in list1:
                        if i not in counting_non_xtal:
                            counting_non_xtal[i] = 0
                        counting_non_xtal[i] += 1
                    for i in list2:
                        if i not in counting_xtal:
                            counting_xtal[i] = 0
                        counting_xtal[i] += 1
                    #print("ISSUE!")
                    #print(entry_protein)
                    #print("NonXtal_anomalies",anomalies,"Xtal_anomalies",anomalies_xtal)
                    if list1: print(entry_protein,vals['Xtal Templ'],"Present in non-xtal, but not xtal",list1)
                    if list2: print(entry_protein,vals['Xtal Templ'],"Present in xtal, but not non-xtal",list2)

        print("Overall")
        print("Present in non-xtal, but not xtal",counting_xtal)
        print("Present in xtal, but not non-xtal",counting_non_xtal)

        structures = self.data["Xtal_SegEnds_Prot#"]
        structures_non_xtal = self.data["NonXtal_SegEnds_Prot#"]
        info = {}
        for structure,vals in structures.items():
            if structure.split("_")[-1] == "wt":
                #print(structure)
                entry = vals['UniProt']
                info[entry] = {}
                for key,val in vals.items():
                    if len(key)>3:
                        continue
                    if not key:
                        continue
                    if key[-1]!="b" and key[-1]!="e":
                        continue

                    info[entry][key] = val

                    if structures_non_xtal[entry][key]!=val:
                        print("error with ",entry,key,"Xtal sheet:",round(val),"NonXtal sheet:",round(structures_non_xtal[entry][key]))
                        #print(structures_non_xtal[entry])
                        #print(vals)
                #print(structure,info)

        # with open(self.xtal_seg_end_file, 'w') as outfile:
        #     yaml.dump(pdb_info, outfile)


    def generate_bw(self, i, v, aa):
        #return dict
        a = {'aa':aa, 'pos':i, 's':'', 'numbers':{'bw':''}}
        if i<int(v['1b']):
            a['s'] = 'N-term'
        elif i<=int(v['1e']):
            a['s'] = 'TM1'
            a['numbers']['bw'] = '1.'+str(50+i-int(v['1x']))
        elif v['i1x']!="-" and v['i1e']!="-" and i<int(v['2b']):
            if i<int(v['i1b']):
                a['s'] = 'ICL1'
            elif i<=int(v['i1e']):
                a['s'] = 'ICL1'
                a['numbers']['bw'] = '12.'+str(50+i-int(v['i1x']))
            else:
                a['s'] = 'ICL1'
        elif i<int(v['2b']):
            a['s'] = 'ICL1'
        elif i<=int(v['2e']):
            a['s'] = 'TM2'
            a['numbers']['bw'] = '2.'+str(50+i-int(v['2x']))
        elif v['e1x']!="-" and i<int(v['3b']):
            if i<int(v['e1b']):
                a['s'] = 'ECL1'
            elif i<=int(v['e1e']):
                a['s'] = 'ECL1'
                a['numbers']['bw'] = '23.'+str(50+i-int(v['e1x']))
            else:
                a['s'] = 'ECL1'
        elif i<int(v['3b']):
            a['s'] = 'ECL1'
        elif i<=int(v['3e']):
            a['s'] = 'TM3'
            a['numbers']['bw'] = '3.'+str(50+i-int(v['3x']))
        elif v['i2x']!="-" and i<int(v['4b']):
            if i<int(v['i2b']):
                a['s'] = 'ICL2'
            elif i<=int(v['i2e']):
                a['s'] = 'ICL2'
                a['numbers']['bw'] = '34.'+str(50+i-int(v['i2x']))
            else:
                a['s'] = 'ICL2'
        elif i<int(v['4b']):
            a['s'] = 'ICL2'
        elif i<=int(v['4e']):
            a['s'] = 'TM4'
            a['numbers']['bw'] = '4.'+str(50+i-int(v['4x']))
        elif v['e2x']!="-" and i<int(v['5b']) and v['e2b']!="-":
            if i<int(v['e2b']):
                a['s'] = 'ECL2'
            elif i<=int(v['e2e']):
                a['s'] = 'ECL2'
                a['numbers']['bw'] = '45.'+str(50+i-int(v['e2x']))
            else:
                a['s'] = 'ECL2'
        elif i<int(v['5b']):
            a['s'] = 'ECL2'
        elif i<=int(v['5e']):
            a['s'] = 'TM5'
            a['numbers']['bw'] = '5.'+str(50+i-int(v['5x']))
        elif i<int(v['6b']):
            a['s'] = 'ICL3'
        elif i<=int(v['6e']):
            a['s'] = 'TM6'
            a['numbers']['bw'] = '6.'+str(50+i-int(v['6x']))
        elif v['7b']=="-": #fix for npy6r_human
            a['s'] = 'C-term'
        elif i<int(v['7b']):
            a['s'] = 'ECL3'
        elif i<=int(v['7e']):
            a['s'] = 'TM7'
            a['numbers']['bw'] = '7.'+str(50+i-int(v['7x']))
        elif v['8x']!="-":
            if i<int(v['8b']):
                a['s'] = 'ICL4'
            elif i<=int(v['8e']):
                a['s'] = 'H8'
                a['numbers']['bw'] = '8.'+str(50+i-int(v['8x']))
            else:
                a['s'] = 'C-term'
        else:
            a['s'] = 'C-term'

        if a['numbers']['bw'] == '':
            a['numbers'].pop('bw', None)

        return a

    def b_and_c_check(self,b_and_c,number,seg):
        offset = 0
        bulge = False
        if seg in b_and_c:
            bcs = sorted(b_and_c[seg])
            if int(number)<50:
                bcs = sorted(bcs, reverse=True)
            for bc in bcs:
                if len(bc)>2: #bulge
                    # print(bc[0:2],number,offset)
                    if int(bc[0:2])<50 and int(number)+offset<int(bc[0:2]): #before x50 and before bulge, do smt
                        offset += 1 #eg if 5x461, then 5.46 becomes 5x461, 5.45 becomes 5x46
                    elif int(bc[0:2])<50 and int(number)+offset==int(bc[0:2]): #before x50 and is bulge, do smt
                        bulge = True # eg if 5x461, then 5.46 becomes 5x461
                    elif int(bc[0:2])>=50 and int(number)+offset>int(bc[0:2])+1: #after x50 and after bulge, do smt
                        offset -= 1 #eg if 2x551, then 2.56 becomes 2x551, 5.57 becomes 5x56
                    elif int(bc[0:2])>=50 and int(number)+offset==int(bc[0:2])+1: #after x50 and 1 after bulge, do smt
                        bulge = True # eg if 2x551, then 2.56 becomes 2x551

                else: #2 numbers, it's a constriction
                    if int(bc[0:2])<50 and int(number)+offset<=int(bc[0:2]): #before x50 and before or equal constrictions, do smt
                        offset -= 1 #eg if constriction is 7x44, then 7.44 becomes 7x43, 7.43 becomes 7x42
                    if int(bc[0:2])>50 and int(number)+offset>=int(bc[0:2]): #before x50 and before or equal constrictions, do smt
                        offset += 1 #eg if constriction is 4x57, then 4.57 becomes 4x58, 4.58 becomes 4x59
        
        if bulge!=True:
            gn = str(int(number)+offset)
        elif int(number)<50:
            gn = str(int(number)+offset)+"1"
        elif int(number)>=50:
            gn = str(int(number)-1+offset)+"1"
        # print(gn,number,offset,bulge)
        return gn

    def check_if_residues(self):
        fail = False
        for p in self.pconfs:
            if Residue.objects.filter(protein_conformation=p).count():
                pass
            else:
                print("No residues for ",p)
                self.logger.error('No residues for parent {}'.format(p))
                fail = True
        return fail


    def main_func(self, positions, iteration):
        self.logger.info('STARTING ANNOTATION PROCESS {}'.format(positions))

        if not positions[1]:
            pconfs = self.pconfs[positions[0]:]
        else:
            pconfs = self.pconfs[positions[0]:positions[1]]


        proteins = list(self.data["NonXtal_SegEnds_Prot#"])

        # print(data)
        counter = 0
        lacking = []
        # print('total',len(pconfs))
        for p in pconfs:
            entry_name = p.protein.entry_name
            ref_positions = None
            counter += 1
            missing_x50s = []
            aligned_gn_mismatch_gap = 0
            human_ortholog = ''
            # self.logger.info('DOING {}'.format(p))
            # if p.protein.residue_numbering_scheme.slug!='gpcrdbc' or p.protein.species.common_name != "Human":
            #     continue
            # if p.protein.species.common_name != "Human":
            #     continue
            # if p.protein.entry_name !='aa2ar_human':
            #     continue
            # print(p.protein.entry_name)
            # continue
            # print(counter,p.protein.entry_name)
            # Residue.objects.filter(protein_conformation=p).delete()
            if Residue.objects.filter(protein_conformation=p).count():
                # print(counter,entry_name,"already done")
                continue
            else:
                # print(counter,p)
                if p.protein.species.common_name != "Human" and entry_name not in proteins:
                    human_ortholog = Protein.objects.filter(family=p.protein.family, species__common_name='Human')
                    if human_ortholog.exists():
                        human_ortholog = human_ortholog.get()
                        if human_ortholog.entry_name not in proteins:
                            if human_ortholog.entry_name not in lacking:
                                lacking.append(human_ortholog.entry_name)
                            print(counter,human_ortholog.entry_name, 'not in excel')
                            self.logger.error('Human ortholog ({}) of {} has no annotation in excel'.format(human_ortholog.entry_name,entry_name))
                            continue
                        if human_ortholog.entry_name in proteins:
                            # print(counter,entry_name,'check sequences')
                            ref_positions, aligned_gn_mismatch_gap = self.compare_human_to_orthologue(human_ortholog, p.protein, self.data["NonXtal_SegEnds_Prot#"][human_ortholog.entry_name],counter)
                            s = p.protein.sequence
                            v = self.data["NonXtal_SegEnds_Prot#"][human_ortholog.entry_name]
                            new_v = {}
                            # print(v)
                            failed = None
                            x50s = ['1x','i1x','2x','e1x','3x','i2x','4x','e2x','5x','6x','7x','8x']
                            x50s_must_have = ['1x','2x','3x','4x','5x','6x','7x']
                            for x50 in x50s:
                                #1b  1x  1e  i1b i1x i1e 2b  2x  2e  e1b e1x e1e 3b  3x  3e  i2b i2x i2e 4b  4x  4e  e2b e2x e2e 5b  5x  5e  6b  6x  6e  7b  7x  7e  8b  8x  8e
                                val = v[x50]
                                if isinstance(val, numbers.Real):
                                    i = int(val)
                                    try:
                                        i_b = int(v[x50[:-1]+"b"])
                                        length_to_b = i_b-i
                                        i_e = int(v[x50[:-1]+"e"])
                                        length_to_e = i_e-i
                                    except:
                                        print("Error in annotation",entry_name,human_ortholog.entry_name)
                                        self.logger.error('Error in annotation {}<->{} ({})'.format(entry_name,human_ortholog.entry_name,val))
                                        failed = True
                                        break
                                    if i in ref_positions:
                                        new_v[x50] = ref_positions[i]
                                        ## MAYBE NEED SOME RULES HERE.... 
                                        new_v[x50[:-1]+"b"] = ref_positions[i]+length_to_b
                                        new_v[x50[:-1]+"e"] = ref_positions[i]+length_to_e
                                    else:
                                        new_v[x50] = 0
                                        new_v[x50[:-1]+"b"] = 0
                                        new_v[x50[:-1]+"e"] = 0
                                        missing_x50s.append(x50)
                                        if x50 in x50s_must_have:
                                            # print(entry_name,"tranlated ",x50," no index in ortholog, deleting pconf and protein")
                                            self.logger.warning('{} tranlated {} no index in ortholog, deleting pconf and protein'.format(entry_name,x50))
                                            failed = True
                                            p.protein.delete()
                                            p.delete()
                                            break
                                else:
                                    new_v[x50] = 0
                                    new_v[x50[:-1]+"b"] = 0
                                    new_v[x50[:-1]+"e"] = 0

                            # print(new_v)
                            if failed:
                                continue

                            if aligned_gn_mismatch_gap>10:
                                self.logger.warning('{} ({}) lots of misaligned GN {}'.format(entry_name,human_ortholog.entry_name,aligned_gn_mismatch_gap))
                                # print(entry_name,"(",human_ortholog.entry_name,") lots of misaligned GN",aligned_gn_mismatch_gap)

                            v = new_v
                            #exit()
                            b_and_c = {}
                            for entry,gn in self.data["NonXtal_Bulges_Constr_GPCRdb#"][human_ortholog.entry_name].items():
                                if len(entry)<3:
                                    continue
                                if entry[1]=='x' or entry[2]=='x':
                                    if gn!="" and gn!='-':
                                        seg, number = entry.split("x")
                                        if seg not in b_and_c:
                                            b_and_c[seg] = []
                                        b_and_c[seg].append(number)
                                        if gn!=entry:
                                            print('Something off with b_and_c for',human_ortholog.entry_name,'gn',gn,'entry',entry)
                    else:
                        # pass
                        self.logger.warning('{}  has no human template, deleting'.format(entry_name))
                        p.protein.delete()
                        p.delete()
                        failed = True
                        #continue
                elif entry_name in proteins:
                    # print(entry_name,"not done but ready")    
                    v = self.data["NonXtal_SegEnds_Prot#"][entry_name]
                    # if counter>20:
                    #     break
                    s = self.data["Seqs"][entry_name]['Sequence']
                    b_and_c = {}
                    for entry,gn in self.data["NonXtal_Bulges_Constr_GPCRdb#"][entry_name].items():
                        if len(entry)<3:
                            continue
                        if entry[1]=='x' or entry[2]=='x':
                            if gn!="" and gn!='-':
                                seg, number = entry.split("x")
                                if seg not in b_and_c:
                                    b_and_c[seg] = []
                                b_and_c[seg].append(number)
                                if gn!=entry:
                                    print('Something off with b_and_c for',entry_name,'gn',gn,'entry',entry)
                else: #human but not in proteins
                    # print(entry_name," human but no annotation")
                    self.logger.error('{} is human but has no annotation'.format(entry_name))
                    continue
            #continue
            # self.logger.info('Parsed Seq and B&C {}'.format(entry_name))
            # print(counter,entry_name,"make residues")
            # continue
            pconf = p

            al = []
            bulk = []
            bulk_alt = []

            current = time.time()

            if len(s)<10:
                print(counter,entry_name,"Something wrong with sequence")
            for i,aa in enumerate(s, start=1):
                # if i<170 or i>190:
                #     continue
                res = self.generate_bw(i,v,aa)
                segment = self.all_segments[res['s']]

                ##perform bulges / constriction check! 
                ## only do this on bw numbers
                if 'bw' in res['numbers']:
                    seg, number = res['numbers']['bw'].split(".")
                    gn = self.b_and_c_check(b_and_c,number,seg)
                    res['numbers']['generic_number'] = seg+"x"+gn


                # print("\t",res)

                bulk_info = create_or_update_residue(pconf, segment, self.schemes,res,b_and_c)
                bulk.append(bulk_info[0])
                bulk_alt.append(bulk_info[1])

                al.append(res)

            bulked = Residue.objects.bulk_create(bulk)
            rs = Residue.objects.filter(protein_conformation=pconf).order_by('sequence_number')

            ThroughModel = Residue.alternative_generic_numbers.through
            bulk = []
            for i,res in enumerate(rs):
                for alt in bulk_alt[i]:
                    bulk.append(ThroughModel(residue_id=res.pk, residuegenericnumber_id=alt.pk))
            ThroughModel.objects.bulk_create(bulk)
            end = time.time()
            diff = round(end - current,1)
            self.logger.info('{} {} residues ({}) {}s alignemt {}'.format(p.protein.entry_name,len(rs),human_ortholog,diff,aligned_gn_mismatch_gap))
            if aligned_gn_mismatch_gap>10:
                #print(p.protein.entry_name,len(rs),"residues","(",human_ortholog,")",diff,"s", " Unaligned generic numbers: ",aligned_gn_mismatch_gap)
                self.logger.error('{} {} residues ({}) {}s MANY ERRORS IN ALIGNMENT {}'.format(p.protein.entry_name,len(rs),human_ortholog,diff,aligned_gn_mismatch_gap))

        self.logger.info('COMPLETED ANNOTATIONS PROCESS {}'.format(positions))

    def compare_human_to_orthologue(self, human, ortholog, annotation,counter):

        v = self.data["NonXtal_SegEnds_Prot#"][human.entry_name]
        s = self.data["Seqs"][human.entry_name]['Sequence']
        human_seq = self.data["Seqs"][human.entry_name]['Sequence']
        b_and_c = {}
        for entry,gn in self.data["NonXtal_Bulges_Constr_GPCRdb#"][human.entry_name].items():
            if len(entry)<3:
                continue
            if entry[1]=='x' or entry[2]=='x':
                if gn!='' and gn!="":
                    seg, number = entry.split("x")
                    if seg not in b_and_c:
                        b_and_c[seg] = []
                    b_and_c[seg].append(number)

        al = []
        for i,aa in enumerate(s, start = 1):
            # i += 1 #fix, since first postion is 1
            res = self.generate_bw(i,v,aa)

            segment = self.all_segments[res['s']]

            ##perform bulges / constriction check! 
            ## only do this on bw numbers
            if 'bw' in res['numbers']:
                seg, number = res['numbers']['bw'].split(".")
                gn = self.b_and_c_check(b_and_c,number,seg)

                res['numbers']['generic_number'] = seg+"x"+gn

            al.append(res)

        matrix = matlist.blosum62
        gap_open = -10
        gap_extend = -0.5

        # print(human.sequence)
        # print(ortholog.sequence)



        # for i, r in enumerate(a[0].seq, 1):
        #     print(i,r,a[1][i-1]) #print alignment for sanity check
        #     # find reference positions
        #     ref_positions = {}
        #     ref_positions_in_ali = {}
        #     for position_generic_number, rp in template_ref_positions.items():
        #         gaps = 0
        #         for i, r in enumerate(a[0].seq, 1):
        #             if r == "-":
        #                 gaps += 1
        #             if i-gaps == rp:
        #                 ref_positions_in_ali[position_generic_number] = i
        #     for position_generic_number, rp in ref_positions_in_ali.items():
        #         gaps = 0
        #         for i, r in enumerate(a[1].seq, 1):
        #             if r == "-":
        #                 gaps += 1
        #             if i == rp:
        #                 ref_positions[position_generic_number] = i - gaps

        #return ref_positions

       # pw2 = pairwise2.align.localms(human.sequence, ortholog.sequence, 2, 0, -2, -.5)

        if ortholog.entry_name not in self.pw_aln_error and human.entry_name not in self.pw_aln_error and 1==2:
            pw2 = pairwise2.align.globalds(human_seq, ortholog.sequence, matrix, gap_open, gap_extend)
            aln_human = pw2[0][0]
            aln_ortholog = pw2[0][1]
        else:
            # write sequences to files
            seq_filename = "/tmp/" + ortholog.entry_name + ".fa"
            with open(seq_filename, 'w') as seq_file:
                seq_file.write("> ref\n")
                seq_file.write(human_seq + "\n")
                seq_file.write("> seq\n")
                seq_file.write(ortholog.sequence + "\n")

            try:
                ali_filename = "/tmp/"+ortholog.entry_name +"_out.fa"
                acmd = ClustalOmegaCommandline(infile=seq_filename, outfile=ali_filename, force=True)
                stdout, stderr = acmd()
                pw2 = AlignIO.read(ali_filename, "fasta")
            except:
                return False

            aln_human = pw2[0]
            aln_ortholog = pw2[1]


        wt_lookup = {} #used to match WT seq_number to WT residue record
        pdbseq = {} #used to keep track of pdbseq residue positions vs index in seq
        ref_positions = {} #WT postions in alignment
        mapped_seq = {} # index by human residues, with orthologue position (if there)

        gaps = 0
        unmapped_ref = {}
        mismatch = 0
        aligned_gn = 0
        aligned_gn_mismatch = 0
        aligned_gn_mismatch_gap = 0


        for i, r in enumerate(aln_human, 1): #loop over alignment to create lookups (track pos)
           #  print(i,r,pw2[1][i-1]) #print alignment for sanity check
            if r!=aln_ortholog[i-1]:
                mismatch += 1
            if r == "-":
                gaps += 1
            if r != "-":
                ref_positions[i] = i-gaps
                if len(al)>=(i-gaps):
                    if 'bw' in al[i-gaps-1]['numbers']:
                        aligned_gn += 1
                        if aln_ortholog[i-1]=='-':
                            aligned_gn_mismatch_gap +=1
                        if r!=aln_ortholog[i-1]:
                            aligned_gn_mismatch += 1
                            # print(i,r,pw2[0][1][i-1],al[i-gaps-1]['numbers'],'MisMatch')
                        else:
                            pass
                            # print(i,r,pw2[0][1][i-1],al[i-gaps-1]['numbers'])
                else:
                    print('odd error in alignment',human.entry_name,ortholog.entry_name,len(human_seq),len(al),i-gaps)
            elif r == "-":
                ref_positions[i] = None

            if aln_ortholog[i-1]=='-':
                unmapped_ref[i-gaps] = '-'

        gaps = 0
        for i, r in enumerate(aln_ortholog, 1): #make second lookup
            if r == "-":
                gaps += 1
            if r != "-":
                if ref_positions[i]:
                    mapped_seq[ref_positions[i]] = i-gaps

        # print(counter,human.entry_name,ortholog.entry_name,ortholog.species.common_name,aligned_gn,aligned_gn_mismatch,aligned_gn_mismatch_gap)

        return mapped_seq,aligned_gn_mismatch_gap