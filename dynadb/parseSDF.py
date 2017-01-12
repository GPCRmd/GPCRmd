#let's python
from .uniprotkb_utils import valid_uniprotkbac, retreive_data_uniprot, retreive_protein_names_uniprot, get_other_names, retreive_fasta_seq_uniprot, retreive_isoform_data_uniprot, retreive_isoform_data_uniprot
from contextlib import closing
from django.db import connection
from django.utils import timezone
from django.conf import settings
fh=open('fewmolecules.sdf','r')
complexes=[] #each complex has: the ligand InchiKey, the list of uniprot codes which form the PROTEIN part of the complex, Ki, IC50, Kd, EC50
uniflag=0 
ligflag=0
lines_list=[]
i=0

for line in fh:
    lines_list.append(line)


protlist=[]
while i<len(lines_list):
    if '$$$$' in lines_list[i]:
        complexes.append([ligkey,liginchi, pubchem_id, chembl_id,protlist,kd,ec50,ki,ic50]) 
        protlist=[]
    if '<Ligand InChI Key>' in lines_list[i]:
        ligkey=lines_list[i+1].strip()
    if '<Ligand InChI>' in lines_list[i]:
        liginchi=lines_list[i+1].strip()
    elif '<UniProt (SwissProt) Primary ID of Target Chain>' in lines_list[i]:
        protlist.append(lines_list[i+1].strip())
    elif '<UniProt (TrEMBL) Primary ID of Target Chain>' in lines_list[i]:
        protlist.append(lines_list[i+1].strip())
    elif '<PubChem CID>' in lines_list[i]: 
        pubchem_id=lines_list[i+1].strip()
    elif '<ChEMBL ID of Ligand>' in lines_list[i]:
        chembl_id=lines_list[i+1].strip()
    elif '<Ki (nM)>' in lines_list[i]:
        ki=lines_list[i+1].strip()
        ki=ki.replace(">", "")
        ki=ki.replace("<", "")
    elif '<IC50 (nM)>' in lines_list[i]:
        ic50=lines_list[i+1].strip()
        ic50=ic50.replace(">", "")
        ic50=ic50.replace("<", "")
    elif '<Kd (nM)>' in lines_list[i]:
        kd=lines_list[i+1].strip()
        kd=kd50.replace(">", "")
        kd=kd50.replace("<", "")
    elif '<EC50 (nM)>' in lines_list[i]:
        ec50=lines_list[i+1].strip()
        ec50=ec50.replace(">", "")
        ec50=ec50.replace("<", "")

    i+=1

fh.close()

for comple in complexes:  #need to change to inside other for loop, for every chunk.

    ##################################################################################################
    # Check if that combination of ligand and target already exists. Transform it into tablesearch and use NiceSearcher to retrieve the complex
    # [[' ', ' ', 'protein', '1', 'true', '', '5-hydroxytryptamine-receptor', '  '], ['AND', ' ', 'compound', '1', 'orto', '', 'Clozapine', '  ']]
    query_array=[]
    for uniprot in comple[4]:
        pkprot=DyndbProtein.objects.filter(uniprotkbac=uniprot).filter(is_mutated=False)[0].id
        query_array.append(['AND', ' ', 'protein', str(pkprot), 'true', '', '5-hydroxytryptamine-receptor', '  '])#'5-hydroxytryptamine-receptor' is not really used, so we leave it
    pubchem_id=comple[2]
    compound_id=DyndbCompound.objects.filter(pubchem_cid=pubchem_id)[0].id
    query_array.append(['AND', ' ', 'compound', str(compound_id), 'orto', '', 'Clozapine', '  ']) #'Clozapine' is not really used, so we leave it
    query_array[0][0]=' ' #first element has no boolean!
    resultlist=main(query_array,'complex')
    for i in resultlist:
        if exactmatchtest(arrays_def,'complex',i)=='pass':
            #do not create again that cexp!
            cursor.execute('INSERT INTO dyndb_exp_interaction_data (type, id_complex_exp,ligand1,ligand2,protein1,protein2) VALUES ('+complextype+','+i+','+comple[4]+','+comple[5]+') RETURNING id') #WORKS            
    ##################################################################################################


    #Create the complex_exp record
    with closing(connection.cursor()) as cursor:
        cursor.execute('INSERT INTO dyndb_complex_exp DEFAULT VALUES RETURNING id') #WORKS!
        complex_id=cursor.fetchone()[0] #returns the id of the last insert command
        if len(kd)>0:
            complextype=1
        elif len(ec_fifty)>0;
            complextype=2
        else:
            complextype=0 #functional
        #Create the complex_exp_interaction_data record
        cursor.execute('INSERT INTO dyndb_exp_interaction_data (type, id_complex_exp,ligand1,ligand2,protein1,protein2) VALUES ('+complextype+','+complex_id+','+comple[4]+','+comple[5]+') RETURNING id') #WORKS
        complex_id=cursor.fetchone()[0] #returns the id of the last insert command
        
    #Create the protein and the complexprotein, if it does not exist
    for uniprot in comple[4]:
        if len(DyndbProtein.objects.filter(uniprotkbac=uniprot).filter(is_mutated=False))>0:
            prot_id=DyndbProtein.objects.filter(uniprotkbac=uniprot).filter(is_mutated=False)[0].id
        else:
            seqdata,errdata = retreive_fasta_seq_uniprot(uniprot)
            namedata,errdata = retreive_protein_names_uniprot(uniprot)
            seqdata=seqdata['sequence'] #to insert in dyndb_protein_sequence
            namedata=namedata['RecName'][0]['Full'][0]
            with closing(connection.cursor()) as cursor:
                cursor.executemany(
                    'INSERT INTO dyndb_protein (uniprotkbac,name,is_mutated,isoform) VALUES ('+uniprot+', '+namedata+', False,'+'1 );'
                )
                prot_id=cursor.fetchone()[0]
                cursor.executemany(
                    'INSERT INTO dyndb_protein_sequence (id_protein,sequence,length) VALUES ('+prot_id+', '+seqdata+','+len(seqdata)+');'
                )
        with closing(connection.cursor()) as cursor:
            cursor.executemany(
                'INSERT INTO dyndb_complex_protein (id_complex_exp,id_protein) VALUES ('+complex_id+', '+prot_id+');'
            )
        
    #Create the ccompound and complxcompound, if it does not exist
    if len(DyndbCompound.objects.filter(pubchem_cid=comple[2]))>0:
        compound_id=DyndbCompound.objects.filter(pubchem_cid=comple[2])[0].id
    else:
        pubchem_id=comple[2]
        iupac,errdata = retreive_compound_data_pubchem_post_json('cid',pubchem_id,operation='property',outputproperty='IUPACName')
        iupac=iupac['PropertyTable']['Properties'][0]['IUPACName']
        names,errdata = retreive_compound_data_pubchem_post_json('cid',pubchem_id,operation='synonyms') #different names
        names=names['InformationList']['Information'][0]['Synonym'][0]
        sinchi,errdata = retreive_compound_data_pubchem_post_json('cid',pubchem_id,operation='property',outputproperty='InChI')
        sinchi=sinchi['PropertyTable']['Properties'][0]['InChIKey']
        sinchikey,errdata=retreive_compound_data_pubchem_post_json('cid',pubchem_id,operation='property',outputproperty='InChIKey')
        sinchikey=sinchikey['PropertyTable']['Properties'][0]['IUPACName']
        #cids,errdata = retreive_compound_data_pubchem_post_json('cid',,operation='cids') #returns the CID of that smiles
        #cids=cids['IdentifierList']['CID'][0]
        with closing(connection.cursor()) as cursor:
            cursor.execute('INSERT INTO dyndb_compound (name, iupac_name,pubchem_cid,sinchi,sinchikey) VALUES ('+names+','+iupac+','+pubchem_id+','+sichi+','+sinchikey') RETURNING id')
            compound_id=cursor.fetchone()[0]

    with closing(connection.cursor()) as cursor:
        cursor.executemany(
            'INSERT INTO dyndb_complex_compound (id_compound,id_complex_exp) VALUES ('+compound_id+', '+complex_id+');'
        )
