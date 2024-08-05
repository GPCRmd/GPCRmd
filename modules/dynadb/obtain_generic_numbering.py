from Bio import Align
from Bio.Seq import Seq
from modules.dynadb.models import DyndbDynamics,DyndbProtein,DyndbModeledResidues,DyndbFilesDynamics,DyndbModel
from modules.protein.models import Protein,ProteinFamily
import MDAnalysis as mda
import re
from django.conf import settings
import requests

three_to_one = {'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C',
                'GLN': 'Q', 'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
                'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
                'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V'}

def get_protein_name(uniprot_id):
    base_url = "https://www.uniprot.org/uniprot/"
    query_url = f"{base_url}{uniprot_id}.txt"

    try:
        response = requests.get(query_url)
        response.raise_for_status()
        content = response.text
        for line in content.splitlines():
            if line.startswith("ID"):
                gene_name = line.split()[1].lower()
                return gene_name
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        return None


def obtain_class(dyn_id):
    """
    Obtain GPCR class of the GPCR in a certain dynamic
    """

    fam_d={"001":"A","002":"B","003":"B","004":"C","005":"F","006":"F","007":"Others"} # We'll treat class T as part of F until further notice
    DP = DyndbProtein.objects.filter(dyndbsubmissionprotein__submission_id__dyndbdynamics__pk=dyn_id,prot_type=1)
    # If simulation has any GPCR
    if len(DP):
        dp = DP[0] # Take first one, we are not ready to deal with multiGPCR systems
        # Take GPCRdb slug. First part of it defines GPCR class
        p = dp.receptor_id_protein
        if p:
            fam_slug = dp.receptor_id_protein.family.slug
            fam_code=fam_slug.split("_")[0]
            fam=fam_d[fam_code]
            return fam
        else:
            print('GPCR has no receptor name associated. Class left unefined')
            return False
    else:
        print('DynID %d has no GPCR'%dyn_id)
        return False

def extract_chain_sequence(pdb_file, chain_id):
    """
    Extract the sequence in residue ids and residue names of a particular chain from a structure file
    """

    # Load the PDB file using MDAnalysis
    u = mda.Universe(pdb_file)

    # Select atoms belonging to the specified chain
    chain_atoms = u.select_atoms(f"chainid {chain_id}")
    

    # Extract resname sequence of specified chain. In one-letter code
    seq = []
    for residue in chain_atoms.residues:
        resname = three_to_one[residue.resname] if residue.resname in three_to_one else 'X'
        seq.append(resname)
    resname_seq = ''.join(seq)

    # Extract residue information for the specified chain
    resid_list = [str(residue.resid) for residue in chain_atoms.residues]
    resname_list = [str(residue.resname) for residue in chain_atoms.residues]

    return(resname_seq, resname_list, resid_list)

def generic_numbering(dyn_id, prot = 'gpcr'):
    """
    Obtain generic numbering for GPCRs or G proteins (gpcr/gprot)
    """

    print(prot)
    # Take prot type id, as it is in DyndbProtein
    prot_types = { 'gpcr' : 1, 'gprot' : 2, 'arr' : 3}
    prot_type = prot_types[prot]

    # Obtain protein object of GPCRs/G-prots in this dynamic. 
    DP = DyndbProtein.objects.filter(dyndbsubmissionprotein__submission_id__dyndbdynamics__pk=dyn_id,prot_type=prot_type)
    if len(DP):

        # Obtain uniprot name of this GPCR/Gprot
        if prot == 'gpcr':
            dp = DP[0]
            if dp.receptor_id_protein:
                prot_name = dp.receptor_id_protein.entry_name
            else:
                print('GPCR has no receptor name associated. Class left unefined')
                return {}
        # Else is gprot/b-arrestin
        else: 
            # We are only interested in G protein alpha subunit
            if prot=='gprot':
                DP = DP.filter(name__contains='alpha')

            if len(DP):
                uniprot = DP[0].uniprotkbac
                P = Protein.objects.filter(accession=uniprot)
                dp = DP[0]
                if len(P):
                    prot_name = P[0].entry_name
                else:
                    prot_name = get_protein_name(uniprot)
            else:
                print('no alpha G prot avaliable. Skipping')
                return {}

        # Extract chainID from the first ModeledResidues entry associated to this protein  
        dm = DyndbModel.objects.filter(dyndbsubmissionmodel__submission_id__dyndbdynamics__id=dyn_id)[0] 
        prot_chain =  DyndbModeledResidues.objects.filter(id_protein=dp.id,id_model=dm.pk)[0].chain.upper() 

        # Load coordinates file of this dynamic using biopythin, and extract
        strucfile = settings.MEDIA_ROOT+DyndbFilesDynamics.objects.get(id_dynamics=dyn_id,type=0).id_files.filepath
        (dyn_seq_str, dyn_resnames, dyn_resids) = extract_chain_sequence(strucfile, prot_chain)
        dyn_seq = Seq(dyn_seq_str)


        # Download standard sequence of this receptor type, and extract sqeuence
        residues_list = requests.get('https://gpcrdb.org/services/residues/extended/%s/'%prot_name).json()
        gpcrdb_gennum = { res['sequence_number'] : res['display_generic_number'] for res in residues_list}
        gpcrdb_seq = Seq("".join([ residue["amino_acid"] for residue in residues_list ]))
        gpcrdb_resids = list(gpcrdb_gennum.keys())

        # Skip if protein is not in uniprot
        if not len(gpcrdb_resids):
            print('DynID %d protein %s has no uniprot. Skipping...'%(dyn_id,prot))
            return {}

        # Align with the structure residues
        aligner = Align.PairwiseAligner()
        aligner.mismatch_score = -1
        aligner.extend_gap_score = -0.1
        aligner.open_gap_score = -4
        alignment = aligner.align(dyn_seq, gpcrdb_seq)[0]

        # Correcting resid -> bw association
        alig_dyn_coords = [int(i) for i in alignment.indices[0]]
        alig_gpcrdb_coords = [int(i) for i in alignment.indices[1]]
        residues_data = {}
        for n in range(0, alignment.shape[1]):

            # Skip if gap in Dynamics file sequence (deletion)
            if (alig_dyn_coords[n] != -1):
                
                # These are the sequence indices in the alignment
                gpcrdb_al_pos = alig_gpcrdb_coords[n]
                dyn_al_pos = alig_dyn_coords[n]

                # Obtain resIDs of the current aligned positions, and generic numbering too
                gpcrdb_resid = gpcrdb_resids[gpcrdb_al_pos]
                gpcrdb_resname = gpcrdb_seq[gpcrdb_al_pos]
                gennum = gpcrdb_gennum[int(gpcrdb_resid)]
                dyn_resid = dyn_resids[dyn_al_pos]
                dyn_resname = dyn_resnames[dyn_al_pos]
                pos = "%s-%s-%s"%(dyn_resid,prot_chain,dyn_resname)

                # If not insertion and gennum actually exists
                if (alig_gpcrdb_coords[n] != -1) and gennum:
                    # In GPCR gen-nums, preserve only GPCRdb nomenclature
                    gennum_std = re.sub(r'\.\d+', '', gennum) if prot=='gpcr' else gennum
                    # Save generic numbering info into dictionary
                    residues_data[gennum_std] = pos 

    else:
        try:
            print('DynID %s has no %s'%(dyn_id,prot))
        except:
            print('DynID %s has no protein'%(dyn_id))
        return {}

    return residues_data
