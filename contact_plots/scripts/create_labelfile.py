from sys import argv
import string
from os.path import basename,splitext
from re import sub,compile

def create_labelfile(info_dictfile, outname, outfolder = "./", ligand = None):
	"""
	The idea of this function is to create a label file (get_contacts format) with the ballesteros GPCR id's as labels for a certain model.
	info_dictfile should contain a dictionary-like text file with this format:
		{'POSITION-CHAIN-RESIDUE': BALLESTEROS_ID, ... }
	The optional argument "ligand" corresponds to a file with the PDB identifier of the molecule ligand and its label. Example
	NUMBER CHAIN RESIDUE Ligand
	"""

	#Dictionary with aminoacid codes (label files require 3-letter code)
	AAs =  {'C': 'CYS', 'D': 'ASP', 'S': 'SER', 'Q': 'GLN', 'K': 'LYS',
     'I': 'ILE', 'P': 'PRO', 'T': 'THR', 'F': 'PHE', 'N': 'ASN', 
     'G': 'GLY', 'H': 'HIS', 'L': 'LEU', 'R': 'ARG', 'W': 'TRP', 
     'A': 'ALA', 'V': 'VAL', 'E': 'GLU', 'Y': 'TYR', 'M': 'MET'}

	#Reading dictionary file with the Ballesteros numeration for this protein sequence
	dictfile = eval(open(info_dictfile, 'r').read())

	#open a output label file. It's name will be the same as the pdb, but with a _label.tsv at the end
	outfile_name = outfolder + outname + "_labels.tsv"
	outfile = open(outfile_name,'w')
	outdict = {}

	#Iterate over residues in the dictionary, and extract its corresponding aminoacid type from the PDB
	pattern = compile("-\d\d")
	for ballesteros_id in dictfile:
		AA = dictfile[ballesteros_id]
		#Split by the dash that separates chainame and AA number
		AA_splited = AA.split("-")
		number = AA_splited[0]
		chain = AA_splited[1]
		type_res = AAs[AA_splited[2]]
		ballesteros_id = ballesteros_id.replace(".","-")
		ballesteros_id_cuted = sub(pattern,"",ballesteros_id)
		outdict[int(number)] = ("%s:%s:%s\t%s\n" %(chain, type_res,number, ballesteros_id_cuted))

	#Print a new label file with the results
	for AA in sorted(outdict):

		outfile.write(outdict[AA])

	# If there's a ligandfile specified, add its content as a label at the end of the labelfile
	if ligand is not None:
		ligandfile = open(ligand, "r")

		# Iterate over lines. Split by blank, catch second element as label and first as residue name
		for line in ligandfile:
			ligand_splited = line.split()
			number = ligand_splited[0]
			chain = ligand_splited[1]
			type_res = ligand_splited[2]
			outfile.write("%s:%s:%s\t%s\n" %(chain, type_res,number, "Ligand"))

	#Close output file
	outfile.close()

create_labelfile(argv[1], argv[2], argv[3], argv[4])
