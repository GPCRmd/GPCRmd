#let's python
from .uniprotkb_utils import valid_uniprotkbac, retreive_data_uniprot, retreive_protein_names_uniprot, get_other_names, retreive_fasta_seq_uniprot, retreive_isoform_data_uniprot, retreive_isoform_data_uniprot
from contextlib import closing
from django.db import connection
from django.utils import timezone
from django.conf import settings
from GPCRuniprot import GPCRlist

fh=open('./dynadb/chunk1_from5487587_to_8107333.sdf','r') #chunk1_from5487587_to_8107333.sdf chunk0_from2870096_to_5487587.sdf
complexes=[] #each complex has: the ligand InchiKey, the list of uniprot codes which form the PROTEIN part of the complex, Ki, IC50, Kd, EC50
uniflag=0 
ligflag=0
lines_list=[]
i=0
reference={}
for line in fh:
    lines_list.append(line)

protlist=[]
seqlist=[]
while i<len(lines_list):#make sure the last line is parsed.
    if '$$$$' in lines_list[i]:
        if (len(kd)>0 or len(ec50)>0):
            #for uni in protlist:
                #if uni in GPCRlist:
            complexes.append([ligkey,liginchi, pubchem_id, chembl_id,protlist,kd,ec50,ki,ic50,reference,seqlist]) 
            protlist=[]
            seqlist=[]
            reference={}
        else:
            protlist=[]
            reference={} 
    
    if '<Ligand InChI Key>' in lines_list[i]:
        j=i+1
        while '> <' not in lines_list[j]:
            ligkey+=lines_list[j].strip()
            j+=1


    if '<Ligand InChI>' in lines_list[i]:
        j=i+1
        while '> <' not in lines_list[j]:
            liginchi+=lines_list[j].strip()
            j+=1


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
        reference['authors']=''
        j=i+1
        while '> <' not in lines_list[j]:
            reference['authors']+=lines_list[j].strip()
            j+=1


    elif '> <Article DOI>' in lines_list[i]:
        reference['DOI']=''
        j=i+1
        while '> <' not in lines_list[j]:
            reference['DOI']+=lines_list[j].strip()
            j+=1
        reference['DOI']=lines_list[i+1].strip()


    elif '> <Link to Ligand-Target Pair in BindingDB>' in lines_list[i]:
        reference['bindingdblink']=''
        j=i+1
        while '> <' not in lines_list[j]:
            reference['bindingdblink']+=lines_list[j].strip()
            j+=1

    elif '> <BindingDB Target Chain Sequence>' in lines_list[i]:
        sequence=''
        j=i+1
        while '> <' not in lines_list[j]:
            sequence+=lines_list[j].strip()
            j+=1
        seqlist.append(sequence)

    i+=1

fh.close()

complexcounter=0
for comple in complexes:
    with closing(connection.cursor()) as cursor:

        kd=comple[5]
        ec_fifty=comple[6]

        if len(kd)>0:
            complextype=1
        elif len(ec_fifty)>0:
            complextype=2
        else:
            complextype=0 #functional

        #Check if combination of ligand and target exists. Transform it into tablesearch and use NiceSearcher to retrieve the complex
        # [[' ', ' ', 'protein', '1', 'true', '', '5-receptor', '  '], ['AND', ' ', 'compound', '1', 'orto', '', 'Clozapine', '  ']]

        query_array=[]
        flag=0 #check if either the protein or the compound is new to the database, if it is, do not perform NiceSearch as it is useless.
        unicount=0 
        while unicount<len(comple[4]) and flag==0:#for uniprot in comple[4]:
            uniprot=comple[4][unicount]
            binsequence=comple[10][unicount]
            proteindb=DyndbProteinSequence.objects.filter(sequence=binsequence)
            if len(proteindb)>0:
                pkprot=proteindb[0].id_protein
                query_array.append(['AND', ' ', 'protein', str(pkprot), False, '', '5-hydroxytryptamine-receptor', '  ']) #the name doesnt matter, but false yes! change it depending on the protein! WARNING! 'true' and False.
            else:
                flag=1
            unicount+=1

        pubchem_id=comple[2]
        compdb=DyndbCompound.objects.filter(pubchem_cid=pubchem_id)
        if len(compdb)>0:
            compound_id=compdb[0].id
            query_array.append(['AND', ' ', 'compound', str(compound_id), 'orto', '', 'Clozapine', '  ']) #'Clozapine' is not really used, so we leave it
        else:
            flag=1
        complex_interaction_id='undef'
        exactest=0
        if flag==0: #if either the protein or the compound is not present, then, we are sure that a complex containing them does not exist.
            query_array[0][0]=' ' #first element has no boolean!
            resultlist=main(query_array,'complex')
            for i in resultlist:
                if exactmatchtest(query_array,'complex',i)=='pass':
                    print('complex already exists, no need to record again. Its ID is:',i,' its components are: ',comple)
                    exactest=1
                    #do not create again that cexp!
                    complex_id=i
                    cursor.execute('INSERT INTO dyndb_exp_interaction_data (type, id_complex_exp) VALUES (%s, %s) RETURNING id', (str(complextype),str(i))) # warning should i check if the interactiondata already exists?
                    complex_interaction_id=cursor.fetchone()[0]


        if complex_interaction_id=='undef':
            print('This complex does not exist yet. Record the complex exp')
            #Create the complex_exp record
            cursor.execute('INSERT INTO dyndb_complex_exp DEFAULT VALUES RETURNING id')
            complex_id=cursor.fetchone()[0] #returns the id of the last insert command
            #Create the complex_exp_interaction_data record
            cursor.execute('INSERT INTO dyndb_exp_interaction_data (type, id_complex_exp) VALUES (%s, %s) RETURNING id', (str(complextype),str(complex_id)))
            complex_interaction_id=cursor.fetchone()[0]

        #Create the references
        doires=DyndbReferences.objects.filter(doi=comple[9]['DOI'])
        if len(doires)>0:
            print('DOI already exists, no need to record')
            reference_id=doires[0].id
        else:
            cursor.execute('INSERT INTO dyndb_references (doi, authors, url) VALUES (%s, %s, %s) RETURNING id', (comple[9]['DOI'],comple[9]['authors'], comple[9]['bindingdblink'] )) #the link is to the BindingDB entry, not the paper, but it is the closest thing the sdf file provides
            reference_id=cursor.fetchone()[0]

        cursor.execute('INSERT INTO dyndb_references_exp_interaction_data (id_exp_interaction_data, id_references) VALUES (%s, %s)', (str(complex_interaction_id),str(reference_id)))

        print('Complex recorded. Now, record the kinetic values')
        if complextype==1: #kd, binding
            cursor.execute('INSERT INTO dyndb_binding (id, rvalue,units,description) VALUES (%s, %s, %s, %s)', (str(complex_interaction_id),str(kd),'nM','some description')) #warning should i check if they already exist?

        if complextype==2: #ec_50, efficacy
            cursor.execute('INSERT INTO dyndb_efficacy (id, rvalue,units,description,reference_id_compound) VALUES (%s, %s, %s, %s, %s)', (str(complex_interaction_id),str(ec_fifty),'nM','some description','2')) 

        print('kinetics recorded. Now, record the protein')


        if exactest!=1: #if the complex has not been found by the NiceSearcher, we may need to create the proteins and the compounds.
            unicount=0
            #Create the protein and the complexprotein, if it does not exist

            while unicount<len(comple[4]): #for uniprot in comple[4]:
                is_mutated_boo=False
                uniprot=comple[4][unicount]
                binsequence=comple[10][unicount]
                prot_seq=DyndbProteinSequence.objects.filter(sequence=binsequence) #check if that sequence already exists
                if len(prot_seq)>0:
                    print('that sequence has already been conected to a proteinID in our DB ',prot_seq[0].protein_id)
                    cursor.execute(
                        'INSERT INTO dyndb_complex_protein (id_complex_exp,id_protein) VALUES (%s, %s)', (complex_id,prot_seq[0].protein_id)
                    )

                #maybe, that uniprot entry exists, but with a different sequence (a mutant with respect to the cannonical new to the DB)
                else:
                    DBproteins=DyndbProtein.objects.filter(uniprotkbac=uniprot)
                    if len(DBproteins)>0:
                        #our current protein is a mutant.
                        seqdata,errdata = retreive_fasta_seq_uniprot(uniprot) #THIS FAILES SOMETIMES! do they block my ip? 
                        namedata,errdata = retreive_protein_names_uniprot(uniprot)
                        seqdata=seqdata['sequence']
                        namedata=namedata['RecName'][0]['Full'][0]
                        cursor.execute(
                            'INSERT INTO dyndb_protein (uniprotkbac,name,is_mutated,isoform,id_uniprot_species) VALUES (%s, %s, %s, %s, %s) RETURNING id', (uniprot,namedata,'True','1',str(id_uniprot_species))
                        )

                        prot_id=cursor.fetchone()[0]
                        cursor.execute(
                            'INSERT INTO dyndb_protein_sequence (id_protein,sequence,length) VALUES (%s, %s, %s)', (str(prot_id),seqdata,str(len(seqdata)))
                        )

                        cursor.execute(
                            'INSERT INTO dyndb_complex_protein (id_complex_exp,id_protein) VALUES (%s, %s)', (str(complex_id),str(prot_id))
                        )

                        alignment=align_wt_mut(seqdata,binsequence)
                        residcounter=0
                        while residcounter<len(alignment[0]):
                            
                            cursor.execute(
                                'INSERT INTO dyndb_protein_mutations (id_protein,resid,resletter_from,resletter_to) VALUES (%s, %s, %s, %s)', (str(prot_id),str(residcounter+1),str(alignment[0][residcounter]),str(alignment[1][residcounter]))
                            )
                            residcounter+=1

                    else:
                        
                        data,errdata = retreive_data_uniprot(uniprot,isoform=None,columns='id,entry name,organism,length,')
                        #data {'Entry': 'Q9UQ88', 'Entry name': 'CD11A_HUMAN', 'Length': '783', 'Organism': 'Homo sapiens (Human)'} 
                        data['speciesid'], data['Organism'] = get_uniprot_species_id_and_screen_name(data['Entry name'].split('_')[1])
                        id_uniprot_species=data['speciesid']
                        namedata,errdata = retreive_protein_names_uniprot(uniprot)
                        namedata=namedata['RecName'][0]['Full'][0]
                        cursor.execute(
                            'INSERT INTO dyndb_protein (uniprotkbac,name,is_mutated,isoform,id_uniprot_species) VALUES (%s, %s, %s, %s, %s) RETURNING id', (uniprot,namedata,'False','1',str(id_uniprot_species))
                        )
                        prot_id=cursor.fetchone()[0]
                        cursor.execute(
                            'INSERT INTO dyndb_protein_sequence (id_protein,sequence,length) VALUES (%s, %s, %s)', (str(prot_id),binsequence,str(len(binsequence)) )
                        )
                        cursor.execute(
                            'INSERT INTO dyndb_complex_protein (id_complex_exp,id_protein) VALUES (%s, %s)', (str(complex_id),str(prot_id))
                        )
                unicount+=1

            #Create the ccompound and complxcompound, if it does not exist
            print('Protein recorded, now the compound')
            DBcompound=DyndbCompound.objects.filter(pubchem_cid=comple[2])
            if len(DBcompound)>0:
                compound_id=DBcompound[0].id
                print('compound already existed, mo need to record it')
            else:
                pubchem_id=comple[2]
                iupac,errdata = retreive_compound_data_pubchem_post_json('cid',pubchem_id,operation='property',outputproperty='IUPACName')
                print(comple,iupac,errdata)
                try:
                    iupac=iupac['PropertyTable']['Properties'][0]['IUPACName']
                except KeyError:
                    iupac='NOT DEFINED, PUBCHEMID:'+pubchem_id
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
                cursor.execute('INSERT INTO dyndb_compound (name, iupac_name,pubchem_cid,sinchi,sinchikey) VALUES (%s, %s, %s, %s, %s) RETURNING id', (names,iupac,pubchem_id,sinchi,sinchikey) )
                compound_id=cursor.fetchone()[0]

            cursor.execute(
                'INSERT INTO dyndb_complex_compound (id_compound,id_complex_exp,type) VALUES (%s, %s, %s)', (compound_id,complex_id,'0')
            )
        print('\n\nComplex data recorded without errors.\n\n',complexcounter)
        complexcounter+=1

##############################################################################################################################################
##############################################################################################################################################
