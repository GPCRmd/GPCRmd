from django.conf import settings
from Bio.Align import PairwiseAligner
#from Bio.pairwise2 import format_alignment
#from Bio.Alphabet import generic_protein
from Bio import AlignIO
import re
import os
import io
#The pipeline: get sequence from pdb (checkpdb function) -> compare sequence from pdb to the fasta sequence (matchpdbfa) -> modify pdb to make it match the fasta numbering (repairpdb). 

#The way to detect which format is used is to check if the residue after resid 9999 is 2710. if after 9999 there is a 2710 then all coming numbers are hexadecimal. If after 9999 comes 10000 they are using the insertion code. 

d={'CYSF': 'C', 'OLS': 'S', 'HE6': 'H', 'HEX': 'H', 'CCY0': 'C', 'TRP': 'W', 'TYR': 'Y', 'HEJ': 'H', 'CCY1': 'C', 'CM2L': 'K', 'HDY': 'H', 'HEB': 'H', 'CYSL': 'C', 'NCY4': 'C', 'ASN1': 'N', 'DAB': 'X', 'CCY6': 'C', 'HE4': 'H', 'CYX': 'C', 'CH2E': 'H', 'ARGN': 'R', 'CSEP': 'S', 'HES': 'H', 'ASPH': 'D', 'LYSH': 'K', 'HEG': 'H', 'CCYM': 'C', 'NASH': 'D', 'HDQ': 'H', 'GLYM': 'G', 'OLP': 'P', 'HD9': 'H', 'HS2': 'H', 'HSE': 'H', 'NCY8': 'C', 'HEL': 'H', 'HID': 'H', 'CY0': 'C', 'PTR': 'T', 'HEI': 'H', 'HEY': 'H', 'HD3': 'H', 'M2L': 'K', 'Y1P': 'Y', 'NPTR': 'T', 'HSC': 'H', 'HDT': 'H', 'NY1P': 'Y', 'MELE': 'L', 'NCY6': 'C', 'NCCS': 'C', 'CY7': 'C', 'LYS': 'K', 'ILE': 'I', 'HEC': 'H', 'CHYP': 'P', 'HEH': 'H', 'CT2P': 'T', 'KCX': 'K', 'NCY1': 'C', 'CH2D': 'H', 'NM3L': 'K', 'CACK': 'K', 'CM3L': 'K', 'ACK': 'K', 'HISA': 'H', 'HEU': 'H', 'CCY4': 'C', 'ALY': 'K', 'CASH': 'D', 'HDK': 'H', 'CCME': 'C', 'NH1E': 'H', 'HDH': 'H', 'HIS2': 'H', 'ASP': 'D', 'NCY3': 'C', 'LSN': 'K', 'HD7': 'H', 'CNLN': 'N', 'HISE': 'H', 'CS1P': 'S', 'CY8': 'C', 'NOLP': 'P', 'HSD': 'H', 'SEP': 'S', 'COLT': 'T', 'HD8': 'H', 'CSRM': 'R', 'NM2L': 'K', 'CS2P': 'S', 'HDD': 'H', 'COLS': 'S', 'HEZ': 'H', 'NCYX': 'C', 'GLUP': 'E', 'HDE': 'H', 'NTPO': 'T', 'HDS': 'H', 'NS2P': 'S', 'CCS': 'C', 'NLE': 'L', 'CY2P': 'Y', 'CY3': 'C', 'HIN': 'H', 'ASP1': 'A', 'H2E': 'H', 'HISH': 'H', 'NCY9': 'C', 'MGY': 'G', 'CH1D': 'H', 'NSRM': 'R', 'CCY9': 'C', 'NDAB': 'X', 'NNLN': 'N', 'CY6': 'C', 'CYSG': 'C', 'CHIP': 'H', 'SER': 'S', 'CDRM': 'R', 'OLT': 'T', 'LYN': 'K', 'GLY': 'G', 'NH2D': 'H', 'PHEU': 'F', 'ASN': 'N', 'HET': 'H', 'HDO': 'H', 'HD4': 'H', 'HEE': 'H', 'HE7': 'H', 'DHSE': 'H', 'HE3': 'H', 'CDAB': 'X', 'MLYS': 'K', 'NLN': 'N', 'HEP': 'H', 'MLEU': 'L', 'Y2P': 'Y', 'CGUP': 'E', 'NT2P': 'T', 'CY9': 'C', 'T1P': 'T', 'HIS1': 'H', 'HDV': 'H', 'HDB': 'H', 'HIS': 'H', 'HEM': 'H', 'HDX': 'H', 'M3L': 'K', 'HDW': 'H', 'HDZ': 'H', 'GLUH': 'E', 'GLH': 'E', 'MEVA': 'V', 'SERD': 'S', 'CHID': 'H', 'DRM': 'R', 'HEO': 'H', 'CKCX': 'K', 'NCY0': 'C', 'HEF': 'H', 'CCY5': 'C', 'NCY7': 'C', 'NHYP': 'P', 'NY2P': 'Y', 'HE0': 'H', 'CMLY': 'K', 'MVAL': 'V', 'H2D': 'H', 'SRM': 'R', 'HDC': 'H', 'NT1P': 'T', 'NHID': 'H', 'CARM': 'R', 'HE5': 'H', 'TPO': 'T', 'HDU': 'H', 'LEU': 'L', 'GLU': 'E', 'CTPO': 'T', 'HEK': 'H', 'HE2': 'H', 'MEL': 'L', 'S2P': 'S', 'HDN': 'H', 'CGU': 'E', 'HD5': 'H', 'HD6': 'H', 'AP1': 'D', 'S1P': 'S', 'DHSP': 'H', 'NACK': 'K', 'GLN': 'Q', 'NARM': 'R', 'NCY2': 'C', 'CYS': 'C', 'ARG': 'R', 'HYP': 'P', 'CY1': 'C', 'NHIN': 'H', 'CYSH': 'C', 'HD0': 'H', 'NLYN': 'K', 'NHIP': 'H', 'CY5': 'C', 'CH1E': 'H', 'HDL': 'H', 'HEA': 'H', 'NDRM': 'R', 'NCME': 'C', 'NCYM': 'C', 'CY2': 'C', 'CHIN': 'H', 'HDR': 'H', 'COLP': 'P', 'CCYX': 'C', 'CGLH': 'E', 'MEV': 'V', 'CYS2': 'C', 'HER': 'H', 'HEW': 'H', 'HEQ': 'H', 'HED': 'H', 'ZAFF': 'D', 'HISP': 'H', 'HISD': 'H', 'NGLH': 'E', 'HEV': 'H', 'HDJ': 'H', 'CY1P': 'Y', 'HDM': 'H', 'CY4': 'C', 'THR': 'T', 'NMLY': 'K', 'HDI': 'H', 'MLY': 'K', 'HEN': 'H', 'NSEP': 'S', 'H1D': 'H', 'MET': 'M', 'HIE': 'H', 'NKCX': 'K', 'HD1': 'H', 'NOLT': 'T', 'T2P': 'T', 'ALA': 'A', 'HD2': 'H', 'DHSD': 'H', 'HDP': 'H', 'CYM': 'C', 'HDF': 'H', 'HDA': 'H', 'NS1P': 'S', 'CHIE': 'H', 'CLYN': 'K', 'HISB': 'H', 'ARM': 'R', 'CT1P': 'T', 'CPTR': 'T', 'HSP': 'H', 'CME': 'C', 'HE1': 'H', 'CYSD': 'C', 'PHE': 'F', 'NH2E': 'H', 'CCY3': 'C', 'NH1D': 'H', 'NCY5': 'C', 'PRO': 'P', 'HIP': 'H', 'NHIE': 'H', 'ASPP': 'D', 'CCCS': 'C', 'HE8': 'H', 'VAL': 'V', 'HE9': 'H', 'CYSP': 'C', 'NOLS': 'S', 'CCY2': 'C', 'CCY7': 'C', 'ASH': 'D', 'TRPU': 'W', 'CCY8': 'C', 'HDG': 'H', 'H1E': 'H','CYS':'C', 'ASP':'D', 'SER':'S', 'GLN':'Q', 'LYS':'K', 'ILE':'I', 'PRO':'P', 'THR':'T', 'PHE':'F', 'ASN':'N', 'GLY':'G', 'HIS':'H', 'LEU':'L', 'ARG':'R', 'TRP':'W', 'ALA':'A', 'VAL':'V', 'GLU':'E', 'TYR':'Y', 'MET':'M', 'DCYS':'C', 'DASP':'D', 'DSER':'S', 'DGLN':'Q', 'DLYS':'K', 'DILE':'I', 'DPRO':'P', 'DTHR':'T', 'DPHE':'F', 'DASN':'N', 'DGLY':'G', 'DHIS':'H', 'DLEU':'L', 'DARG':'R', 'DTRP':'W', 'DALA':'A', 'DVAL':'V', 'DGLU':'E', 'DTYR':'Y', 'DMET':'M', 'CCYS':'C', 'CASP':'D', 'CSER':'S', 'CGLN':'Q', 'CLYS':'K', 'CILE':'I', 'CPRO':'P', 'CTHR':'T', 'CPHE':'F', 'CASN':'N', 'CGLY':'G', 'CHIS':'H', 'CLEU':'L', 'CARG':'R', 'CTRP':'W', 'CALA':'A', 'CVAL':'V', 'CGLU':'E', 'CTYR':'Y', 'CMET':'M', 'NCYS':'C', 'NASP':'D', 'NSER':'S', 'NGLN':'Q', 'NLYS':'K', 'NILE':'I', 'NPRO':'P', 'NTHR':'T', 'NPHE':'F', 'NASN':'N', 'NGLY':'G', 'NHIS':'H', 'NLEU':'L', 'NARG':'R', 'NTRP':'W', 'NALA':'A', 'NVAL':'V', 'NGLU':'E', 'NTYR':'Y', 'NMET':'M'}
		
def checkpdb_ngl(name_of_file,segid,start,stop,chain):
	'''Get sequence from a PDB file in a given interval defined by a combination of Segment Identifier (segid), starting residue number (start), end residue number (stop), chain identifier (chain). All can be left in blank. Returns 1) a list of minilist: each minilist has the resid and the aminoacid code. 2) a string with the sequence.'''
	if settings.MEDIA_ROOT[:-1] in name_of_file: 
		fpdb=open(name_of_file,'r')
	else:
		fpdb=open(settings.MEDIA_ROOT[:-1] + name_of_file,'r')
	cpos=0 #current residue position
	ppos=0 #previous residue position
	ppos2='0' #previous position after converting hexadecimals to decimals
	pchain='' #previous chain
	seqplain=list() #list of minilist. each minilist contains the residue number and its aminoacid.
	flag=0
	hexflag=0
	pfields=['','' ,'','AAA','Z','0','0','0','0','']
	for line in fpdb:
		if useline2(line):
			fields=[ '','' ,'' ,line[17:21],line[21],line[22:27],line[31:39],line[39:47],line[47:55],line[72:77]] 
			#fields[3]:Aminoacid code, fields[4]:chain, fields[5]:resid, fields[6-8]:X,Y,Z coordinates
			fields[3]=fields[3].strip() #if it is a standard aa with 3 letters, eliminate whitespace.
			fields[5]=fields[5].strip() #if it is a standard RESID with 4 characters, eliminate whitespace.
			#~ if fields[5]==pfields[5] and fields[3]!=pfields[3]: #avoids that same resid is used by different resnames.
				#~ return 'Corrupted PDB in position: '+pfields[5]+' Same resid has two or more different aminoacid codes/resnames'
			i=3
			while i<9:
				if fields[i].strip()=='':
					return 'Missing required field in the PDB file at line: '+line
				i+=1

			if fields[5]!=pfields[5]: #resid has changed->new aa
				
				if fields[4]!=pfields[4]  or fields[9]!=pfields[9] or fields[5]=='1': #resid count has been reseted by new chain, new segid or whatever. 
					ppos='0'
					flag=0
				cpos=fields[5] #current position (resid) in the pdb during the present loop cycle
				if flag==1:
					cpos2=int(str(cpos),16)
					ppos2=int(str(ppos),16)
				elif flag==0:
					cpos2=int(cpos)
					ppos2=int(ppos)
				if cpos=='2710' and ppos=='9999':
					cpos2=int(cpos,16)
					flag=1
					hexflag=1
				if (fields[4]==chain or chain == '') and cpos2 >= start and cpos2 <= stop and (segid in line[72:77] or segid==''):
					if cpos2>=ppos2+1:
						try:
							seqplain.append([d[fields[3]],cpos,cpos2])
						except: #Modified aminoacid
							seqplain.append(('X',cpos,cpos2))

					elif cpos2<ppos2 and cpos!=1: 
						return 'Residue numbering order is corrupted in position:'+str(cpos2)

			pchain=fields[4]
			pfields=fields
			ppos=cpos

	fpdb.close()
	onlyaa='' #ignore the resids, pick the aa and that is it.
	for minilist in seqplain:
		onlyaa=onlyaa+minilist[0]
	#print(seqplain,onlyaa)
	if len(onlyaa)==0:
		return 'Unable to extract sequence from PDB file. Double check if the elements that define your interval exist: chain, segid, resid.'
	return (seqplain,onlyaa,hexflag)

		
def get_number_segments(pdbname):
	fpdb=open(pdbname,'r')
	cpos=0 #current residue position
	ppos=0 #previous residue position
	ppos2='0' #previous position after converting hexadecimals to decimals
	pchain='' #previous chain
	seqplain=list() #list of minilist. each minilist contains the residue number and its aminoacid.
	breaklines=[]
	flag=0
	hexflag=0
	pfields=['','' ,'','AAA','Z','0','0','0','0','']
	jumps=0
	jumpflag=0
	sequences=[]
	firstsegid=0
	cseq=''
	for line in fpdb:
		if useline(line):
			if firstsegid==0:
				breaklines.append(line.strip())
				firstsegid=1
			fields=[ '','' ,'' ,line[17:21],line[21],line[22:27],line[31:39],line[39:47],line[47:55],line[72:77]] 
			#fields[3]:Aminoacid code, fields[4]:chain, fields[5]:resid, fields[6-8]:X,Y,Z coordinates
			fields[3]=fields[3].strip() #if it is a standard aa with 3 letters, eliminate whitespace.
			fields[5]=fields[5].strip() #if it is a standard RESID with 4 characters, eliminate whitespace.
			#~ if fields[5]==pfields[5] and fields[3]!=pfields[3]: #avoids that same resid is used by different resnames.
				#~ return 'Corrupted PDB in position: '+pfields[5]+' Same resid has two or more different aminoacid codes/resnames'

			if fields[5]!=pfields[5]: #resid has changed->new aa

				if (fields[4]!=pfields[4]  or fields[9]!=pfields[9]) and pfields!=['','' ,'','AAA','Z','0','0','0','0','']: #resid count has been reseted by new chain or new segid. 
					ppos='0'
					flag=0
					jumps+=1
					jumpflag=1
				cpos=fields[5] #current position (resid) in the pdb during the present loop cycle
				if flag==1:
					cpos2=int(str(cpos),16)
					ppos2=int(str(ppos),16)
				elif flag==0:
					cpos2=int(cpos)
					ppos2=int(ppos)
				if cpos=='2710' and ppos=='9999':
					cpos2=int(cpos,16)
					flag=1
					hexflag=1			
					
				if cpos2!=ppos2+1 and jumpflag==0 and ppos2!=0:
					jumps+=1
					jumpflag=1
				elif cpos2<ppos2 and cpos!=1: 
					return 'Residue numbering order is corrupted in position:'+str(cpos2)
					
			elif (fields[4]!=pfields[4] or fields[9]!=pfields[9]) and pfields!=['','' ,'','AAA','Z','0','0','0','0','']:
				jumpflag=1
				jumps+=1

			if jumpflag==1:
				breaklines.append(line.strip())
				sequences.append(cseq)
				if (fields[5]!=pfields[5]) or ((fields[4]!=pfields[4] or fields[9]!=pfields[9]) and pfields!=['','' ,'','AAA','Z','0','0','0','0','']):				
					try:
						cseq=d[fields[3]]
					except KeyError:
						cseq='X'
			else:
				if (fields[5]!=pfields[5]) or ((fields[4]!=pfields[4] or fields[9]!=pfields[9]) and pfields!=['','' ,'','AAA','Z','0','0','0','0','']):				
					try:
						cseq=cseq+d[fields[3]]
					except KeyError:
						cseq=cseq+'X'
								
			pchain=fields[4]
			pfields=fields
			ppos=cpos
			jumpflag=0
			
	sequences.append(cseq) #append last segment, no jump is detected for last segment.
	print(sequences)
	segment_sequence_table=[]
	for i in range(len(breaklines)):
		segment_sequence_table.append(breaklines[i] +' --> '+ sequences[i][:8]+ ' (...)')
	breaklines='<br>'.join(segment_sequence_table)
	fpdb.close()
	return (jumps+1,breaklines)	
		
#############################################################################################################################################

def checkpdb(name_of_file,segid,start,stop,chain):
	'''Get sequence from a PDB file in a given interval defined by a combination of Segment Identifier (segid), starting residue number (start), end residue number (stop), chain identifier (chain). All can be left in blank. Returns 1) a list of minilist: each minilist has the resid and the aminoacid code. 2) a string with the sequence.'''
	fpdb=open(name_of_file,'r')
	startexists=False
	stopexists=False
	cpos=0 #current residue position
	ppos=0 #previous residue position
	ppos2='0' #previous position after converting hexadecimals to decimals
	pchain='' #previous chain
	seqplain=list() #list of minilist. each minilist contains the residue number and its aminoacid.
	flag=0
	hexflag=0
	pfields=['','' ,'','AAA','Z','0','0','0','0','']
	for line in fpdb:
		if useline(line):
			fields=[ '','' ,'' ,line[17:21],line[21],line[22:27],line[31:39],line[39:47],line[47:55],line[72:77]] 
			#fields[3]:Aminoacid code, fields[4]:chain, fields[5]:resid, fields[6-8]:X,Y,Z coordinates
			fields[3]=fields[3].strip() #if it is a standard aa with 3 letters, eliminate whitespace.
			fields[5]=fields[5].strip() #if it is a standard RESID with 4 characters, eliminate whitespace.
			#~ if fields[5]==pfields[5] and fields[3]!=pfields[3]: #avoids that same resid is used by different resnames.
				#~ return 'Corrupted PDB in position: '+pfields[5]+' Same resid has two or more different aminoacid codes/resnames'
			i=3
			while i<9:
				if fields[i].strip()=='':
					return 'Missing required field in the PDB file at line: '+line
				i+=1

			if fields[5]!=pfields[5]: #resid has changed->new aa
				
				if fields[4]!=pfields[4] or fields[9]!=pfields[9] or fields[5]=='1': #resid count has been reseted by new chain, new segid or whatever. 
					ppos='0'
					flag=0
				cpos=fields[5] #current position (resid) in the pdb during the present loop cycle
				if flag==1:
					cpos2=int(str(cpos),16)
					ppos2=int(str(ppos),16)
				elif flag==0:
					cpos2=int(cpos)
					ppos2=int(ppos)
				if cpos=='2710' and ppos=='9999':
					cpos2=int(cpos,16)
					flag=1
					hexflag=1
					
				if (fields[4]==chain or chain == '') and (segid in line[72:77] or segid=='') and cpos2 == start:
					startexists=True
					
				if (fields[4]==chain or chain == '') and (segid in line[72:77] or segid=='') and cpos2 == stop:
					stopexists=True					
					
				if (fields[4]==chain or chain == '') and cpos2 >= start and cpos2 <= stop and (segid in line[72:77] or segid==''):

					if cpos2!=ppos2+1 and ppos2!=0 and (ppos2 >= start and ppos2 <= stop): #if previous position is inside the segment and it is not continuous with the current one:
						return 'Resid numbering is not continous. There is a jump from '+str(ppos2)+' to '+str(cpos2)+'.This means that either the PDB numbering is corrupted or that there is another segment inside the interval you defined. If it is the latter case, define a new segment ending at this point and another one afterwards.'

					elif cpos2<ppos2 and cpos!=1: 
						return 'Residue numbering order is corrupted in position:'+str(cpos2)					
					
					else:
						try:
							seqplain.append([d[fields[3]],cpos,cpos2,str(fields[3]) ])
						except: #Modified aminoacid
							seqplain.append(('X',cpos,cpos2, str(fields[3]))) #include resname to check during alig if X is allowed in sequence or not.

			pchain=fields[4]
			pfields=fields
			ppos=cpos

	fpdb.close()
	onlyaa='' #ignore the resids, pick the aa and that is it.
	for minilist in seqplain:
		onlyaa=onlyaa+minilist[0]

	if len(onlyaa)==0:
		return 'Unable to extract sequence from PDB file. Double check if the elements that define your interval exist: chain, segid, resid.'

	if not startexists:
		return 'Start resid does not exist in the given combination: Start:'+ str(start) +' Stop:'+ str(stop) +' Chain:'+ chain +' Segid:'+ segid
	
	if not stopexists:
		return 'Stop resid does not exist in the given combination: Start:'+ str(start) +' Stop:'+ str(stop) +' Chain:'+ chain +' Segid:'+ segid
	#print(seqplain, "   " , onlyaa)

	return (seqplain,onlyaa,hexflag)


def fasta_to_phylip(align_string):
    """
    Convert a fasta alignment into a nexus-format one
    """

    f = io.StringIO()
    f.write(align_string)
    f.seek(0)
    align = AlignIO.read(f, "fasta") #, alphabet = generic_protein)
    p_alignment = format(align, "phylip")
    return(p_alignment)


#############################################################################################################################################
def select_align(mode, mat_sco, mis_sco, open_gap, ext_gap):
	"""
	The replace of depecrated pairwise2.align.localms, need to use Align.PairwiseAligner from Biopython. 
	"""
	aligner= PairwiseAligner()
	aligner.mode = mode # "local" or "global"
	aligner.match_score = mat_sco #match_score
	aligner.mismatch_score = mis_sco #mismatch_score
	aligner.open_gap_score = open_gap #open gap penalty
	aligner.extend_gap_score = ext_gap #extend gap penalty
	return aligner

def align_wt_mut_global(wtseq,mutseq):
	aligner = select_align("global", 5, -1, -1.5, -1)
	bestalig=aligner.align(wtseq,mutseq)[0]  #,5,-1,-1.5,-1
	return bestalig

def align_wt_mut(wtseq,mutseq):
	aligner = select_align("local", 5, -1, -1.5, -1)
	bestalig=aligner.align(wtseq,mutseq)[0]  #,5,-1,-1.5,-1
	return bestalig
	
def align_wt_mut_viewer(wtseq,mutseq):
	aligner = select_align("local", 5, -1, -1.5, -1.5)
	bestalig=aligner.align(wtseq,mutseq)[0]  #,5,-1,-1.5,-1
	return bestalig
#############################################################################################################################################
natural_aa=['TRP', 'PHE', 'ASN', 'GLY', 'MET', 'VAL', 'ARG', 'PRO', 'LYS', 'GLU', 'TYR', 'ALA', 'THR', 'HIS', 'CYS', 'SER', 'LEU', 'GLN', 'ILE', 'ASP']
non_natural_aa=['CYSL', 'CCY6', 'CHID', 'HED', 'ARGN', 'NGLU', 'NGLH', 'CTHR', 'LYN', 'NCY9', 'OLP', 'CY5', 'HEP', 'CCYX', 'CCME', 'DALA', 'NCY0', 'COLS', 'CY1', 'NACK', 'OLT', 'GLUH', 'NHIP', 'CGLY', 'CYS2', 'DVAL', 'HISP', 'HDX', 'NGLY', 'CH1E', 'HEK', 'NOLS', 'NCY4', 'CCYM', 'DHIS', 'CCY5', 'CY4', 'CCY9', 'ACK', 'NM2L', 'NOLT', 'CY6', 'HDF', 'CGLU', 'HE1', 'CCYS', 'HIN', 'GLH', 'CYSF', 'HEF', 'NTYR', 'CME', 'CS1P', 'HE8', 'CILE', 'S1P', 'CCY4', 'MVAL', 'ASPP', 'NCY8', 'HS2', 'NHIS', 'NTHR', 'NPHE', 'MEV', 'HDU', 'HDE', 'NCCS', 'HIE', 'DHSE', 'NPTR', 'CCY1', 'NVAL', 'HE4', 'HDO', 'HE6', 'CMLY', 'NALA', 'DTHR', 'NOLP', 'CCY8', 'NMET', 'HEJ', 'NCY6', 'DRM', 'NCY7', 'NASP', 'HIS1', 'HSP', 'COLP', 'CARG', 'NLEU', 'MLYS', 'HEA', 'NDRM', 'LYSH', 'CTRP', 'DGLU', 'MEL', 'HDS', 'HE7', 'CCS', 'CT1P', 'HISB', 'CYSP', 'CT2P', 'TRPU', 'CY9', 'HEH', 'HIS2', 'SRM', 'HDC', 'HDW', 'HDV', 'HDK', 'HEQ', 'CNLN', 'HDZ', 'CS2P', 'DPHE', 'CCY2', 'HE5', 'HDL', 'CASH', 'NTPO', 'CGLN', 'PHEU', 'CH2D', 'ARM', 'NH2E', 'NNLN', 'NTRP', 'ASH', 'NARM', 'CMET', 'HDG', 'CALA', 'DGLY', 'NCY5', 'NSEP', 'ALY', 'NY1P', 'CASN', 'MEVA', 'NM3L', 'HEX', 'GLUP', 'CYSG', 'HDA', 'HDR', 'CPRO', 'HSE', 'HEL', 'NLE', 'NCY3', 'NCY1', 'HER', 'HSD', 'CCCS', 'HEG', 'HEN', 'NARG', 'CTPO', 'CY1P', 'NS2P', 'DASP', 'HDH', 'CACK', 'M2L', 'CH1D', 'HD2', 'CSEP', 'HEY', 'H1D', 'NCME', 'HE0', 'CTYR', 'NS1P', 'ASPH', 'CVAL', 'CGLH', 'Y1P', 'DHSD', 'HD7', 'Y2P', 'ZAFF', 'NH1D', 'CH2E', 'CKCX', 'CYSD', 'AP1', 'NCYM', 'DARG', 'NLYS', 'HEW', 'CM2L', 'CGU', 'CHIN', 'HISH', 'HEU', 'NT1P', 'SEP', 'HDQ', 'CYX', 'COLT', 'HISA', 'HD1', 'HDD', 'HE3', 'T2P', 'M3L', 'CHIP', 'CCY7', 'HE9', 'NKCX', 'CYSH', 'GLYM', 'DHSP', 'HEE', 'CY7', 'HD0', 'NPRO', 'H1E', 'CDAB', 'DTYR', 'HEC', 'NSER', 'CYM', 'HSC', 'HEI', 'NH1E', 'NMLY', 'OLS', 'CLEU', 'NCY2', 'DTRP', 'CPHE', 'CDRM', 'NHIN', 'HDM', 'DMET', 'CSER', 'HISD', 'H2E', 'HDP', 'HDY', 'CHIE', 'NHYP', 'CLYN', 'HDJ', 'NY2P', 'HET', 'HD9', 'HDN', 'NLYN', 'NCYS', 'MGY', 'HEO', 'DASN', 'CASP', 'DLYS', 'DILE', 'HID', 'TPO', 'HEZ', 'CCY0', 'HD3', 'DSER', 'HDI', 'NILE', 'NCYX', 'S2P', 'HYP', 'NASH', 'NH2D', 'CY2', 'CM3L', 'CGUP', 'HISE', 'HEV', 'H2D', 'CHIS', 'NHID', 'CLYS', 'HE2', 'MLEU', 'NASN', 'HEM', 'HIP', 'CY2P', 'CY3', 'NDAB', 'T1P', 'NGLN', 'HDB', 'HD5', 'KCX', 'DPRO', 'DLEU', 'PTR', 'HD4', 'HES', 'CY0', 'NSRM', 'NLN', 'DAB', 'DGLN', 'MELE', 'HD6', 'NHIE', 'SERD', 'NT2P', 'ASN1', 'LSN', 'CY8', 'DCYS', 'CSRM', 'HDT', 'CCY3', 'MLY', 'HD8', 'CARM', 'CHYP', 'HEB', 'ASP1', 'CPTR']
def matchpdbfa(sequence,pdbseq,tablepdb,hexflag,start=1):
	'''Get the sequence from database, compare this sequence with the one given in the pdb.
	 Do an alignment to check if the resids are corrupted in the pdb. Returns a table showing
	 the changes in the pdb numbering according to the database sequence.'''
	warningmessage=''
	try:
		aligner = select_align("local", 5, -1, -1.5, -5)
		bestalig=aligner.align(sequence,pdbseq)[0]  #select the aligment with the best score.
		#pairwise2.align.localms(seq1,seq2,score for identical matches, score for mismatches, score for opening a gap, score for extending a gap)
	except:
		return 'Incorrect alignment. Make sure you have defined a correct range of sequence and PDB. '

	biglist=list()
	counterepair=1
	i=0
	pdbalig=bestalig[1] #PDB sequence after alignment
	fastalig=bestalig[0]
	if '-' in fastalig: 
		return 'PDB file contains insertions with respect to fasta, this is not allowed. This is the alignment: <br> PDB <br>:'+str(bestalig[0])+'<br>Submited Sequence:<br>'+str(bestalig[1])
	duos=list()
	mismatchlist=list()
	while i < len(fastalig):
		newpos=i+start  #Sequence from 100 to 150 -> interval_seq= fullseq[100-1:150]-> interval_seq first residue is, actually, 100 of the full seq, That is why we sum the start value. 
		if i+1>9999 and hexflag==1: #hexflag==1 means that the original PDB uses hexadecimal notation
			newpos=format(i+1,'x')	#hexadecimal once 9999 resid is used.

		if pdbalig[i]=='-':
			tablepdb.insert(i,'-')
			try:
				return 'There is a gap in the pdb alignment. That means that you should define a new segment in the table ending before the gap and other one after it. The gap is in position:'+str(tablepdb[i][0])+str(tablepdb[i][1])+'<br> This is the alignment: PDB <br>:'+str(bestalig[0])+'<br>Submited Sequence:<br>'+str(bestalig[1])
			except IndexError:
				return 'There is a gap in the pdb alignment. Maybe you should define a new segment or check if the length of the PDB segment and the sequence match. If your segment is one resid long, put the same resid in res from and res to, also, put the same resid in seq from and seq to. Like: Res from:81 Res to:81; Seq from:81 Seq to:81. Or Res from:81 Res to:81; Seq from:83 Seq to:83 '

		elif fastalig[i]!=pdbalig[i]:
			if fastalig[i]=='X' and tablepdb[i][3] in natural_aa:
				return 'Error: Unknown residue in submited protein sequence but natural/standard resid in its PDB file. Check submited sequence in position:'+str(newpos) + ' and PDB in resid '+ str(tablepdb[i][2])
			elif fastalig[i]=='X' and tablepdb[i][3] in non_natural_aa:
				warningmessage='Warning: Unknown residue in submited protein and non natural resid in its PDB file at position: '+str(tablepdb[i])				
				minilist=[tablepdb[i], [fastalig[i],newpos]]
				duos.append(minilist)
				
			elif tablepdb[i][0]=='X':
				warningmessage='Warning: Unknown residue in PDB file: '+ str(tablepdb[i]) #if you change this, change also checkpdb view to allow this view to detect if the return value is a warning or an error		
				minilist=[tablepdb[i], [fastalig[i],newpos]]
				duos.append(minilist)
							
			else:
				minilist=[tablepdb[i], [fastalig[i],newpos]]	
				mismatchlist.append(minilist)

		else:
			minilist=[tablepdb[i],[fastalig[i],newpos]]
			duos.append(minilist)
		i=i+1

	if len(mismatchlist)>0:
		return ('Error: One or more missmatches were found, this is not allowed. ',mismatchlist) #if you change this, change also checkpdb view to allow this view to detect if the return value is a warning or an error

	if len(warningmessage)>0:
		return (warningmessage,duos)

	#now check if there is any jump/discontinuity in the PDB corrected numbering. If there is, the reason is that there are more that one segments in that user defined interval.
	counter=0
	for minilist in duos:
		if counter>0 and minilist[0][2]!=previous_resid+1:
			return 'There is a jump in the pdb alignment. That means that you should define a new segment in the table. From '+ str(previous_resid) + ' to ' + str(minilist[0][2])
			
		previous_resid=minilist[0][2]
		counter+=1    
	
	return (duos)

#############################################################################################################################################

def matchpdbfa_ngl(sequence,pdbseq,tablepdb,hexflag,start=1):
	'''Get the sequence from database, compare this sequence with the one given in the pdb.
	 Do an alignment to check if the resids are corrupted in the pdb. Returns a table showing
	 the changes in the pdb numbering according to the database sequence.'''

	aligner = select_align("local", 100, -1, -10, -10)
	bestalig=aligner.align(sequence.upper(),pdbseq.upper())[0]  #select the aligment with the best score.
	print(bestalig)
	#pairwise2.align.localms(seq1,seq2,score for identical matches, score for mismatches, score for opening a gap, score for extending a gap)
	#print(bestalig)
	biglist=list()
	counterepair=1
	i=0
	pdbalig=bestalig[1] #PDB sequence after alignment
	fastalig=bestalig[0]
	if '-' in fastalig: 
		return 'PDB file contains insertions with respect to fasta, this is not allowed'
	duos=list()
	mismatchlist=list()
	while i < len(fastalig):
		newpos=i+start  #IT USED TO BE i+1, but now we use start=1 as default!
		if i+1>9999 and hexflag==1: #hexflag==1 means that the original PDB uses hexadecimal notation
			newpos=format(i+1,'x')	#hexadecimal once 9999 resid is used.
		
		if pdbalig[i]=='-':
			tablepdb.insert(i,'-')
			minilist=[tablepdb[i],[fastalig[i],newpos]]
			duos.append(minilist)

		elif fastalig[i]!=pdbalig[i] and pdbalig[i]!='-':
			minilist=[tablepdb[i], [fastalig[i],newpos]]
			duos.append(minilist)
			mismatchlist.append(minilist)

		else:
			minilist=[tablepdb[i],[fastalig[i],newpos]]
			duos.append(minilist)
		i=i+1
		print(minilist)

	if len(mismatchlist)>0:
		return ('One or more missmatches were found, this is not allowed. ',mismatchlist)

	return (duos)
#############################################################################################################################################

def repairpdb(pdbfile, guide,segid,start,stop,chain,counter):	

	'''Takes a pdb file as input, the numbering of this pdb is modified according to the fasta sequence of the PDB whose relation
	 is represented in a schema called guide like: [[A,'27',27],[A,28]] where the first element is the pdb item and the second is the 
	 fasta one. The number between '' can ben in hexadecimal format. The format used to write numbers bigger than 9999 (hexadecimal or insertion code)  in the new PDB file is the same that was used in the original PDB'''

	tmppdbfile=os.path.splitext(pdbfile)[0]
	oldpdb=open(pdbfile, 'r')
	newpdb=open(pdbfile[:-4]+'_corrected'+str(counter)+'.pdb','w')
	count=-1
	pvresid=-1
	pfields=['','' ,'','AAA','Z','0','0','0','0','']
	pchain='Z'
	ppos=0
	for line in oldpdb:
		if useline(line):
			fields=[ '','' ,'' ,line[17:21],line[21],line[22:27],line[31:39],line[39:47],line[47:55],line[72:77]]
			fields[3]=fields[3].strip() #it is a standard aa with 3 letters, eliminate whitespace.
			fields[5]=fields[5].strip() #it is a standard RESID with 4 characters, eliminate whitespace.
			#fields[3]:Aminoacid code, fields[4]:chain, fields[5]:resid, fields[6-8]:coordinates
			cpos=fields[5]
			if fields[4]!=pfields[4] or fields[9]!=pfields[9] or fields[5]=='1': #resid count has been reseted by new chain or whatever. 
				ppos='0'
				flag=0
			if flag==1:
				cpos2=int(str(cpos),16)
				ppos2=int(str(ppos),16)
			elif flag==0:
				cpos2=int(cpos)
				ppos2=int(ppos)
			if cpos=='2710' and ppos=='9999':
				cpos2=int(cpos,16)
				flag=1

			if (fields[4]==chain or chain=='') and cpos2>=start and cpos2<=stop and (segid in line[72:77] or segid==''):
				if fields[5]!=pvresid: #if a new resid is found
					n=1 #count is not refreshed yet. your count is set in the previous aminoacid.
					try:
						while (guide[count+n][0]=='-'): #jump the deletions in the pdb (pdb:12,fasta:12)(pdb:-,fasta:13), (pdb:-,fasta:14), (pdb:13,fasta:15) you can NOT write 13 or 14!
							n=n+1
					except IndexError: #user PDB range has ended but PDB and fasta do not
						newpdb.write(line)
						continue
					count=count+n-1

					count=count+1 #Count gets NOW updated.
				spacesn=4-len(str(guide[count][1][1])) #divide the 4 columns between numbers and spaces.
				newline=line[0:22]+' '*spacesn+str(guide[count][1][1])+' '+line[27:] #the space before line[27:] is to delete the insertion code from AMBER.
				if len(str(guide[count][1][1]))==5: #AMBER notation after 9999 uses 5 digits.
					newline=line[0:22]+str(guide[count][1][1])+line[27:]
				newpdb.write(newline)
				pvresid=fields[5]

			else:
				newpdb.write(line)

			pchain=fields[4]
			ppos=cpos
		elif line.startswith('TER') and fields[4]==chain and cpos2>=start and cpos2<=stop and (segid in line[72:77] or segid==''):
			ter=line[:23]+ (3-len(str(guide[count][1][1])))*' '+str(guide[count][1][1])+'\n'
			newpdb.write(ter)

		elif line.startswith('ENDMDL'):
			break

		else:
			newpdb.write(line)

	newpdb.close()
	oldpdb.close()
	return pdbfile[:-4]+'_corrected'+str(counter)+'.pdb' #'/tmp/'+tmppdbfile[tmppdbfile.rfind('/')+1:]+'_corrected'+str(counter)+'.pdb'
#############################################################################################################################################

def unique(pdbname, usechain=False,usesegid=False):
	'''Checks if a given combination of resid, chain (optional) and segid (optional) ensures that a given resid is unique in the whole PDB file. '''
	flag=0
	pdbset=set()
	oldpdb=open(pdbname,'r')
	pfields=['','' ,'','AAA','Z','0','0','0','0','']
	ppos=0
	atomdic=dict()
	for line in oldpdb:
		line=line.strip()
		if line.startswith('ATOM') or line.startswith('HETATM'):
			#fields[3]:Aminoacid code, fields[4]:chain, fields[5]:resid, fields[6-8]:coordinates
			#fields=[ '','' ,'' ,line[17:20],line[21],line[22:27],line[31:39],line[39:47],line[47:55],line[72:77]]
			fields=[ '','' ,'' ,line[17:21],line[21],line[22:27],line[31:39],line[39:47],line[47:55],line[72:77]]
			fields[3].replace(" ","")
			csegid=fields[9]


			if fields[5]!=pfields[5]: #do not run same aa more than 1 time.

				if (fields[4]!=pfields[4]) or (fields[9]!=pfields[9]) or fields[5].replace(" ","")=='1': #new counting for new chain, segid or whatever
					ppos=0
					flag=0
				if flag==1:
					cpos=int(fields[5],16)
				else:
					cpos=int(fields[5])
				if flag!=1 and (int(pfields[5])==9999 and cpos==2710): #decimal numbers are finished 99999->2710
					cpos=int(str(cpos),16)
					flag=1

				newele=str(cpos)+'_'+line[17:21].replace(" ","")+'_'+fields[4]+'_'+csegid #resid_resname_chain_segid
				if usechain==False:
					if usesegid==False:
						newele=str(cpos)+'_'+line[17:21].replace(" ","")+'_ _ ' #resid_resname
					else:
						newele=str(cpos)+'_'+line[17:21].replace(" ","")+'_ _'+csegid #resid_resname_ _segid

				elif usesegid==False:
					newele=str(cpos)+'_'+line[17:21].replace(" ","")+'_'+fields[4]+'_ ' #resid_resname_chain_

				#check that the selected fields are NOT empty:
				if usechain==True and fields[4].isspace():
					return 'Chain field is empty in:' + newele+ '. Do not use this field or fill it.'
				if usesegid==True and csegid.isspace():
					return 'Segid field is empty in:' + newele + '. Do not use this field or fill it.'
				if newele in pdbset:
					return 'The parameters you have provided do not define a unique aminoacid as: ' + newele + ' is repeated'
					oldpdb.close()
				else:
					pdbset.add(newele)
			pfields=fields
			ppos=cpos
	oldpdb.close()
	return True



#############################################################################################################################################

def useline(line):
	if line.startswith('ATOM') or line.startswith('HETATM'):
		return True

	return False
	
#########################################################################################################################################
	
def useline2(line):
	'''returns True if line starts with ATOM, or HETATM with a resname included in the d dictionary''' 
	if line.startswith('ATOM') or line.startswith('HETATM'):
		trykey=line[17:21]
		trykey=trykey.strip()
		if trykey in d.keys():
			return True
		else:
			return False #this heteroatom is not useful

	else:
		return False

#############################################################################################################################################

def segment_id(pdbname, segid, start, stop, chain):
	'''Looks for gaps in the sequence between start and stop in the given chain and segid ONCE the PDB file has been corrected. If the distance with de previous atom is bigger than 5 units it considers that the two atoms belong to different segments''' 
	seq=list()
	flag=0
	newpdb=open(pdbname,'r')
	pfields=['','' ,'','AAA','Z','0','0','0','0','']
	ppos=0
	ccoor=[0,0,0]
	pcoor=[0,0,0]
	for line in newpdb:
		if useline(line):
			#fields[3]:Aminoacid code, fields[4]:chain, fields[5]:resid, fields[6-8]:coordinates
			fields=[ '','' ,'' ,line[17:21],line[21],line[22:27],line[31:39],line[39:47],line[47:55],line[72:77]]
			fields[3]=fields[3].strip()
			fields[5]=fields[5].strip()
			try:
				ccoor[0]=float(fields[6])
				ccoor[1]=float(fields[7])
				ccoor[2]=float(fields[8])
			except:
				print (fields[6],fields[7],fields[8])
			if fields[5]!=pfields[5]: #do not run same aa more than 1 time.
				if fields[4]!=pfields[4] or fields[9]!=pfields[9] or fields[5]=='1': #different chain and new counting
					ppos=0
					flag=0
				if flag==1:
					cpos=int(fields[5],16)
				else:
					cpos=int(fields[5])

				if flag!=1 and (int(pfields[5])==9999 and cpos==2710): #decimal numbers are finished 99999->2710
					cpos=int(str(cpos),16)
					flag=1
				if (fields[4]==chain or chain=='') and cpos>=start and cpos<=stop and (segid in line[72:77] or segid==''):
					if cpos==ppos+1: #No gap between current and previous position.
						seq.append(d[fields[3]])

					elif cpos>ppos+1: #There is a gap, but is it solded or segmented?
						distance=(((ccoor[0]-pcoor[0])**2)+((ccoor[1]-pcoor[1])**2) + ((ccoor[2]-pcoor[2])**2))**0.5

						if distance < 5: #SOLDED GAP
							for i in range(cpos-ppos-1): #if there is a jump from 2 to 4 #print 1 "-"
								seq.append('-') #seq.append('-'*cpos-ppos-1)
							try:
								seq.append(d[fields[3]])
							except:
								seq.append('X')
						else: #NEW SEGMENT
							for i in range(cpos-ppos-1):
								seq.append('/')
							seq.append('\n') #newline is IMPORTANT to represent the segment jump!

							try:
								seq.append(d[fields[3]])
							except:
								seq.append('X')


			pcoor=ccoor.copy()
			pfields=fields
			ppos=cpos

	newpdb.close()
	fullseq=''.join(seq)
	fullseq.lstrip('/') #delete starting / as they appear due to resid count jumping because of change of chains, etc.
	return fullseq



#############################################################################################################################################

def searchtop(pdbfile,sequence, start,stop,chain='', segid=''):
	'''Takes a PDB file and two resids that define an interval in the PDB, extracts the interval's sequence and aligns it to the one in sequence. '''

	result=checkpdb(pdbfile,segid,start,stop,chain)
	if isinstance(result,str):
		return 'Error in segment definition: Start:'+ str(start) +' Stop:'+ str(stop) +' Chain:'+ chain +' Segid:'+ segid+'\n'+result
	else:
		tablepdb,simplified_sequence,hexflag=result

	aligner = select_align("local", -5, -1, -5, -5)
	bestalig=aligner.align(sequence,simplified_sequence)[0]  #select the aligment with the best score.

	print(bestalig)
	'''
	The resulting alignment should be like:
    ARTNIRRAWLALEKQYL
    ----IRRAWL-------
	'''
	i=0
	flag=0
	warningmessage= ''
	while i<len(bestalig[1]): #bestalig[1] holds the aligned pdbseq
		if bestalig[1][i]!='-' and (bestalig[1][i]!=bestalig[0][i]): #mistmatchs not allowed
			warningmessage= 'Mismatch between PDB sequence and submited protein sequence.\n PDB has '+str(bestalig[1][i])+' while submited sequence has '+ str(bestalig[0][i])+' in resid: '+str(i+1)+ '.\n The suggested "seq from" and "seq to" values might be wrong.' #+1?? not sure!
		if bestalig[1][i]!='-' and flag==0: #find first NON-gap	
			seq_res_from=i+1
			flag=1

		if bestalig[1][i]!='-' and flag==1: #find first gap after the pdb sequence ----------AKLISR-(this one at the left)----------
			seq_res_to=i+1 #keeps adding one until bestalig[1][i]=='-', gap has appeared after the sequence!

		i+=1
  
	if '-' in bestalig[0][seq_res_from-1:seq_res_to] or '-' in bestalig[1][seq_res_from-1:seq_res_to]:
		return 'The selected PDB sequence can not align with the uniprot sequence without gaps.\n This is the aligment between the sequence and the PDB: \n SEQ: '+ str(bestalig[0])+'\n PDB: '+ str(bestalig[1])

	return (seq_res_from, seq_res_to, warningmessage)


#############################################################################################################################################
def main_pdbcheck(pdbname,fastaname,segid='',start=-1,starthex=False,stop=99999,stophex=False,chain='A'): #we need to know if start and stop are hexadecimal or not!
	if starthex is True:
		start=int(str(start),16)
	if stophex is True:
		stop=int(str(stop),16)
	if start>=stop:
		raise Exception('Start resid is larger or equal to the end resid')
		#return 'Start resid is larger or equal to the end resid'
	if len(segid)>4:
		raise Exception('Segid string length is larger than 4 characters.')
		#return 'Segid string length is larger than 4 characters.'

	if uniqueset(pdbname, segid, start, stop, chain):
		tablepdb,simplified_sequence,hexflag=checkpdb(pdbname,segid,start,stop,chain)
		#print('\n',tablepdb,simplified_sequence,'\n')
		guide=matchpdbfa(fastaname,simplified_sequence,tablepdb,hexflag)
		#print(guide,'\n') #Table containing the relation between the numbering of the original PDB file and the corrected one.
		repairpdb(pdbname,guide,segid,start,stop,chain)
		#print(segment_id(pdbname, segid, start, stop, chain),'\n')

