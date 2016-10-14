from django.conf import settings

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.PDB import *
from Bio.PDB.PDBIO import Select
from residue.models import Residue
from structure.functions import BlastSearch, MappedResidue

import Bio.PDB.Polypeptide as polypeptide
import os,logging

logger = logging.getLogger("protwis")

#==============================================================================
#Class for annotating the pdb structures with generic numbers
class GenericNumbering(object):
    
    
    residue_list = ["ARG","ASP","GLU","HIS","ASN","GLN","LYS","SER","THR","HID","PHE","LEU","ILE","TYR","TRP","VAL","MET","PRO","CYS","ALA","GLY"]
  
    def __init__ (self, pdb_file=None, pdb_filename=None, structure=None, blast_path='blastp',
        blastdb=os.sep.join([settings.STATICFILES_DIRS[0], 'blast', 'protwis_blastdb']),top_results=1):
    
        # pdb_file can be either a name/path or a handle to an open file
        self.pdb_file = pdb_file
        self.pdb_filename = pdb_filename
        
        # dictionary of 'MappedResidue' object storing information about alignments and bw numbers
        self.residues = {}
        self.pdb_seq = {} #Seq('')
        # list of uniprot ids returned from blast
        self.prot_id_list = []
        #setup for local blast search
        self.blast = BlastSearch(blast_path=blast_path, blastdb=blastdb,top_results=top_results)
        
        if self.pdb_file:
            self.pdb_structure = PDBParser(PERMISSIVE=True, QUIET=True).get_structure('ref', self.pdb_file)[0]
        elif self.pdb_filename:
            self.pdb_structure = PDBParser(PERMISSIVE=True, QUIET=True).get_structure('ref', self.pdb_filename)[0]
        else:
            self.pdb_structure = structure

        self.parse_structure(self.pdb_structure)


    def parse_structure(self, pdb_struct):
        """
        extracting sequence and preparing dictionary of residues
        bio.pdb reads pdb in the following cascade: model->chain->residue->atom
        """
        for chain in pdb_struct:
            self.residues[chain.id] = {}
            self.pdb_seq[chain.id] = Seq('')
            
            for res in chain:
            #in bio.pdb the residue's id is a tuple of (hetatm flag, residue number, insertion code)
                if res.resname == "HID":
                    resname = polypeptide.three_to_one('HIS')
                else:
                    if res.resname not in self.residue_list:
                        continue
                    self.residues[chain.id][res.id[1]] = MappedResidue(res.id[1], polypeptide.three_to_one(res.resname))
    
            self.pdb_seq[chain.id] = ''.join([self.residues[chain.id][x].name for x in sorted(self.residues[chain.id].keys())])
            
            for pos, res in enumerate(sorted(self.residues[chain.id].keys()), start=1):
                self.residues[chain.id][res].pos_in_aln = pos


    def locate_res_by_pos (self, chain, pos):

        for res in self.residues[chain].keys():
            if self.residues[chain][res].pos_in_aln == pos:
                return res
        return 0


    def map_blast_seq (self, prot_id, hsps, chain):
    
        #find uniprot residue numbers corresponding to those in pdb file
        q_seq = list(hsps.query)
        tmp_seq = list(hsps.sbjct)
        subj_counter = hsps.sbjct_start	
        q_counter = hsps.query_start
        
        logger.info("{}\n{}".format(hsps.query, hsps.sbjct))
        logger.info("{:d}\t{:d}".format(hsps.query_start, hsps.sbjct_start))

        rs = Residue.objects.prefetch_related('display_generic_number', 'protein_segment').filter(
            protein_conformation__protein=prot_id)
        residues = {}
        for r in rs:
            residues[r.sequence_number] = r

        while tmp_seq:
            #skipping position if there is a gap in either of sequences
            if q_seq[0] == '-' or q_seq[0] == 'X' or q_seq[0] == ' ':
                subj_counter += 1
                tmp_seq.pop(0)
                q_seq.pop(0)
                continue
            if tmp_seq[0] == '-' or tmp_seq[0] == 'X' or tmp_seq[0] == ' ':
                q_counter += 1
                tmp_seq.pop(0)
                q_seq.pop(0)
                continue
            if tmp_seq[0] == q_seq[0]:
                resn = self.locate_res_by_pos(chain, q_counter)
                if resn != 0:
                    if subj_counter in residues:
                        db_res = residues[subj_counter]
                        
                        if db_res.protein_segment:
                            segment = db_res.protein_segment.slug
                            self.residues[chain][resn].add_segment(segment)

                        if db_res.display_generic_number:
                            num = db_res.display_generic_number.label
                            bw, gpcrdb = num.split('x')
                            gpcrdb = "{}.{}".format(bw.split('.')[0], gpcrdb)
                            self.residues[chain][resn].add_bw_number(bw)
                            self.residues[chain][resn].add_gpcrdb_number(gpcrdb)
                            self.residues[chain][resn].add_gpcrdb_number_id(db_res.display_generic_number.id)
                            self.residues[chain][resn].add_display_number(num)
                            self.residues[chain][resn].add_residue_record(db_res)
                    else:
                        logger.warning("Could not find residue {} {} in the database.".format(resn, subj_counter))

                    
                    if prot_id not in self.prot_id_list:
                        self.prot_id_list.append(prot_id)
            q_counter += 1
            subj_counter += 1
            tmp_seq.pop(0)
            q_seq.pop(0)        
    
                    
    def get_substructure_mapping_dict(self):

        mapping_dict = {}
        for chain in self.residues.keys():
            for res in self.residues[chain].keys():
                if self.residues[chain][res].segment in mapping_dict.keys():
                    mapping_dict[self.residues[chain][res].segment].append(self.residues[chain][res].number)
                else:
                    mapping_dict[self.residues[chain][res].segment] = [self.residues[chain][res].number,]
        return mapping_dict


    def get_annotated_structure(self):
    
        for chain in self.pdb_structure:
            for residue in chain:
                if residue.id[1] in self.residues[chain.id].keys():
                    if self.residues[chain.id][residue.id[1]].gpcrdb != 0.:
                        residue["CA"].set_bfactor(float(self.residues[chain.id][residue.id[1]].gpcrdb))
                    if self.residues[chain.id][residue.id[1]].bw != 0.:
                        residue["N"].set_bfactor(float(self.residues[chain.id][residue.id[1]].bw))
      
        return self.pdb_structure
  
  
    def save_gn_to_pdb(self):
    
        #replace bfactor field of CA atoms with b-w numbers and return filehandle with the structure written
        for chain in self.pdb_structure:
            for residue in chain:
                if residue.id[1] in self.residues[chain.id].keys():
                    if self.residues[chain.id][residue.id[1]].gpcrdb != 0.:
                        residue["CA"].set_bfactor(float(self.residues[chain.id][residue.id[1]].gpcrdb))
                    if self.residues[chain.id][residue.id[1]].bw != 0.:
                        residue["N"].set_bfactor(float(self.residues[chain.id][residue.id[1]].bw))
                    r = self.residues[chain.id][residue.id[1]]
        #get the basename, extension and export the pdb structure with b-w numbers
        root, ext = os.path.splitext(self.pdb_filename)
        io=PDBIO()
        io.set_structure(self.pdb_structure)
        io.save("%s_GPCRDB%s" %(root, ext))
           
    
    def assign_generic_numbers(self):
        
        alignments = {}
        #blast search goes first, looping through all the chains
        for chain in self.pdb_seq.keys():
            alignments[chain] = self.blast.run(self.pdb_seq[chain])
            
        #map the results onto pdb sequence for every sequence pair from blast
        for chain in self.pdb_seq.keys():
            for alignment in alignments[chain]:
                if alignment == []:
                    continue
                for hsps in alignment[1].hsps:
                    self.map_blast_seq(alignment[0], hsps, chain)
        return self.get_annotated_structure()
