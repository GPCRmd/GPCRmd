#let's python
from .uniprotkb_utils import valid_uniprotkbac, retreive_data_uniprot, retreive_protein_names_uniprot, get_other_names, retreive_fasta_seq_uniprot, retreive_isoform_data_uniprot, retreive_isoform_data_uniprot
from contextlib import closing
from django.db import connection
from django.utils import timezone
from django.conf import settings
from GPCRuniprot import GPCRlist

fh=open('./dynadb/chunk1_from5487587_to_8107333.sdf','r')
complexes=[] #each complex has: the ligand InchiKey, the list of uniprot codes which form the PROTEIN part of the complex, Ki, IC50, Kd, EC50
uniflag=0 
ligflag=0
lines_list=[]
i=0
reference={}
for line in fh:
    lines_list.append(line)


protlist=[]
while i<len(lines_list):
    if '$$$$' in lines_list[i]:
        if (len(kd)>0 or len(ec50)>0):
            #for uni in protlist:
                #if uni in GPCRlist:
            complexes.append([ligkey,liginchi, pubchem_id, chembl_id,protlist,kd,ec50,ki,ic50,reference]) 
            protlist=[]
            reference={}
        else:
            protlist=[]
            reference={} 
    
    if '<Ligand InChI Key>' in lines_list[i]:
        ligkey=lines_list[i+1].strip()
    if '<Ligand InChI>' in lines_list[i]:
        liginchi=lines_list[i+1].strip()
    elif '<UniProt (SwissProt) Primary ID of Target Chain>' in lines_list[i]: #we are only using SwissProt, because trEMBLE is predicted.
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
        kd=kd.replace(">", "")
        kd=kd.replace("<", "")
    elif '<EC50 (nM)>' in lines_list[i]:
        ec50=lines_list[i+1].strip()
        ec50=ec50.replace(">", "")
        ec50=ec50.replace("<", "")
    elif '> <Authors>' in lines_list[i]:
        reference['authors']=lines_list[i+1].strip()
    elif '> <Article DOI>' in lines_list[i]:
        reference['DOI']=lines_list[i+1].strip()
    elif '> <Link to Ligand-Target Pair in BindingDB>' in lines_list[i]:
        reference['bindingdblink']=lines_list[i+1].strip()

    i+=1

fh.close()

#print('Complexes FOUND:', complexes)
complexcounter=0
for comple in complexes: #423 last record
    kd=comple[5]
    ec_fifty=comple[6]
    '''
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
            cursor.execute('INSERT INTO dyndb_exp_interaction_data (type, id_complex_exp) VALUES ('+complextype+','+i+' RETURNING id') #WORKS            
    ##################################################################################################
    '''


    print('Record the complex exp')
    with closing(connection.cursor()) as cursor:
        #Create the complex_exp record
        cursor.execute('INSERT INTO dyndb_complex_exp DEFAULT VALUES RETURNING id') #WORKS!
        complex_id=cursor.fetchone()[0] #returns the id of the last insert command
        if len(kd)>0:
            complextype=1
        elif len(ec_fifty)>0:
            complextype=2
        else:
            complextype=0 #functional



        #Create the complex_exp_interaction_data record
        cursor.execute('INSERT INTO dyndb_exp_interaction_data (type, id_complex_exp) VALUES (%s, %s) RETURNING id', (str(complextype),str(complex_id))) #WORKS

        complex_interaction_id=cursor.fetchone()[0] #returns the id of the last insert command




    print('Complex recorded. Now, record the kinetic values')
    if complextype==1: #kd, binding
        with closing(connection.cursor()) as cursor:
            cursor.execute('INSERT INTO dyndb_binding (id, rvalue,units,description) VALUES (%s, %s, %s, %s)', (str(complex_interaction_id),str(kd),'nM','some description'))

    if complextype==2: #ec_50, efficacy
        with closing(connection.cursor()) as cursor:
            cursor.execute('INSERT INTO dyndb_efficacy (id, rvalue,units,description,reference_id_compound) VALUES (%s, %s, %s, %s, %s)', (str(complex_interaction_id),str(ec_fifty),'nM','some description','2')) 

    print('kinetics recorded. Now, record the protein')

    #Create the protein and the complexprotein, if it does not exist
    for uniprot in comple[4]:
        if len(DyndbProtein.objects.filter(uniprotkbac=uniprot).filter(is_mutated=False))>0:
            prot_id=DyndbProtein.objects.filter(uniprotkbac=uniprot).filter(is_mutated=False)[0].id
            print('Protein already existed, no need to record')
        else:
            seqdata,errdata = retreive_fasta_seq_uniprot(uniprot) #THIS FAILES SOMETIMES! do they block my ip? 
            namedata,errdata = retreive_protein_names_uniprot(uniprot)
            print('seqdata and namedata',seqdata,namedata)
            seqdata=seqdata['sequence'] #to insert in dyndb_protein_sequence sometimes this does not work because of the retrieval process
            namedata=namedata['RecName'][0]['Full'][0]
            with closing(connection.cursor()) as cursor:
                cursor.execute(
                    'INSERT INTO dyndb_protein (uniprotkbac,name,is_mutated,isoform,id_uniprot_species) VALUES (%s, %s, %s, %s, %s) RETURNING id', (uniprot,namedata,'False','1','11463')
                )

                prot_id=cursor.fetchone()[0]
                cursor.execute(
                    'INSERT INTO dyndb_protein_sequence (id_protein,sequence,length) VALUES (%s, %s, %s)', (prot_id,seqdata,len(seqdata))
                )

        with closing(connection.cursor()) as cursor:
            cursor.execute(
                'INSERT INTO dyndb_complex_protein (id_complex_exp,id_protein) VALUES (%s, %s)', (complex_id,prot_id)
            )
        


    #Create the ccompound and complxcompound, if it does not exist
    print('Protein recorded, now the compound')
    if len(DyndbCompound.objects.filter(pubchem_cid=comple[2]))>0:
        compound_id=DyndbCompound.objects.filter(pubchem_cid=comple[2])[0].id
        print('compound already existed, mo need to record it')
    else:
        pubchem_id=comple[2]
        iupac,errdata = retreive_compound_data_pubchem_post_json('cid',pubchem_id,operation='property',outputproperty='IUPACName')
        iupac=iupac['PropertyTable']['Properties'][0]['IUPACName']
        names,errdata = retreive_compound_data_pubchem_post_json('cid',pubchem_id,operation='synonyms') #different names
        for name in names['InformationList']['Information'][0]['Synonym']:
            if len(name)<60:
                defname=name
                break
        names=defname
        sinchi,errdata = retreive_compound_data_pubchem_post_json('cid',pubchem_id,operation='property',outputproperty='InChI')
        sinchi=sinchi['PropertyTable']['Properties'][0]['InChI']
        sinchikey,errdata=retreive_compound_data_pubchem_post_json('cid',pubchem_id,operation='property',outputproperty='InChIKey')
        sinchikey=sinchikey['PropertyTable']['Properties'][0]['InChIKey']
        print('trying to record the comopund...')
        with closing(connection.cursor()) as cursor:
            print('THIS IS THE NAME',names)
            cursor.execute('INSERT INTO dyndb_compound (name, iupac_name,pubchem_cid,sinchi,sinchikey) VALUES (%s, %s, %s, %s, %s) RETURNING id', (names,iupac,pubchem_id,sinchi,sinchikey) )
            compound_id=cursor.fetchone()[0]
        print('success! now the complex compound...')

    with closing(connection.cursor()) as cursor:
        cursor.execute(
            'INSERT INTO dyndb_complex_compound (id_compound,id_complex_exp) VALUES (%s, %s)', (compound_id,complex_id)
        )
    print('Compound recorded. EVERYTHING WENT WELL. $$$$$$$$$$$$$.',complexcounter)
    complexcounter+=1
        
    

'''
from contextlib import closing
from django.db import connection
aa=[]
with closing(connection.cursor()) as cursor:
    cursor.execute("SELECT accession FROM protein")
    rows=cursor.fetchall()
    for row in rows:
        if row[0] != None:
            aa.append(row[0])
    print(aa)
'''
