from django.core.management.base import BaseCommand, CommandError
import MDAnalysis as mda
from MDAnalysis.analysis import align
from MDAnalysis.analysis.rms import rmsd
from django.conf import settings
import os
from dynadb.models import DyndbModel, DyndbDynamics, DyndbFiles, DyndbModelComponents
import urllib.request
import re
import mdtraj as md
from dynadb.pipe4_6_0 import useline2, d
import pickle
import numpy as np
import transforms3d

class Command(BaseCommand):
    help = "Retrieves the transformation matrix corresponding to the alignment between our model PDBs and the x-ray PDBs. This will be used to align the ED map of the x-ray structure to our model and simulation."
    def add_arguments(self, parser):
        parser.add_argument(
           '--sub',
            dest='submission_id',
            nargs='*',
            action='store',
            default=False,
            help='Specify submission id(s) for which the matrix will be precomputed.'
        )
        parser.add_argument(
           '--dyn',
            dest='dynamics_id',
            nargs='*',
            action='store',
            default=False,
            help='Specify dynamics id(s) for which the matrix will be precomputed. '
        )
        parser.add_argument(
            '--ignore_publication',
            action='store_true',
            dest='ignore_publication',
            default=False,
            help='Consider both published and unpublished dynamics.',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrites already generated matrices.',
        )

    def handle(self, *args, **options):
        def obtain_lig_li(dyn_id):
            comp=DyndbModelComponents.objects.filter(id_model__dyndbdynamics=dyn_id)
            lig_li=[]
            for c in comp:
                ctype=c.type
                if ctype ==1:
                    lig_li.append(c.resname)
            return lig_li
        def seq_from_pdb(filepath,sel_chain_li):
            fpdb=open(filepath,'r')
            onlyaa=""
            resnum_pre=False
            
            for line in fpdb:
                if useline2(line):
                    chain=line[21]
                    resnum=line[22:26].strip()
                    aa=line[17:20]
                    if not sel_chain_li or (chain in sel_chain_li):
                        if resnum != resnum_pre:
                            resnum_pre=resnum
                            try:
                                onlyaa+=d[aa]
                            except: #Modified aminoacid
                                onlyaa+="X"
            fpdb.close()
            return (onlyaa)

        root = settings.MEDIA_ROOT
        EDmap_path=os.path.join(root,"Precomputed/ED_map")
        if not os.path.isdir(EDmap_path):
            os.makedirs(EDmap_path)
        tmp_path=os.path.join(EDmap_path,"tmp")
        if not os.path.isdir(tmp_path):
            os.makedirs(tmp_path)

        if options['ignore_publication']:
            dynobj=DyndbDynamics.objects.all()
        else:
            dynobj=DyndbDynamics.objects.filter(is_published=True)
        if options['submission_id']:
            dynobj=dynobj.filter(submission_id__in=options['submission_id'])
        if options['dynamics_id']:
            dynobj=dynobj.filter(id__in=options['dynamics_id'])
        if dynobj == []:
            self.stdout.write(self.style.NOTICE("No dynamics found with specified conditions."))

        for dyn in dynobj:
            dyn_id=dyn.id

            pdbfile_li=DyndbFiles.objects.filter(dyndbfilesdynamics__id_dynamics=dyn_id, id_file_types=2)
            if pdbfile_li:
                ref_filepath=pdbfile_li[0].filepath
                if len(pdbfile_li) >1:
                    self.stdout.write(self.style.NOTICE("More than one coordinate file found for dyn %s. Only considering %s" % (dyn_id,ref_filepath)))
            else:
                self.stdout.write(self.style.NOTICE("No coordinate file found for dyn %s. Skipping. " % (dyn_id)))
                continue
            ref_fileroot=re.search("([\w_]*)\.pdb$",ref_filepath).group(1)
            matrix_datafile=os.path.join(EDmap_path,"dyn_%s_transfmatrix.data"%dyn_id)

            try:
                self.stdout.write(self.style.NOTICE("\nObtaining matrix for dynamics with id %d"%dyn_id))
                model=DyndbModel.objects.select_related("id_protein","id_complex_molecule").get(dyndbdynamics__id=dyn_id)
                pdbid_wchain=model.pdbid
                if "." in pdbid_wchain:
                    (pdbid,pdbchain)=pdbid_wchain.split(".")
                    pdbchainli=[pdbchain]
                else:
                    pdbid=pdbid_wchain
                    pdbchain=False
                    pdbchainli=False
                pdburl="https://files.rcsb.org/download/"+pdbid+".pdb"
                mobile_filepath=os.path.join(tmp_path,pdbid+".pdb")
                urllib.request.urlretrieve(pdburl,mobile_filepath )


                mobile = mda.Universe(mobile_filepath)
                # For some reason I cannot open that with MDanalysis. So I will open it with MDtraj and save (that can be opened). I will take the oportunity to filter only the protein and ligand
                ref_filepath_filt=os.path.join(tmp_path,ref_fileroot+"_filt.pdb")
                ref_struc=md.load(ref_filepath)

                lig_li=obtain_lig_li(dyn_id)
                lig_li=["resname "+lig for lig in lig_li]
                res_sel=" or ".join(lig_li)
                if res_sel:
                    fin_sel="protein or "+res_sel
                else:
                    fin_sel="protein"
                ref_struc_sel=ref_struc.topology.select(fin_sel)
                ref_struc.atom_slice(atom_indices=ref_struc_sel,inplace=True)
                ref_struc.save(ref_filepath_filt)
                
                ref = mda.Universe(ref_filepath_filt)

                # Now I need to generate the fasta needed as input for fasta2select, which gives us the selection of mathing segments of the two structures
                ref_chains=[]
                ref_segids=[]
                for m in model.dyndbmodeledresidues_set.all():
                    ref_chains.append(m.chain)
                    ref_segids.append(m.segid)
                ref_seq=seq_from_pdb(ref_filepath,ref_chains)
                if not ref_seq:
                    self.stdout.write(self.style.ERROR("Error extracting sequence of reference structure. Skipping." ))
                    continue
                mob_seq=seq_from_pdb(mobile_filepath,pdbchainli)
                if not mob_seq:
                    if pdbchainli:
                        self.stdout.write(self.style.ERROR("Chain %s not found in mobile structure. Skipping." % pdbchain ))
                    else:
                        self.stdout.write(self.style.ERROR("Error extracting sequence of mobile structure. Skipping." ))
                    continue
                fasta_filepath=os.path.join(tmp_path,"dyn_%s.fasta"%dyn_id)
                f = open(fasta_filepath, "w+")
                f.write("#Ref\n") 
                f.write(ref_seq+"\n")
                f.write("#Mob\n") 
                f.write(mob_seq+"\n")
                f.close()


                aln_filepath=os.path.join(tmp_path,"dyn_%s.aln"%dyn_id)
                ref_resids=[a.resid for a in ref.select_atoms('name CA and (%s)'%" or ".join(["segid %s"%sid for sid in ref_segids]))] 
                if pdbchainli:
                    target_resids=[a.resid for a in mobile.select_atoms('name CA and segid %s'%pdbchain)] # if there are no segid, chain is used as segid
                else:
                    target_resids=[a.resid for a in mobile.select_atoms('name CA')]
                clustalw_path="clustalw"
                
                equivalent_res= mda.analysis.align.fasta2select(fasta_filepath, ref_resids=ref_resids, target_resids=target_resids,
                    clustalw=clustalw_path, alnfilename=aln_filepath)
                ref_selection=equivalent_res["reference"]
                mobile_selection=equivalent_res["mobile"]

                #Time to obtain the rotation and translation
                mobile0 = mobile.select_atoms(mobile_selection).select_atoms("name CA").positions - mobile.atoms.center_of_mass()
                ref0 = ref.select_atoms(ref_selection).select_atoms("name CA").positions - ref.atoms.center_of_mass()
                R, rmsd = align.rotation_matrix(mobile0, ref0)

                trans=ref.select_atoms(ref_selection).select_atoms("name CA").center_of_mass()- mobile.select_atoms(mobile_selection).select_atoms("name CA").center_of_mass()

                r_angl=transforms3d.euler.mat2euler(R)

                with open(matrix_datafile, 'wb') as filehandle:  
                    # store the data as binary data stream
                    pickle.dump([r_angl,trans], filehandle)

                #to open:
#                    with open('/protwis/sites/files/Precomputed/ED_map/dyn_4_transfmatrix.data', 'rb') as filehandle:  
#                        (r_angl,trans) = pickle.load(filehandle)

                #remove tmp files
                for filenm in os.listdir(tmp_path):
                    os.remove(os.path.join(tmp_path,filenm))
                os.rmdir(tmp_path) 

                self.stdout.write(self.style.SUCCESS("Transformation matrix successfully generated at %s"%matrix_datafile))
            except Exception as e:
                self.stdout.write(self.style.ERROR(e))
        else:
            self.stdout.write(self.style.NOTICE("Transformation matrix already exists for dyn %s. Skipping."%dyn_id))




#ref = mda.Universe(ref_filepath)
#mobile = mda.Universe(mobile_filepath)
#
##Return selection strings that will select equivalent residues.
#fasta_filepath="/protwis/sites/files/tests/ED_map/fasta/ed_map.fasta"
#alnfilename="/protwis/sites/files/tests/ED_map/fasta/ed_map.aln"
#ref_resids=[a.resid for a in ref.select_atoms('name CA')] 
#target_resids=[a.resid for a in mobile.select_atoms('name CA')]
#clustalw_path="clustalw"
#
#equivalent_res= mda.analysis.align.fasta2select(fasta_filepath, ref_resids=ref_resids, target_resids=target_resids,
    #clustalw=clustalw_path, alnfilename=alnfilename)
#ref_selection=equivalent_res["reference"]
#mobile_selection=equivalent_res["mobile"]
#mobile_atoms=mobile.select_atoms(mobile_selection)
#mobile0 = mobile_atoms.select_atoms("name CA").positions - mobile_atoms.center_of_mass()
#ref_atoms=ref.select_atoms(ref_selection)
#ref0 = ref_atoms.select_atoms("name CA").positions - ref_atoms.center_of_mass()
#R, rmsd = align.rotation_matrix(mobile0, ref0)
#
#r_angl=transforms3d.euler.mat2euler(R)
#trans=ref.select_atoms(ref_selection).select_atoms("name CA").center_of_mass()- mobile.select_atoms(mobile_selection).select_atoms("name CA").center_of_mass()
#
