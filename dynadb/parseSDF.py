#let's python
from .uniprotkb_utils import valid_uniprotkbac, retreive_data_uniprot, retreive_protein_names_uniprot, get_other_names, retreive_fasta_seq_uniprot, retreive_isoform_data_uniprot, retreive_isoform_data_uniprot
fh=open('fewmolecules.sdf','r')
complexes=[] #each complex has: the ligand InchiKey, the list of uniprot codes which form the PROTEIN part of the complex, Ki, IC50, Kd, EC50
uniflag=0 
ligflag=0
lines_list=[]
i=0

for line in fh:
    lines_list.append(line)

data,errdata = retreive_data_uniprot('P28222',isoform=1,columns='id,entry name,organism,length,')
data=data['Organism']
seqdata,errdata = retreive_fasta_seq_uniprot('P28222')
namedata,errdata = retreive_protein_names_uniprot('P28222')
seqdata=seqdata['sequence']
namedata=namedata['RecName'][0]['Full'][0]
retreive_isoform_data_uniprot['Displayed'] #should return the isoform


iupac,errdata = retreive_compound_data_pubchem_post_json('smiles','O',operation='property',outputproperty='IUPACName')
iupac=iupac['PropertyTable']['Properties'][0]['IUPACName']
names,errdata = retreive_compound_data_pubchem_post_json('smiles','O',operation='synonyms') #different names
names=names['InformationList']['Information'][0]['Synonym'][0]
cids,errdata = retreive_compound_data_pubchem_post_json('smiles','O',operation='cids') #returns the CID of that smiles
cids=cids['IdentifierList']['CID'][0]


protlist=[]
while i<len(lines_list):
    if '$$$$' in lines_list[i]:
        complexes.append([ligkey,protlist,ki,ic50,kd,ec50]) 
        protlist=[]
    if '<Ligand InChI Key>' in lines_list[i]: #<Ligand InChI>
        ligkey=lines_list[i+1].strip()
    elif '<UniProt (SwissProt) Primary ID of Target Chain>' in lines_list[i]: #<BindingDB Target Chain Sequence> MAYBE THIS IS USEFUL!
        protlist.append(lines_list[i+1].strip())
    elif '<UniProt (TrEMBL) Primary ID of Target Chain>' in lines_list[i]:
       protlist.append(lines_list[i+1].strip())
    elif '<Ki (nM)>' in lines_list[i]:
        ki=lines_list[i+1].strip()
    elif '<IC50 (nM)>' in lines_list[i]:
        ic50=lines_list[i+1].strip()
    elif '<Kd (nM)>' in lines_list[i]:
        kd=lines_list[i+1].strip()
    elif '<EC50 (nM)>' in lines_list[i]:
        ec50=lines_list[i+1].strip()

    i+=1

fh.close()



############################################ RETURNS THE PK OF THE ROW!!! ################################################################## 
#with closing(connection.cursor()) as cursor:
#    cursor.execute('INSERT INTO dyndb_model_components (resname,numberofmol,type, id_model, id_molecule) VALUES (1,21,7,11,3) RETURNING id')
#    aa=cursor.fetchone()[0]
############################################################################################################################################
from contextlib import closing
from django.db import connection
from django.utils import timezone
from django.conf import settings

with closing(connection.cursor()) as cursor: #works without putting any ID!
    cursor.execute('INSERT INTO dyndb_model_components (resname,numberofmol,type, id_model, id_molecule) VALUES (1,21,7,4,6)') #AUTMOATIC PK!!

for comple in complexes:
    with closing(connection.cursor()) as cursor:
        cursor.execute('INSERT INTO dyndb_complex_exp (ki, ic_fifty, kd, ec_fifty) VALUES ('+comple[2]+','+comple[3]+','+comple[4]+','+comple[5]+') RETURNING id') #WORKS
        complex_id=cursor.fetchone()[0] #returns the id of the last insert command
        if len(kd)>0:
            complextype=1
        elif len(ec_fifty)>0;
            complextype=2
        else:
            complextype=3 #functional

        cursor.execute('INSERT INTO dyndb_exp_interaction_data (type, id_complex_exp,ligand1,ligand2,protein1,protein2) VALUES ('+complextype+','+complex_id+','+comple[4]+','+comple[5]+') RETURNING id') #WORKS
        complex_id=cursor.fetchone()[0] #returns the id of the last insert command
        

    for uniprot in comple[1]:
        #prot_id=DyndbProtein.objects.filter(uniprotkbac=uniprot,is_mutaded=false)[0].id
        seqdata,errdata = retreive_fasta_seq_uniprot(uniprot)
        namedata,errdata = retreive_protein_names_uniprot(uniprot)
        seqdata=seqdata['sequence'] #to insert in dyndb_protein_sequence
        namedata=namedata['RecName'][0]['Full'][0]
        with closing(connection.cursor()) as cursor:
            cursor.executemany(
                'INSERT INTO DyndbProtein (uniprotkbac,name,is_mutated,isoform) VALUES ('+uniprot+', '+namedata+', False,'+'1');'
            )
            prot_id=cursor.fetchone()[0]
            cursor.executemany(
                'INSERT INTO DyndbComplexProtein (id_complex_exp,id_protein) VALUES ('+complex_id+', '+prot_id+');'
            )
        
    #compound_id=DyndbCompound.objects.filter(sinchikey=comple[0])[0].id
    iupac,errdata = retreive_compound_data_pubchem_post_json('smiles','O',operation='property',outputproperty='IUPACName')
    iupac=iupac['PropertyTable']['Properties'][0]['IUPACName']
    names,errdata = retreive_compound_data_pubchem_post_json('smiles','O',operation='synonyms') #different names
    names=names['InformationList']['Information'][0]['Synonym'][0]
    cids,errdata = retreive_compound_data_pubchem_post_json('smiles','O',operation='cids') #returns the CID of that smiles
    cids=cids['IdentifierList']['CID'][0]
    with closing(connection.cursor()) as cursor:
        cursor.execute('INSERT INTO dyndb_compound (name, iupac_name,pubchem_cid,sinchi,sinchikey) VALUES ('+names+','+iupac+','+cids+','+comple[0]+','+comple[0]') RETURNING id')
        compound_id=cursor.fetchone()[0]

    with closing(connection.cursor()) as cursor:
        cursor.executemany(
            'INSERT INTO DyndbComplexCompound (id_compound,id_complex_exp) VALUES ('+compound_id+', '+complex_id+');'
        )
