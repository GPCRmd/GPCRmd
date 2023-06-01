############################################### IUPHAR and BindingDB parsing#######################################################################################################################

#run with /env/bin/python fillDB.py
#if you have any doubts, contact: alejandrovarelarial@gmail.com
import os, sys
from django.conf import settings
proj_path = settings.MODULES_ROOT

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.append(proj_path)
os.chdir(proj_path)

from django.core.wsgi import get_wsgi_application
from django.utils import timezone
application = get_wsgi_application()

import pickle
import requests
import time
from modules.dynadb.customized_errors import StreamSizeLimitError, StreamTimeoutError, ParsingError
from django.db.models import F
from modules.protein.models import Protein
from uniprotkb_utils_fillDB import retreive_data_uniprot,retreive_protein_names_uniprot,valid_uniprotkbac, retreive_data_uniprot, retreive_protein_names_uniprot, get_other_names, retreive_fasta_seq_uniprot, retreive_isoform_data_uniprot
from contextlib import closing
from django.db import connection
from django.utils import timezone
from rdkit.Chem import MolFromInchi,MolFromSmiles
from molecule_download_fillDB import retreive_compound_data_pubchem_post_json, retreive_compound_sdf_pubchem, retreive_compound_png_pubchem, CIDS_TYPES, pubchem_errdata_2_response, retreive_molecule_chembl_similarity_json, chembl_get_compound_id_query_result_url,get_chembl_molecule_ids, get_chembl_prefname_synonyms, retreive_molecule_chembl_id_json, retreive_compound_png_chembl, chembl_get_molregno_from_html, retreive_compound_sdf_chembl, chembl_errdata_2_response
from UniprotCodes import gpcr_uniprot_codes
from django.db.models import Q
from modules.dynadb.models import DyndbBinding,DyndbEfficacy,DyndbReferencesExpInteractionData,DyndbExpInteractionData,DyndbReferences, DyndbProteinCannonicalProtein, DyndbProtein, DyndbProteinSequence, DyndbUniprotSpecies, DyndbUniprotSpeciesAliases, DyndbOtherProteinNames, DyndbProteinActivity, DyndbFileTypes, DyndbCompound, DyndbMolecule, DyndbFilesMolecule,DyndbFiles,DyndbOtherCompoundNames, DyndbCannonicalProteins,DyndbComplexProtein,DyndbReferencesProtein,DyndbComplexMoleculeMolecule,DyndbComplexMolecule,DyndbComplexCompound,DyndbReferencesMolecule,DyndbReferencesCompound,DyndbComplexExp
from modules.dynadb.models import DyndbProteinMutations,DyndbProteinCannonicalProtein, DyndbProtein, DyndbProteinSequence, DyndbUniprotSpecies, DyndbUniprotSpeciesAliases, DyndbOtherProteinNames, DyndbFileTypes, DyndbCompound, DyndbMolecule, DyndbFilesMolecule,DyndbFiles,DyndbOtherCompoundNames,DyndbInhibition
from modules.dynadb.pipe4_6_0 import *
from Bio import Entrez
from Bio.Entrez import efetch
from modules.dynadb.views import dealwithquery,do_boolean,prepare_to_boolean,get_uniprot_species_id_and_screen_name, get_file_name,get_file_paths, generate_molecule_properties_BindingDB
Entrez.email = 'alejandrovarelarial@yahoo.es'

def complexmatch_complex_exp(result_id,querylist):
    ''' Extracts every element from each complex in result_id and checks if there are elements in the complex which are not in the querylist '''
    moltypetrans={0:'orto',1:'alo'}

    for cprotein in DyndbComplexProtein.objects.select_related('id_protein__receptor_id_protein').filter(id_complex_exp=result_id):

        is_receptor=cprotein.id_protein.receptor_id_protein!=None
        if is_receptor is True:
            is_receptor='true'
        else:
            is_receptor=False
        cprotstr=str(cprotein.id_protein.id)
        #print(['protein',cprotstr,is_receptor], 'this protein is in this cmol')
        if ['protein',cprotstr,is_receptor] not in querylist:
            print('missing protein:',['protein',str(cprotein.id_protein.id),is_receptor])
            return 'fail'

    for ccompound in DyndbComplexCompound.objects.select_related('id_compound').filter(id_complex_exp=result_id):
        comstr=str(ccompound.id_compound.id)
        #print('this compound is in this cmol',['compound',comstr,moltypetrans[ccompound.type]])
        if (['compound',comstr,moltypetrans[ccompound.type]] not in querylist) and (['compound',comstr,'all'] not in querylist):
            print('mising compound:',['compound',str(ccompound.id_compound.id),moltypetrans[ccompound.type]])
            return 'fail' 

    return 'pass'

def do_query_complex_exp(table_row,return_type): #table row will be a list as [id,type]
    '''Returns a list of id's of the selected type (complex, model or dynamics) where the element in table_row appears. If the elemnt in table_row is a compound the ids brom both the compound and all the correspondent molecules are retrieved'''
    rowlist=[]
    print('\n\nSearching...',table_row)
    if return_type=='complex':
        if table_row[0]=='protein':
            is_receptor=DyndbProtein.objects.get(pk=table_row[1]).receptor_id_protein
            if (table_row[2]=='true' and is_receptor!=None) or (table_row[2]==False and is_receptor==None):
                q=DyndbProtein.objects.filter(pk=table_row[1])
                q=q.annotate(cmol_id=F('dyndbcomplexprotein__id_complex_exp'))
                q=q.values('cmol_id')
                for row in q:
                    rowlist.append(row['cmol_id'])

        elif table_row[0]=='molecule':
            user_molecule = table_row[1]
            if table_row[2]=='orto' or table_row[2]=='all': #orthosteric ligand
                for comp in DyndbComplexMoleculeMolecule.objects.select_related('id_complex_molecule').filter(id_molecule=user_molecule).filter(type=0): 
                    rowlist.append(comp.id_complex_molecule.id)

            elif table_row[2]=='alo' or table_row[2]=='all': #alosteric ligand
                for comp in DyndbComplexMoleculeMolecule.objects.select_related('id_complex_molecule').filter(id_molecule=user_molecule).filter(type=1): 
                    rowlist.append(comp.id_complex_molecule.id)

        else:
            user_compound = table_row[1]
            q = DyndbComplexCompound.objects.filter(id_compound=user_compound)
            q = q.annotate(cmol_id=F('id_complex_exp')) 
            q = q.values('type','cmol_id')
            for row in q:
                if (table_row[2]=='orto' or table_row[2]=='all') and row['type']==0: #ortoligand
                    rowlist.append(row['cmol_id'])
                if (table_row[2]=='alo' or table_row[2]=='all') and row['type']==1: #alosteric ligand
                    rowlist.append(row['cmol_id'])

    rowlist=[res_id for res_id in rowlist if res_id!=None]
    return rowlist

def main_complex_exp(arrays,return_type):
    rowdict=dealwithquery(arrays)
    results=dict()
    for keys,values in rowdict.items():
        #we need to differentiate between list of lists, and simples lists
        #parenthesis lines are like: dict[key]=[ [ID, TYPE]  [AND, ID, TYPE], [OR, ID, TYPE], [AND, ID, TYPE]  ]
        #other lines are like: dickt[key]=[AND, ID, TYPE]
        inner_results=list()
        if type(values[0])==list: #inside of parenthesis
            for item in values: #values is a list, so it keeps the order of the rows, so does inner_results.
                if item[0]=='AND' or item[0]=='OR' or item[0]=='NOT':
                    inner_results.append([ item[0] , do_query_complex_exp(item[1:4],return_type) ]) #inner_results=[ ['AND', [1,2,3] ]  ],  ['OR', [2,3,5] ]  ]

                else: #first line inside parenthesis, the boolean of this row aplies to the whole parenthesis and it is stored in the rowdict.                
                    inner_results.append([ 'NONE' , do_query_complex_exp(item[0:3], return_type)])
            results[keys]=list(do_boolean(inner_results)) #results[counter,boolean]=[1,2,3,4] #counter is the row number where the '(' appears


        else: #simple row
            results[keys]=do_query_complex_exp(values,return_type) #do query for each value, save it under same key
    aaa=do_boolean( prepare_to_boolean(results) )
    return aaa



def exactmatchtest_complex_exp(arrays,return_type,result_id):
    ''' Extracts every element from each complex, model or dynamic in result_id and checks if there are elements in it which are not in the querylist '''
    rowdict=dealwithquery(arrays)
    querylist=list()
    for keys,values in rowdict.items():
        if keys[1]!='NOT':
            if type(values[1])==list:
                for item in values:
                    if len(item)==3:
                        querylist.append(item)
                    elif len(item)>3 and item[0]!='NOT':
                        querylist.append(item[1:])
            else:
                querylist.append(values)
    #hack the list to add the corresponding molecules and compounds to the ones the user has queried.
    tmpquerylist=[]
    for item in querylist:
        if item[0]=='compound':
            for molid in DyndbMolecule.objects.filter(id_compound=item[1]):
                tmpquerylist.append(['molecule',str(molid.id),item[2]])
        elif item[0]=='molecule':
            tmpquerylist.append(['compound',str(DyndbMolecule.objects.get(pk=item[1]).id_compound.id),item[2]])

    querylist+=tmpquerylist
    if return_type=='complex':
        return complexmatch_complex_exp(result_id,querylist)

    return 'pass'
##########################################################################################################################################


def scorenames(names_list):
    '''Given a list of synomins, returns the most human friendly'''
    maxscore=-99999
    bestname=names_list[0]
    counter=0
    for name in names_list:
        oriname=name
        score=0
        name=name.lower()
        score=len(name)*-0.4 #the longer the name, the worse the score
        score=score+ 3*((name.count('a')+name.count('e')+name.count('i')+name.count('o')+name.count('u'))*100/len(name))
        score=score-len(re.findall("\d", name))
        score=score-counter #ponderate the order
        if score>maxscore and len(name)<60:
            maxscore=score
            bestname=oriname
        counter=+1
    return bestname
    
    

def newrecord(tablename,fields_values,insert_id=False):
    '''Takes a dictionary with information and saves it into the database '''
    postgresql_name=tablename[0]
    django_name=tablename[1]
    username='gpcrmd_admin'
    try:
        nextid=django_name.objects.latest('id').id+1
    except:
        nextid=1 #warning, some tables do NOT have an id column! they will keep nextid as 1 despite they lack that column!
    
    if tablename[0] in ['dyndb_exp_interaction_data','dyndb_complex_molecule','dyndb_references','dyndb_protein','dyndb_files','dyndb_compound','dyndb_molecule']:
        fields_values.update({'creation_timestamp':timezone.now(),'created_by_dbengine':username, 'last_update_by_dbengine':username})

    fields=','.join(list(fields_values.keys()))
    values=list(fields_values.values())
    tmpvalues=[]
    for i in values:
        if i!=None:
            tmpvalues.append(str(i))
        else:
            tmpvalues.append(i)
    values=tmpvalues
    if insert_id:
        values=values+[str(nextid)]
        values=tuple(values)
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                'INSERT INTO '+postgresql_name+' ('+fields+', id) VALUES ('+'%s,'*(len(values)-1)+'%s)', values
            )

    else:
        values=tuple(values)
        with closing(connection.cursor()) as cursor:
            try:
                cursor.execute(
                    'INSERT INTO '+postgresql_name+' ('+fields+') VALUES ('+'%s,'*(len(values)-1)+'%s) RETURNING id', values
                )
                nextid=cursor.fetchone()[0]
            except:
                cursor.execute(
                    'INSERT INTO '+postgresql_name+' ('+fields+') VALUES ('+'%s,'*(len(values)-1)+'%s)', values
                )

    return nextid

def fetch_abstract(pmid):
    '''Given a Pubmed identifier, returns bibliographic info about it.'''
    try:
        handle = efetch(db='pubmed', id=pmid, retmode='xml')
    except:
        time.sleep(5)
        handle = efetch(db='pubmed', id=pmid, retmode='xml')
    xml_data = handle.read()
    #print (xml_data)
    linelist=[]
    for line in xml_data.split('\n'):
        linelist.append(line)

    i=0
    title=''
    journal=''
    issn=''
    volume=''
    issue=''
    authors=''
    doi=None
    year=None
    while i<len(linelist):
        line=linelist[i]
        if re.search('<ArticleTitle>(.*)</ArticleTitle>', line, re.IGNORECASE):
            title_search = re.search('<ArticleTitle>(.*)</ArticleTitle>', line, re.IGNORECASE)
            if title_search:
                title = title_search.group(1)

        elif re.search('<Title>(.*)</Title>', line, re.IGNORECASE):
            title_search=re.search('<Title>(.*)</Title>', line, re.IGNORECASE)
            journal= title_search.group(1)    
       
        elif re.search('>(.*)</ISSN>', line, re.IGNORECASE):
            title_search=re.search('>(.*)</ISSN>', line, re.IGNORECASE)
            issn = title_search.group(1)

        elif re.search('<Volume>(.*)</Volume>', line, re.IGNORECASE):
            title_search=re.search('<Volume>(.*)</Volume>', line, re.IGNORECASE)
            volume = title_search.group(1)

        elif re.search('<Issue>(.*)</Issue>', line, re.IGNORECASE):
            title_search=re.search('<Issue>(.*)</Issue>', line, re.IGNORECASE)
            issue = title_search.group(1)
            
        elif re.search('<AuthorList', line, re.IGNORECASE):
            j=i+1
            while not re.search('</AuthorList>', linelist[j], re.IGNORECASE):
                if '<Author' in linelist[j]:
                    lastname=''
                    initials=''
                    if re.search('<LastName>(.*)</LastName>', linelist[j+1], re.IGNORECASE):
                        lastname=re.search('<LastName>(.*)</LastName>', linelist[j+1], re.IGNORECASE).group(1)

                    if re.search('<Initials>(.*)</Initials>', linelist[j+3], re.IGNORECASE):
                        initials=re.search('<Initials>(.*)</Initials>', linelist[j+3], re.IGNORECASE).group(1)
                    author=lastname+', '+initials+'; '
                    authors+=author
                j+=1
        elif re.search('<ELocationID',line,re.IGNORECASE) and re.search('EIdType="doi"',line,re.IGNORECASE):
            title_search = re.search('<ELocationID.*>(.*)</ELocationID>', line, re.IGNORECASE)
            if title_search:
                doi = title_search.group(1)

            if len(doi)==0:
                doi=None

        elif re.search('<pubdate>',line,re.IGNORECASE):
            j=i+1
            while not re.search('</PubDate>',linelist[j],re.IGNORECASE):
                line=linelist[j]
                year_search = re.search('<Year>(.*)</Year>', line, re.IGNORECASE)
                if year_search:
                    year = year_search.group(1)
     
                j+=1

        i+=1
    refdic={'title':title, 'volume':volume, 'issue':issue, 'authors':authors,'pubyear':year, 'issn':issn, 'journal':journal,'doi':doi}

    return refdic



def iuphar_parser(file_name):
    '''Gets some columns from interactions.csv file from iuphar'''
    with open(file_name,'r') as fh: #warning: delete first line!
        records=[]
        linecount=0
        for line in fh:
            if linecount!=0: #jump first line of the csv->headers
                line=line.strip()
                linelist=list(line)
                counterchar=0
                cleanline=''
                state='off'
                for char in linelist:
                    if char=='"':
                        counterchar+=1
                        if counterchar%2==0:
                            state='off'
                        else:
                            state='on'
                    if char==',' and state=='on':
                        char=';'
                    cleanline+=str(char)
                line=cleanline
                fields=line.split(',')
                if len(fields)==34:
                    interaction=dict()
                    interaction['uniprot']=fields[3]
                    if '|' in interaction['uniprot']:
                        interaction['uniprot']=interaction['uniprot'].split('|')
                    else:
                        interaction['uniprot']=[interaction['uniprot']]
                    interaction['uniprot2']=fields[7]
                    if '|' in interaction['uniprot2']:
                        interaction['uniprot2']=interaction['uniprot2'].split('|')     
                    else:
                        interaction['uniprot2']=[interaction['uniprot2']]
                    interaction['pubchem_sid']=fields[14] #https://pubchem.ncbi.nlm.nih.gov/rest/pug/substance/sid/252827410/cids/XML?cids_type=all to convert to compound id
                    interaction['experiment_type']=fields[25]
                    interaction['median_value']=fields[27]
                    interaction['pmid']=fields[-1]
                    interaction['pmid']=interaction['pmid'].split('|') #if there is no |, the result is a list with only one element
                    emptyflag=0
                    
                    interaction['uniprot']=interaction['uniprot']+interaction['uniprot2']
                    interaction['uniprot']=list(filter(lambda x: len(x)!=0, interaction['uniprot']))
                    
                    interaction['pmid']=list(filter(lambda x: len(x)!=0, interaction['pmid']))
                    interaction['target_id']=fields[1]
                    if len(interaction['uniprot'])!=0 and len(interaction['pubchem_sid'])!=0 and len(interaction['experiment_type'])!=0 and len(interaction['median_value'])!=0 and len(interaction['pmid'])!=0:
                        records.append(interaction)
           
            linecount+=1
                    
    return records

def to_bindingdb_format(records):
    '''Transforms data from iuphar format into the one we use to fill the database'''
    complexes=[]
    for record in records:
        print('\n\n\n\nPROCCESSING RECORD:',record)
        kd=''
        ec50=''
        ic50=''
        ki=''
        #complex=[ligkey,liginchi, pubchem_id, chembl_id,protlist,kd,ec50,ki,ic50,reference,seqlist,SDF,binding_id]
        protlist=record['uniprot']
        if record['experiment_type']=='Kd':
            kd=record['median_value']
        elif record['experiment_type']=='EC50':
            ec50=record['median_value']
        elif record['experiment_type']=='IC50':
            ic50=record['median_value']
        elif record['experiment_type']=='Ki':
            ki=record['median_value']
        else:
            continue 
        target_id=str(record['target_id'])
        seqlist=[]
        gpcr_flag=0
        for protein in protlist:
            if protein in gpcr_uniprot_codes:
                gpcr_flag=1
                
            response = requests.get("http://www.uniprot.org/uniprot/"+protein+".fasta") #seq of cannonicalid
            sequenceraw=response.text.split('\n')[1:] #skip header
            seq=''.join(sequenceraw)
            seqlist.append(seq)
        
        if gpcr_flag==0 or len(seq)==0 or len(target_id)==0:
            continue #no interest in non gpcr coomplexes nor empty sequences
        pubchemid=requests.get('https://pubchem.ncbi.nlm.nih.gov/rest/pug/substance/sid/'+str(record['pubchem_sid'])+'/cids/json?cids_type=all')
        pubchemid=pubchemid.json()
        try:
            pubchemid=pubchemid['InformationList']['Information'][0]['CID'][0]
        except KeyError:
            print('no way to found the cid')
            continue #no compound found to that substance.
        try:
            datasdfpubchem,errdata = retreive_compound_sdf_pubchem('cid',pubchemid,outputfile='/tmp/trysdf_removewheneveryouwant.sdf',in3D=True)
            if len(errdata)>0:
                print('no sdf for this pubchem',pubchemid,errdata)
                continue
            sinchi,errdata=retreive_compound_data_pubchem_post_json('cid',pubchemid,operation='property',outputproperty='InChI')
            sinchi=sinchi['PropertyTable']['Properties'][0]['InChI'][6:]
            sinchikey,errdata=retreive_compound_data_pubchem_post_json('cid',pubchemid,operation='property',outputproperty='InChIKey')
            sinchikey=sinchikey['PropertyTable']['Properties'][0]['InChIKey']
        except:
            print('ERROR WHEN SEARCHING SINCHI AND SINCHIKEY')
            continue
        complexes.append([sinchikey,sinchi,pubchemid,'',protlist,kd,ec50,ki,ic50,{'pmid':record['pmid'],'DOI':'','bindingdblink':'','authors':''},seqlist,'iuphar','iuphar_'+target_id])

        print('\n\n\nONE RECORD READY',record)

    with open('iuphar_useful_complexes_pickle', 'wb') as fp:
        pickle.dump(complexes, fp)
        
    return (complexes)



def get_complexes(chunk):
    '''Fills the GPCRmd database with data from the BindingDB.'''
    fh=open(chunk,'r')
    complexes=[] #each complex has: the ligand InchiKey, the list of uniprot codes which form the PROTEIN part of the complex, Ki, IC50, Kd, EC50
    uniflag=0 
    ligflag=0
    errflag=0
    lines_list=[]
    i=0
    reference={}
    for line in fh:
        lines_list.append(line)

    protlist=[]
    seqlist=[]
    emptyprot=False
    print('lines in memory')
    while i<len(lines_list):#make sure the last line is parsed.

        if '$$$$' in lines_list[i]:
            if ( len( kd.replace('0','').replace('.','') )>0 or len( ec50.replace('0','').replace('.','') )>0  or len( ic50.replace('0','').replace('.','') )>0  or len(ki.replace('0','').replace('.','') )>0 ) and emptyprot==False and errflag==0 and len(set(protlist).intersection(set(gpcr_uniprot_codes)))>0 and pubchem_id!='':
                complexes.append([ligkey,liginchi, pubchem_id, chembl_id,protlist,kd,ec50,ki,ic50,reference,seqlist,SDF,binding_id]) 
            protlist=[]
            reference={} 
            seqlist=[]
            emptyprot=False
            errflag=0

        if '<Ligand InChI Key>' in lines_list[i]:
            ligkey=''
            j=i+1
            while '> <' not in lines_list[j]:
                ligkey+=lines_list[j].strip()
                j+=1

        elif '> <BindingDB Reactant_set_id>' in lines_list[i]:
            binding_id=lines_list[i+1].strip()


        elif '<Ligand InChI>' in lines_list[i]:
            liginchi=''
            j=i+1
            while '> <' not in lines_list[j]:
                liginchi+=lines_list[j].strip()
                j+=1

        elif lines_list[i].startswith('Vconf') or 'Mrv' in lines_list[i] or 'SciTegic' in lines_list[i]: #old:   elif lines_list[i].startswith('Vconf'):
            SDF='\n\n\n'
            j=i+1
            while 'M  END' not in lines_list[j]:
                if lines_list[j]!='\n': #skip empty lines
                    SDF+=lines_list[j] #no strip! we need the file as it is!
                j+=1
            if 'M  END' in lines_list[j]:
                SDF+=lines_list[j]
            SDF+='$$$$\n'

        elif '<UniProt (SwissProt) Primary ID of Target Chain>' in lines_list[i]: #we are only using SwissProt, because trEMBLE is predicted.
            if len(lines_list[i+1].strip())>0:
                protlist.append(lines_list[i+1].strip())
            else:
                emptyprot=True

        elif '<PubChem CID>' in lines_list[i]: 
            pubchem_id=lines_list[i+1].strip()

        elif '<ChEMBL ID of Ligand>' in lines_list[i]:
            chembl_id=lines_list[i+1].strip()[6:]

        elif '<PMID>' in lines_list[i]:
            reference['pmid']=''
            reference['pmid']=lines_list[i+1].strip() 
            if reference['pmid']=='':
                reference['pmid']=None

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
            if reference['DOI']=='':
                reference['DOI']=None

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
                sequence+=lines_list[j].strip().replace(' ','').upper()
                j+=1
            seqlist.append(sequence)

        i+=1

    fh.close()
    
    return complexes
    
def record_complex_in_DB(comple,fromiuphar=False,ec50_id=None):
    ''' It uses a variation of the NiceSearcher to check if a new entry in the Binding DB sdf already exists as a complex, if it is not, a new comoplex is created. '''
    #all records in memory, now record them in the DB.
    try:
        isoformid=1
        recorded_ids=dict() #save here the inserted ids so we can return it when failing and delete those ids
        recorded_ids['intdata']=[]
        recorded_ids['intdataref']=[]
        recorded_ids['bind']=[]
        recorded_ids['ec50']=[]
        recorded_ids['ic50']=[]
        recorded_ids['ki']=[]
        print(comple[:-2])

        kd=comple[5]
        ec_fifty=comple[6]
        ki=comple[7]
        ic_fifty=comple[8]

        if sum([len(kd)>0,len(ec_fifty)>0,len(ic_fifty)>0,len(ki)>0])>1:
            complextype=5

        elif len(kd)>0:
            complextype=1

        elif len(ec_fifty)>0:
            complextype=2

        elif len(ic_fifty)>0:
            complextype=4 #3

        elif len(ki)>0:
            complextype=3  #4  

        else:
            complextype=0 #functional
            return 'this type is not useful'

        #Check if the combination of ligand and target exists. Transform it into tablesearch and use NiceSearcher to retrieve the complex
        # [[' ', ' ', 'protein', '1', 'true', '', '5-receptor', '  '], ['AND', ' ', 'compound', '1', 'orto', '', 'Clozapine', '  ']]

        query_array=[]
        flag=0 #check if either the protein or the compound is new to the database, if it is, do not perform NiceSearch as it is useless.
        unicount=0 
        while unicount<len(comple[4]) and flag==0: #build the query for the proteins
            uniprot=comple[4][unicount]
            isGPCR=uniprot in gpcr_uniprot_codes
            if isGPCR is True:
                isGPCR='true'
            binsequence=comple[10][unicount]
            proteindb=DyndbProteinSequence.objects.filter(sequence=binsequence)
            if len(proteindb)>0:
                pkprot=proteindb[0].id_protein.id
                query_array.append(['AND', ' ', 'protein', str(pkprot), isGPCR, '', '5-hydroxytryptamine-receptor', '  ']) #the name doesnt matter
            else:
                flag=1

            unicount+=1

        pubchem_id=comple[2]
        compdb=DyndbCompound.objects.filter(pubchem_cid=pubchem_id)
        compdbsinchi=DyndbCompound.objects.filter(sinchi=comple[1],sinchikey=comple[0])
        #join the ligand to the query
        if len(compdb)>0:
            compound_id=compdb[0].id
            query_array.append(['AND', ' ', 'compound', str(compound_id), 'orto', '', 'Clozapine', '  ']) #'Clozapine' is not really used, so we leave it
        elif len(compdbsinchi)>0: #double-check if that comp exists with inchi and inchikey
            compound_id=compdbsinchi[0].id
            query_array.append(['AND', ' ', 'compound', str(compound_id), 'orto', '', 'Clozapine', '  ']) #'Clozapine' is not really used, so we leave it   

        else:
            flag=1

        complex_interaction_id='undef'
        exactest=0

        if flag==0: #if either the protein or the compound is not present, then, we are sure that a complex containing them does not exist.
            query_array[0][0]=' ' #first element has no boolean!
            resultlist=main_complex_exp(query_array,'complex')
            for i in resultlist:
                if exactmatchtest_complex_exp(query_array,'complex',i)=='pass':
                    exactest=1 #this complex already exists
                    complex_id=i
                    print('This is the complex id found',i)
                    if complextype==5: #Call again this function, this time with only one rvalue at a time. WARNING, THIS HAS CAUSED ERRORS IN CHUNK: BindingDB_All_3D_from_complex_540002_to_complex_560001sdf
                        print('\n\n\n\n\nMore than one data affinity in one record!\n\n\n\n\n')
                        if kd:
                            completmp=comple.copy()
                            completmp[6]=''
                            completmp[7]=''
                            completmp[8]=''
                            try:
                                result=record_complex_in_DB(completmp,fromiuphar)   
                            except:
                                if type(result)==dict:
                                    return result

                        if ec_fifty:
                            completmp=comple.copy()
                            completmp[5]=''
                            completmp[7]=''
                            completmp[8]=''
                            try:
                                result=record_complex_in_DB(completmp,fromiuphar)  
                            except:
                                if type(result)==dict:
                                    return result

                        if ki:
                            completmp=comple.copy()
                            completmp[6]=''
                            completmp[5]=''
                            completmp[8]=''
                            try:
                                result=record_complex_in_DB(completmp,fromiuphar)  
                            except:
                                if type(result)==dict:
                                    return result

                        if ic_fifty: 
                            completmp=comple.copy()
                            completmp[6]=''
                            completmp[7]=''
                            completmp[5]=''
                            try:
                                if ec_fifty: #two values of efficacy togheter. Save the ec50 of this experiment as the reference for the ic_fifty
                                    intdata=DyndbExpInteractionData.objects.filter(id_complex_exp=i).filter(type=2) #ecfifty type with that complex exp
                                    for intd in intdata:
                                        effrec=DyndbEfficacy.objects.filter(description=comple[12]).filter(id=intd.id)
                                        if len(effrec)>0:
                                            ec_fifty_id=intd.id

                                    result=record_complex_in_DB(completmp,fromiuphar,ec50_id=ec_fifty_id)
                                else:
                                    result=record_complex_in_DB(completmp,fromiuphar)
                            except:
                                if type(result)==dict:
                                    return result

                    else:
                        if complextype==4:
                            complextype_mod=2 #icfifty is type number 2 for the DB
                        else:
                            complextype_mod=complextype
                        intdata=DyndbExpInteractionData.objects.filter(id_complex_exp=i).filter(type=complextype_mod) #one cexp can have data for kd from iuphar and bindingDB
                        if len(intdata)>0:
                            print('we have a record for that cexp already',str(intdata))
                            for expintdata in intdata:		
                                if complextype==1: #kd
                                    if len(DyndbBinding.objects.filter(id=expintdata.id).filter(description=comple[12]))>0: 
                                        #this experiment data is already recorded, do not record it again
                                        print('\n\n\nThis complex was already recorded\n\n\n')
                                        return 'This complex was already recorded'
                            
                                elif complextype==2: #ec50
                                    if len(DyndbEfficacy.objects.filter(id=expintdata.id).filter(description=comple[12]))>0: 
                                        #this experiment data is already recorded, do not record it again
                                        print('\n\n\nThis complex was already recorded')
                                        return 'This complex was already recorded'

                                elif complextype==3: #ki
                                    if len(DyndbInhibition.objects.filter(id=expintdata.id).filter(description=comple[12]))>0: 
                                        #this experiment data is already recorded, do not record it again
                                        print('\n\n\nThis complex was already recorded')
                                        return 'This complex was already recorded'

                                elif complextype==4: #ic50
                                    if len(DyndbEfficacy.objects.filter(id=expintdata.id).filter(description=comple[12]).filter(type=3))>0: 
                                        #this experiment data is already recorded, do not record it again
                                        print('\n\n\nThis complex was already recorded')
                                        return 'This complex was already recorded'



                            #if python gets to this line is because it has not returned anything-> it has not found any intdata matching the one we want to insert now                 
                            complex_interaction_id=newrecord(['dyndb_exp_interaction_data',DyndbExpInteractionData],{'type':complextype,'id_complex_exp':i},True)
                            recorded_ids['intdata'].append(complex_interaction_id)
                            
                        else: #no intdata for that cexp, record it
                            complex_interaction_id=newrecord(['dyndb_exp_interaction_data',DyndbExpInteractionData],{'type':complextype,'id_complex_exp':i},True)
                            recorded_ids['intdata'].append(complex_interaction_id)
                            
                            
        if complex_interaction_id=='undef':
            #This complex does not exist yet. Record the complex exp and the intdata
            with closing(connection.cursor()) as cursor:
                try:		
                    lastid=str(DyndbComplexExp.objects.latest('id').id + 1)
                except:
                    lastid=1
                cursor.execute('INSERT INTO dyndb_complex_exp (id,is_published,creation_timestamp,created_by_dbengine,last_update_by_dbengine) VALUES (%s,%s,%s,%s,%s) RETURNING id', (lastid,True, timezone.now(),'gpcrmd','gpcrmd'))
                complex_id=cursor.fetchone()[0]
                recorded_ids['complexid']=complex_id   
            cmol_id=newrecord(['dyndb_complex_molecule',DyndbComplexMolecule],{'id_complex_exp':complex_id, 'is_published':True},True) 
            recorded_ids['complexmol']=cmol_id
            if complextype==4:
                complextype_mod=2 #icfifty is type number 2 for the DB
            else:
                complextype_mod=complextype
            #Create the complex_exp_interaction_data record
            complex_interaction_id=newrecord(['dyndb_exp_interaction_data',DyndbExpInteractionData],{'type':complextype_mod,'id_complex_exp':complex_id},True)
            recorded_ids['intdata'].append(complex_interaction_id)
                
        #Create the references
        if fromiuphar:
            for reference in comple[9]['pmid']:
                doirespmid=DyndbReferences.objects.filter(pmid=str(reference) )
                #complexes.append([sinchikey,sinchi,pubchemid,'',protlist,kd,ec50,'','',{'pmid':record['pmid'],'DOI':'','bindingdblink':'','authors':''},seqlist,'iuphar',''])
                if len(doirespmid)>0 and reference!=None:
                    reference_id=doirespmid[0].id
                else:
                    fullref=fetch_abstract(reference)
                    try:
                        doi=fullref['doi']
                    except KeyError:
                        doi=None

                    reference_id=newrecord(['dyndb_references',DyndbReferences],{'doi':doi, 'authors':fullref['authors'], 'url':'http://www.guidetopharmacology.org/','dbname':'IUPHAR','pmid':str(reference),'title':fullref['title'],'issue':fullref['issue'],'volume':fullref['volume'],'pub_year':fullref['pubyear'],'journal_press':fullref['journal']},True)
                
                intref=DyndbReferencesExpInteractionData.objects.filter(id_exp_interaction_data=complex_interaction_id).filter(id_references=reference_id)
                if len(intref)==0:
                    refexpintdata=newrecord(['dyndb_references_exp_interaction_data',DyndbReferencesExpInteractionData],{'id_exp_interaction_data':complex_interaction_id, 'id_references':reference_id},True)
                    recorded_ids['intdataref'].append(refexpintdata)
                    
        else:
            doiresdoi=DyndbReferences.objects.filter(doi=comple[9]['DOI'])
            doiresurl=DyndbReferences.objects.filter(url=str(comple[9]['bindingdblink']))
            doirespmid=DyndbReferences.objects.filter(pmid=comple[9]['pmid'])

            #does this reference already exist?
            if (len(doiresdoi)>0 and comple[9]['DOI']!=None) or (len(doiresurl)>0 and str(comple[9]['bindingdblink'])!='') or (len(doirespmid)>0 and comple[9]['pmid']!=None):
                if len(doiresdoi)>0:
                    reference_id=doiresdoi[0].id
                elif len(doiresurl)>0:
                    reference_id=doiresurl[0].id
                else:
                    reference_id=doirespmid[0].id

            else: #reference does not exist yet
                if comple[9]['pmid'] is not None:
                    fullref=fetch_abstract(comple[9]['pmid'])
                    if comple[9]['DOI'] is None:
                        doi=fullref['doi']
                    else:
                        doi=comple[9]['DOI']

                    reference_id=newrecord(['dyndb_references',DyndbReferences],{'doi':doi, 'authors':comple[9]['authors'], 'url':comple[9]['bindingdblink'],'dbname':'BindingDB','pmid':comple[9]['pmid'],'title':fullref['title'],'issue':fullref['issue'],'volume':fullref['volume'],'pub_year':fullref['pubyear'],'journal_press':fullref['journal']},True)

                    #the link is to the BindingDB entry, not the paper, but it is the closest thing the sdf file provides

                else:
                    reference_id=newrecord(['dyndb_references',DyndbReferences],{'doi':comple[9]['DOI'], 'authors':comple[9]['authors'], 'url':comple[9]['bindingdblink'],'dbname':'BindingDB','pmid':comple[9]['pmid']},True)


            #now that reference exists, create the referenceexpintdata, if it does not exist already
            intref=DyndbReferencesExpInteractionData.objects.filter(id_exp_interaction_data=complex_interaction_id).filter(id_references=reference_id)

            if len(intref)==0:
                refexpintdata=newrecord(['dyndb_references_exp_interaction_data',DyndbReferencesExpInteractionData],{'id_exp_interaction_data':complex_interaction_id, 'id_references':reference_id},True)
                recorded_ids['intdataref'].append(refexpintdata)
                    
                    
        #Complex recorded. Now, record the kinetic values
        
        if complextype==1: #kd, binding
            if len(DyndbBinding.objects.filter(id=complex_interaction_id).filter(description=comple[12]))==0:
                print('new kd, recording it...')
                newrecord(['dyndb_binding',DyndbBinding],{'id':complex_interaction_id,'rvalue':kd,'units':'nM','description':comple[12]})
                recorded_ids['bind'].append(complex_interaction_id)

        if complextype==2: #ec_50, efficacy
            if len(DyndbEfficacy.objects.filter(id=complex_interaction_id).filter(description=comple[12]))==0:
                print('new ec50, recording it...')
                newrecord(['dyndb_efficacy',DyndbEfficacy],{'id':complex_interaction_id,'type':0,'rvalue':ec_fifty,'units':'nM','description':comple[12]})
                recorded_ids['ec50'].append(complex_interaction_id)

        if complextype==4: #ic_50, inhibition efficacy
            if len(DyndbEfficacy.objects.filter(id=complex_interaction_id).filter(description=comple[12]).filter(type=3))==0:
                print('new ic50, recording it...')
                if ec50_id is not None:
                    newrecord(['dyndb_efficacy',DyndbEfficacy],{'id':complex_interaction_id,'rvalue':ic_fifty,'units':'nM','description':comple[12],'type':3, 'reference_id_efficacy':ec50_id})
                else:
                    newrecord(['dyndb_efficacy',DyndbEfficacy],{'id':complex_interaction_id,'rvalue':ic_fifty,'units':'nM','description':comple[12],'type':3})

                recorded_ids['ic50'].append(complex_interaction_id)

        if complextype==3: #ki, inhibition
            if len(DyndbInhibition.objects.filter(id=complex_interaction_id).filter(description=comple[12]))==0:
                print('new ki, recording it...')
                newrecord(['dyndb_inhibition',DyndbInhibition],{'id':complex_interaction_id,'rvalue':ki,'units':'nM','description':comple[12]})
                recorded_ids['ki'].append(complex_interaction_id)

        #kinetics recorded

        if exactest!=1: #if the complex has not been found by the NiceSearcher, we may need to create the proteins and the compounds.
            unicount=0
            #Create the protein and the complexprotein, if it does not exist

            while unicount<len(comple[4]): #for uniprot in comple[4]:
                isoformid=1
                is_mutated_boo=False
                uniprot=comple[4][unicount]
                binsequence=comple[10][unicount]
                prot_seq=DyndbProteinSequence.objects.filter(sequence=binsequence) #check if that sequence already exists
                if len(prot_seq)>0:
                    cprotid=newrecord(['dyndb_complex_protein',DyndbComplexProtein],{'id_complex_exp':complex_id,'id_protein':prot_seq[0].id_protein.id},True)
                    recorded_ids['cprotein']=cprotid

                #The sequece of this protein is NOT in the DB
                #maybe that uniprot entry exists, but with a different sequence (a new mutant with respect to the cannonical not yet recorded in our DB)
                else:
                    DBproteins=DyndbProtein.objects.filter(uniprotkbac=uniprot).filter(is_mutated=False)
                    if len(DBproteins)>0:
                        cannonical_id=DBproteins[0].id
                        if len(DyndbCannonicalProteins.objects.filter(id_protein=cannonical_id))==0:
                            newrecord(['dyndb_cannonical_proteins',DyndbCannonicalProteins],{'id_protein':cannonical_id})

                        #our current protein is a mutant.
                        jj=1
                        isoflag=0
                        #check the isoform of this sequence
                        while jj<20 and isoflag==0:
                            time.sleep(round(jj*0.05,2))
                            response = requests.get("http://www.uniprot.org/uniprot/"+uniprot+"-"+str(jj)+".fasta")
                            seqlist=response.text.split('\n')[1:] #skip header
                            seq=''.join(seqlist)
                            if seq==binsequence:
                                isoformid=jj
                                isoflag=1
                            jj+=1
                        try:
                            data,errdata = retreive_data_uniprot(uniprot,isoform=isoformid,columns='id,entry name,organism,length,')
                            #data {'Entry': 'Q9UQ88', 'Entry name': 'CD11A_HUMAN', 'Length': '783', 'Organism': 'Homo sapiens (Human)'} 
                            data['speciesid'], data['Organism'] = get_uniprot_species_id_and_screen_name(data['Entry Name'].split('_')[1])
                        except:
                            data,errdata = retreive_data_uniprot(uniprot,columns='id,entry name,organism,length,')
                            data['speciesid'], data['Organism'] = get_uniprot_species_id_and_screen_name(data['Entry Name'].split('_')[1])                            

                        id_uniprot_species=data['speciesid']
                        seqdata,errdata = retreive_fasta_seq_uniprot(uniprot)
                        namedata,errdata = retreive_protein_names_uniprot(uniprot)
                        namedataori=namedata
                        seqdata=seqdata['sequence']
                        namedata=namedata['RecName'][0]['Full'][0]
                        if uniprot in gpcr_uniprot_codes: #if this uniprot code is a GPCR, find its id in receptor_id_protein
                            receptor_protein_id=str(Protein.objects.filter(accession=uniprot)[0].id)
                            prot_id=newrecord(['dyndb_protein',DyndbProtein],{'uniprotkbac':uniprot,'name':namedata,'is_mutated':'True','isoform':isoformid,'receptor_id_protein':receptor_protein_id,'id_uniprot_species':id_uniprot_species, 'is_published':True},True)

                        else:
                            prot_id=newrecord(['dyndb_protein',DyndbProtein],{'uniprotkbac':uniprot,'name':namedata,'is_mutated':'True','isoform':isoformid,'id_uniprot_species':id_uniprot_species,'is_published':True},True)
             
                        try:
                            preference_id=DyndbReferences.objects.filter(doi='https://doi.org/10.1093/nar/gku989')[0].id
                        except: #if the DB has not the reference to Uniprot already created, do it.

                            preference_id=newrecord(['dyndb_references',DyndbReferences],{'doi':'https://doi.org/10.1093/nar/gku989','url':'https://academic.oup.com/nar/article-lookup/doi/10.1093/nar/gku989','authors':'The UniProt Consortium','title':'UniProt: a hub for protein information','dbname':'Uniprot','journal_press':'Nucleic Acids Research','pub_year':'2014','volume':'43','pages':'D204'},True)

                        newrecord(['dyndb_references_protein',DyndbReferencesProtein],{'id_protein':prot_id,'id_references':preference_id},True)
                        for name in namedataori['RecName'][0]['Full']:
                            newrecord(['dyndb_other_protein_names',DyndbOtherProteinNames],{'id_protein':prot_id,'other_names':name},True)

                        newrecord(['dyndb_protein_cannonical_protein',DyndbProteinCannonicalProtein],{'id_protein':prot_id,'id_cannonical_proteins':cannonical_id},True) 
                        newrecord(['dyndb_protein_sequence',DyndbProteinSequence],{'id_protein':prot_id,'sequence':binsequence,'length':len(seqdata)})
                        cprotid=newrecord(['dyndb_complex_protein',DyndbComplexProtein],{'id_complex_exp':complex_id,'id_protein':prot_id},True)
                        recorded_ids['cprotein']=cprotid
                        alignment=align_wt_mut(seqdata,binsequence)
                        residcounter=0
                        while residcounter<len(alignment[0]):
                            if alignment[0][residcounter]!=alignment[1][residcounter]:
                                print('\n\n\n\nSequences do not match:\n\n\n\n\n\n\n\n')
                                a=[str(prot_id),str(residcounter+1),str(alignment[0][residcounter]),str(alignment[1][residcounter])]
                                print(a)
                                time.sleep(1)
                                newrecord(['dyndb_protein_mutations',DyndbProteinMutations],{'id_protein':prot_id,'resid':residcounter+1,'resletter_from':alignment[0][residcounter],'resletter_to':alignment[1][residcounter]},True)

                            residcounter+=1

                    #New Uniprot Code
                    else:
                        ij=1
                        isoflag=0
                        #check the isoform of the this new unicode
                        while ij<20 and isoflag==0:
                            time.sleep(round(ij*0.05,2))
                            response = requests.get("http://www.uniprot.org/uniprot/"+uniprot+"-"+str(ij)+".fasta")
                            seqlist=response.text.split('\n')[1:] #skip header
                            seq=''.join(seqlist)
                            if seq==binsequence:
                                isoformid=ij
                                isoflag=1
                            ij+=1
                        data,errdata = retreive_data_uniprot(uniprot,isoform=isoformid,columns='id,accession,organism_name,length,')

                        #BEFORE ISOFORM: data,errdata = retreive_data_uniprot(uniprot,isoform=None,columns='id,entry name,organism,length,')
                        #data {'Entry': 'Q9UQ88', 'Entry name': 'CD11A_HUMAN', 'Length': '783', 'Organism': 'Homo sapiens (Human)'}
                        try:
                            data['speciesid'], data['Organism'] = get_uniprot_species_id_and_screen_name(data['Entry Name'].split('_')[1])
                        except KeyError:
                            time.sleep(2)
                            data,errdata = retreive_data_uniprot(uniprot,columns='id,entry name,organism,length,') #use default isoform
                            try:
                                data['speciesid'], data['Organism'] = get_uniprot_species_id_and_screen_name(data['Entry Name'].split('_')[1])
                            except KeyError:
                                print('error retrieving data from uniprot. Invalid uniprot accession code?'+uniprot) 

                        id_uniprot_species=data['speciesid']
                        namedata,errdata = retreive_protein_names_uniprot(uniprot)
                        namedataori=namedata
                        namedata=namedata['RecName'][0]['Full'][0]

                        if uniprot in gpcr_uniprot_codes:
                            receptor_protein_id=str(Protein.objects.filter(accession=uniprot)[0].id)
                            prot_id=newrecord(['dyndb_protein',DyndbProtein],{'uniprotkbac':uniprot,'name':namedata,'is_mutated':'False','isoform':isoformid,'receptor_id_protein':receptor_protein_id,'id_uniprot_species':id_uniprot_species,'is_published':True},True)
                        else:
                            prot_id=newrecord(['dyndb_protein',DyndbProtein],{'uniprotkbac':uniprot,'name':namedata,'is_mutated':'False','isoform':isoformid,'id_uniprot_species':id_uniprot_species,'is_published':True},True) 
                        try:
                            preference_id=DyndbReferences.objects.filter(doi='https://doi.org/10.1093/nar/gku989')[0].id
                        except:
                            preference_id=newrecord(['dyndb_references',DyndbReferences],{'doi':'https://doi.org/10.1093/nar/gku989','url':'https://academic.oup.com/nar/article-lookup/doi/10.1093/nar/gku989','authors':'The UniProt Consortium','title':'UniProt: a hub for protein information','dbname':'Uniprot','journal_press':'Nucleic Acids Research','pub_year':'2014','volume':'43','pages':'D204'},True)

                        newrecord(['dyndb_references_protein',DyndbReferencesProtein],{'id_protein':prot_id,'id_references':preference_id},True)

                        for name in namedataori['RecName'][0]['Full']:
                            newrecord(['dyndb_other_protein_names',DyndbOtherProteinNames],{'id_protein':prot_id,'other_names':name},True)

                        cannonical_id=prot_id
                        newrecord(['dyndb_cannonical_proteins',DyndbCannonicalProteins],{'id_protein':cannonical_id})
                        newrecord(['dyndb_protein_cannonical_protein',DyndbProteinCannonicalProtein],{'id_protein':prot_id,'id_cannonical_proteins':cannonical_id},True)
                        newrecord(['dyndb_protein_sequence',DyndbProteinSequence],{'id_protein':prot_id,'sequence':binsequence,'length':len(binsequence)})
                        cprotid=newrecord(['dyndb_complex_protein',DyndbComplexProtein],{'id_complex_exp':complex_id,'id_protein':prot_id},True)
                        recorded_ids['cprotein']=cprotid
                unicount+=1

            #Create the compound and complexcompound, if it does not exist
            DBcompound=DyndbCompound.objects.filter(pubchem_cid=comple[2])
            compdbsinchi=DyndbCompound.objects.filter(sinchi=comple[1][6:],sinchikey=comple[0])
            if len(DBcompound)>0:
                compound_id=DBcompound[0].id
                #compound already existed, no need to record it
                try:
                    molecule_id=DyndbMolecule.objects.filter(id_compound=compound_id).filter(description='Standard form BindingDB')[0].id
                except:
                    return recorded_ids
                    
                cmolmol=DyndbComplexMoleculeMolecule.objects.filter(id_molecule=molecule_id).filter(id_complex_molecule=cmol_id).filter(type=0)
                if len(cmolmol)==0:
                    cmolmol=newrecord(['dyndb_complex_molecule_molecule',DyndbComplexMoleculeMolecule],{'id_molecule':molecule_id,'id_complex_molecule':cmol_id,'type':0},True)
                    recorded_ids['cmolmol']=cmolmol

            elif len(compdbsinchi)>0:
                compound_id=compdbsinchi[0].id
                #compound already existed, mo need to record it
                try:
                    molecule_id=DyndbMolecule.objects.filter(id_compound=compound_id).filter(description='Standard form BindingDB')[0].id
                except:
                    return recorded_ids
                cmolmol=DyndbComplexMoleculeMolecule.objects.filter(id_molecule=molecule_id).filter(id_complex_molecule=cmol_id).filter(type=0)
                if len(cmolmol)==0:
                    newrecord(['dyndb_complex_molecule_molecule',DyndbComplexMoleculeMolecule],{'id_molecule':molecule_id,'id_complex_molecule':cmol_id,'type':0},True)
                    recorded_ids['cmolmol']=cmolmol

            else:      
                pubchem_id=comple[2]
                #write this string into file comple[11]
                try:
                    nextid=DyndbFiles.objects.latest('id').id+1
                except:
                    nextid=1
                try:
                    nextmol=DyndbMolecule.objects.latest('id').id+1
                except:
                    nextmol=1
                SDFname=get_file_name('molecule',nextid,nextmol,ext='sdf',subtype='molecule')
                SDFpath=get_file_paths('molecule')
                SDFpath=SDFpath+SDFname

                PNGname=get_file_name('molecule',nextid+1,nextmol,ext='png',subtype='image')
                PNGpath=get_file_paths('molecule')
                PNGpath=PNGpath+PNGname

                datapubchem,errdata = retreive_compound_png_pubchem('cid',pubchem_id,outputfile=PNGpath,width=300,height=300) #works
                if comple[11]!='iuphar':
                    with open(SDFpath,'w+') as sdfhand:
                        for line in comple[11]:
                            sdfhand.write(line)
                else:
                    datasdfpubchem,errdata = retreive_compound_sdf_pubchem('cid',pubchem_id,outputfile=SDFpath,in3D=True)

                dyndbfilesid=newrecord(['dyndb_files',DyndbFiles],{'filename':SDFname,'filepath':SDFpath,'id_file_types':20},True)

                dyndbpngid=newrecord(['dyndb_files',DyndbFiles],{'filename':PNGname,'filepath':PNGpath,'id_file_types':19},True)

                #GET MOLECULE INFO FROM SDF FILE
                try:
                    molprop=generate_molecule_properties_BindingDB(SDFpath)
                except:
                    url_cidtosdf='https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/'+pubchem_id+'/SDF?record_type=3d'
                    response=requests.get(url_cidtosdf)
                    if response.status_code==200:
                        with open(SDFpath,'w') as sdfh:
                            sdfh.write(response.text)
                        molprop=generate_molecule_properties_BindingDB(SDFpath)
                    else:                    
                        #No 3D file for that compound, try 2d
                        url_cidtosdf='https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/'+pubchem_id+'/SDF?record_type=2d'
                        response=requests.get(url_cidtosdf)
                        if response.status_code==200:
                            with open(SDFpath,'w') as sdfh:
                                sdfh.write(response.text)
                            try:
                                molprop=generate_molecule_properties_BindingDB(SDFpath)
                            except:
                                print('can not generate molecule properties from SDF 2D file')
                                return recorded_ids
                        else:
                            print('no 2d file for that compound. error.',puchem_id) 
                            return recorded_ids

                try:
                    iupac,errdata = retreive_compound_data_pubchem_post_json('cid',pubchem_id,operation='property',outputproperty='IUPACName')
                    iupac=iupac['PropertyTable']['Properties'][0]['IUPACName']
                except:
                    iupac='NOT DEFINED, PUBCHEMID:'+str(pubchem_id)

                try:
                    names,errdata = retreive_compound_data_pubchem_post_json('cid',pubchem_id,operation='synonyms') #different names
                    cnames=[]
                    for name in names['InformationList']['Information'][0]['Synonym']:
                        cnames.append(name)
                    defname=scorenames(cnames)
                    if len(defname)<60:
                        defname=defname
                    else:
                        defname='PubChemID:'+str(pubchem_id)
                except:
                    defname='PubChemID:'+str(pubchem_id)
                
                names=defname
                try:
                    sinchi,errdata = retreive_compound_data_pubchem_post_json('cid',pubchem_id,operation='property',outputproperty='InChI')
                    sinchi=sinchi['PropertyTable']['Properties'][0]['InChI'][6:]
                except:
                    return recorded_ids
                try:
                    sinchikey,errdata=retreive_compound_data_pubchem_post_json('cid',pubchem_id,operation='property',outputproperty='InChIKey')
                    sinchikey=sinchikey['PropertyTable']['Properties'][0]['InChIKey']
                except:
                    return recorded_ids 

                if comple[3]!='': #write chembleid when available
                    try:
                        compound_id=newrecord(['dyndb_compound',DyndbCompound],{'name':names,'iupac_name':iupac,'pubchem_cid':pubchem_id,'sinchi':sinchi,'sinchikey':sinchikey,'chemblid':comple[3],'is_published':True},True)
                        recorded_ids['compound']=compound_id
                    except:
                        try:
                            no_name='PubChemID:'+str(pubchem_id)
                            compound_id=newrecord(['dyndb_compound',DyndbCompound],{'name':no_name,'iupac_name':iupac,'pubchem_cid':pubchem_id,'sinchi':sinchi,'sinchikey':sinchikey,'chemblid':comple[3],'is_published':True},True)
                            recorded_ids['compound']=compound_id
                        except: #maybe chemblid is duplicated. sometimes different pubchemids have the same chembleid...Sad! 115216 and 6917920 have chemblid: 297624 according to BindingDB
                            return recorded_ids
                else:
                    try:
                        compound_id=newrecord(['dyndb_compound',DyndbCompound],{'name':names,'iupac_name':iupac,'pubchem_cid':pubchem_id,'sinchi':sinchi,'sinchikey':sinchikey,'is_published':True},True)
                        recorded_ids['compound']=compound_id

                    except:
                        try:
                            no_name='PubChemID:'+str(pubchem_id)
                            compound_id=newrecord(['dyndb_compound',DyndbCompound],{'name':no_name,'iupac_name':iupac,'pubchem_cid':pubchem_id,'sinchi':sinchi,'sinchikey':sinchikey,'is_published':True},True)
                            recorded_ids['compound']=compound_id
                        except:
                            return recorded_ids
                        
                #recording alternative names
                for name in cnames[:50]:
                    if len(name)<200:
                        newrecord(['dyndb_other_compound_names',DyndbOtherCompoundNames],{'id_compound':compound_id,'other_names':name},True)

                urlcompo='https://pubchem.ncbi.nlm.nih.gov/summary/summary.cgi?cid=[compound id]'
                compound_reference=DyndbReferences.objects.filter(authors='National Center for Biotechnology Information. PubChem Compound Database').filter(title='Compound data comes from Pubchem')
                if len(compound_reference)==0:
                    creference_id=newrecord(['dyndb_references',DyndbReferences],{'url':urlcompo,'authors':'National Center for Biotechnology Information. PubChem Compound Database','dbname':'PubChem Compound Database','title':'Compound data comes from Pubchem'},True)
                else:
                    creference_id=compound_reference[0].id
                refcompound=newrecord(['dyndb_references_compound',DyndbReferencesCompound],{'id_compound':compound_id,'id_references':creference_id},True)
                recorded_ids['refcompound']=refcompound

                try:
                    molecule_id=newrecord(['dyndb_molecule',DyndbMolecule],{'id_compound':compound_id,'description':'Standard form BindingDB','net_charge':molprop['charge'],'inchi':molprop['inchi']['inchi'][6:],'inchikey':molprop['inchikey'],'inchicol':molprop['inchicol'],'smiles':molprop['smiles'],'is_published':True},True)

                except: #inchicol problem or molprop referenced before assigment
                    try:
                        maxcol=1
                        for mol in DyndbMolecule.objects.filter(inchikey=str(molprop['inchikey'])):
                            col=mol.inchicol
                            if col>maxcol:
                                maxcol=col
                        maxcol=maxcol+1
                    except UnboundLocalError: #local variable 'molprop' referenced before assignment
                        return recorded_ids
                    try:
                        molecule_id=newrecord(['dyndb_molecule',DyndbMolecule],{'id_compound':compound_id,'description':'Standard form BindingDB','net_charge':molprop['charge'],'inchi':molprop['inchi']['inchi'][6:],'inchikey':molprop['inchikey'],'inchicol':maxcol,'smiles':molprop['smiles'],'is_published':True},True)
                    except:
                        #molecule_id wont be defined if there is an error, do not try to add it to the recorded_ids because then it will fail and wont allow us to return the recorded_ids with the compound
                        return recorded_ids

                with closing(connection.cursor()) as cursor:
                    cursor.execute ("""
                       UPDATE dyndb_compound
                       SET std_id_molecule=%s
                       WHERE id=%s
                    """, ( str(molecule_id),str(compound_id) )  )

                newrecord(['dyndb_files_molecule',DyndbFilesMolecule],{'id_molecule':molecule_id,'id_files':dyndbfilesid,'type':0},True)
                newrecord(['dyndb_files_molecule',DyndbFilesMolecule],{'id_molecule':molecule_id,'id_files':dyndbpngid,'type':2},True)
                pubchemref=DyndbReferences.objects.filter(title='Information for this molecule was obtained via PubChem API and RDKit tools')
                if len(pubchemref)==0:
                    mreference_id=newrecord(['dyndb_references',DyndbReferences],{'url':'https://pubchem.ncbi.nlm.nih.gov/','authors':'National Center for Biotechnology Information. PubChem Compound Database','title':'Information for this molecule was obtained via PubChem API and RDKit tools','dbname':'PubChem Compound Database'},True)
                else:
                    mreference_id=pubchemref[0].id
                newrecord(['dyndb_references_molecule',DyndbReferencesMolecule],{'id_molecule':molecule_id,'id_references':mreference_id},True)
                newrecord(['dyndb_complex_molecule_molecule',DyndbComplexMoleculeMolecule],{'id_molecule':molecule_id,'id_complex_molecule':cmol_id,'type':0},True)

            newrecord(['dyndb_complex_compound',DyndbComplexCompound],{'id_compound':compound_id,'id_complex_exp':complex_id,'type':0},True)


        intdata_id=recorded_ids['intdata'][0]
        id_complex_exp=DyndbExpInteractionData.objects.filter(id=intdata_id)[0].id_complex_exp.id #ecfifty type with that complex exp
        prot_id=DyndbComplexProtein.objects.filter(id_complex_exp=id_complex_exp)[0].id_protein.id
        compound_id=DyndbComplexCompound.objects.filter(id_complex_exp=id_complex_exp)[0].id_compound.id
        with closing(connection.cursor()) as cursor:
            cursor.execute ("""
               UPDATE dyndb_exp_interaction_data
               SET ligand1=%s,protein1=%s
               WHERE id=%s
            """, ( str(compound_id), str(prot_id), str(intdata_id) )  )
    except:
        return recorded_ids

def fill_db(chunks):
    log=open('./errorfillDBlog.log','w')
    for chunk in chunks:
        pos=0
        neg=0
        print('Proccessing chunk:',chunk, '\n\n this are all the chunks:\n',str(chunks))
        complexes=get_complexes(chunk)
        complecount=0
        for comple in complexes:
            print('Progress in chunk '+chunk[chunk.rfind('/')+1:]+' is: '+str((complecount/len(complexes))*100)+ 'with '+str(neg)+' errors and '+str(pos)+' successes')
            complecount+=1
            #record_complex_in_DB(comple,fromiuphar=False)
            try:
                error_dict=record_complex_in_DB(comple,fromiuphar=False) #only saves the return value if it finishes without errror! keeps the prevous one!
                if type(error_dict)==dict:
                    neg+=1
                    log.write(str(comple))
                    log.write('THIS IS WHAT THE FUNCTION RETURNS:')
                    log.write(str(error_dict))
                    print('\n\n\nError in chunk: '+chunk+'\n\n\n')

                    for instance_id in error_dict['bind']:
                        try:
                            log.write('Deleting binding record...\n')
                            instance = DyndbBinding.objects.get(id=instance_id)
                            instance.delete()                                          
                        except:
                            log.write('error dele binding\n')
                            continue

                    for instance_id in error_dict['ki']:
                        try:
                            log.write('Deleting ki record...\n')
                            instance = DyndbInhibition.objects.get(id=instance_id)
                            instance.delete()                                          
                        except:
                            log.write('error dele ki\n')
                            continue

                    for instance_id in error_dict['ec50']:
                        try:
                            log.write('deltetin eff record\n')
                            instance = DyndbEfficacy.objects.get(id=instance_id)
                            instance.delete()
                        except:
                            log.write('error deleting eff\n')
                            continue   

                    for instance_id in error_dict['ic50']:
                        try:
                            log.write('deltetin eff record\n')
                            instance = DyndbEfficacy.objects.get(id=instance_id)
                            instance.delete()
                        except:
                            log.write('error deleting eff\n')
                            continue  
  

                    for instance_id in error_dict['intdataref']:
                        try:
                            log.write('trying to delete intdataref\n')
                            instance = DyndbReferencesExpInteractionData.objects.get(id=instance_id)
                            instance.delete()
                        except:
                            log.write('error deleting intdataref\n')
                            continue

                    for instance_id in error_dict['intdata']:
                        try:
                            log.write('deletin intdata...\n')
                            instance = DyndbExpInteractionData.objects.get(id=instance_id)
                            instance.delete()
                        except:
                            log.write('error deleting intdata\n')
                            continue
                    try:
                        log.write('deleting cmolmol\n')
                        instance = DyndbComplexMoleculeMolecule.objects.get(id=error_dict['cmolmol'])
                        instance.delete()
                    except:
                        log.write('error deleting cmolmol\n')
                        pass
                    
                    try:
                        log.write('deleting cmol\n')
                        instance = DyndbComplexMolecule.objects.get(id=error_dict['complexmol'])
                        instance.delete()
                    except:
                        log.write('error deleting cmol\n')
                        pass
                    
                    try:
                        log.write('deleting cprot\n')
                        instance = DyndbComplexProtein.objects.get(id=error_dict['cprotein'])
                        instance.delete()
                    except:
                        log.write('error deleting cprot\n')
                        pass
                    
                    try:
                        log.write('deleting cexp\n')
                        instance = DyndbComplexExp.objects.get(id=error_dict['complexid'])
                        instance.delete()
                    except:
                        log.write('error deleting cexp\n')
                        pass                
                    try:
                        log.write('trying to delete refcom\n')
                        instance = DyndbReferencesCompound.objects.get(id=error_dict['refcompound'])
                        instance.delete()
                    except:
                        log.write('error deleting refcom\n')
                        pass
                    
                    try:
                        log.write('lets delete that compound\n')
                        log.write(error_dict['compound'])                
                        instance = DyndbCompound.objects.get(id=error_dict['compound'])
                        instance.delete()
                    except:
                        log.write('error del compound\n')
                        pass
                    
                    try:
                        log.write('deltin molecule\n')
                        instance = DyndbMolecule.objects.get(id=error_dict['molecule'])
                        instance.delete()
                    except:
                        log.write('error deleting molecule\n')
                        pass

                    continue
                else:
                    print('\n\n\nComplex recorded without errors.\n\n\n')
                    pos+=1
            except:
                raise
        print('this chunk had ',str(neg),'errors and',str(pos),'successes')
        time.sleep(5)
                
def fill_db_iuphar(filename):
    '''Fills Binding and efficacy table with IUPHAR csv data. The file iuphar_useful_complexes_pickle is a serialized python list,
     containing the csv records in a format available to the record_complex_in_DB function. This file is created after the first use. '''
    records=iuphar_parser(filename)
    try:
        with open (settings.MODULES_ROOT + '/iuphar_useful_complexes_pickle', 'rb') as fp:
            complexes = pickle.load(fp)
        print('Pickle found...this is going to be fast')
    except:
        print('This could take a while...')
        complexes=to_bindingdb_format(records)
        with open (settings.MODULES_ROOT + '/iuphar_useful_complexes_pickle', 'wb') as fp:
            pickle.dump(complexes,fp) 
    print('lets record in DB')
    for comple in complexes:
        try:
            record_complex_in_DB(comple,fromiuphar=True)
        except:
            raise

mypath=settings.MODULES_ROOT + '/dynadb/chunks/chunksBindingDB'
chunks=[os.path.join(mypath, f) for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))][28:]
fill_db(chunks)
fill_db_iuphar('./dynadb/interactions.csv')
