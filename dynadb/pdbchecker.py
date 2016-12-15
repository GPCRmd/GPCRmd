#from __future__ import print_function
import os.path as path
from os import devnull
from functools import cmp_to_key
from operator import itemgetter
from .customized_errors import ParsingError


import os
import sys
#sys.tracebacklimit = 0
#import argparse
#from molvs.metal import MetalDisconnector
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem import rdinchi
from rdkit import rdBase
from rdkit.Chem import GetPeriodicTable
import fileinput
import logging
import numpy as np
import re
from rdkit.Chem.AllChem import AssignBondOrdersFromTemplate
from rdkit.Chem import Draw
from rdkit.Chem.Draw.MolDrawing import DrawingOptions

#logging.basicConfig(filename='example.log',level=logging.CRITICAL)

from .molecule_properties_tools import stdout_redirected,remove_isotopes

rdBase.DisableLog('rdApp.debbug')
rdBase.DisableLog('rdApp.info')
rdBase.DisableLog('rdApp.warning')
rdBase.EnableLog('rdApp.error')
rdBase.EnableLog('rdApp.critical')

import logging

nometals = {'H','He','B', 'C','N','O','F','Ne','Si','P','S','Cl','Ar','Ge','As','Se','Br','Kr','Te','I','Xe','At','Rn'}


def write_entry(line,fileh,serial):
    if serial < 99999:
        newserial = "%5d" % serial
    else:
        newserial = "*****" 
    
    print("".join((line[:6],newserial,line[11:])), file=fileh,end="")
    
def split_protein_pdb(filename,modeled_residues,outputfolder=None):
        '''Get sequence from a PDB file in a given interval defined by a combination of Segment Identifier (segid), starting residue number (start), end residue number (stop), chain identifier (chain). All can be left in blank. Returns 1) a list of minilist: each minilist has the resid and the aminoacid code. 2) a string with the sequence.'''
        fpdb=open(filename,'r')
        header = "CRYST1    0.000    0.000    0.000  90.00  90.00  90.00 P 1           1"
        rootname,ext = path.splitext(filename)
        if outputfolder is not None:
            basename = path.basename(rootname)
            rootname = path.join(outputfolder,basename)
        proteinpdbfilename = rootname+"_protein.pdb"
        proteinpdb = open(proteinpdbfilename,'w',newline='\n')
        print(header, file=proteinpdb)
        nonproteinpdbfilename = rootname+"_non_protein.pdb"
        nonproteinpdb = open(nonproteinpdbfilename,'w',newline='\n')
        print(header, file=nonproteinpdb)

        cpos=0 #current residue position
        ppos=0 #previous residue position
        ppos2='0' #previous position after converting hexadecimals to decimals
        protein_serial = 0
        non_protein_serial = 0
        hexflag=0
        pfields={ 'record':None,'serial': None,'name': None,'altloc':None,'resname':None,
        'chain':None,'resid':None,'x':None,'y':None,'z':None,'occupancy':None,
        'beta':None,'segid':None,'element':None,'charge':None}
        required_fields = {'serial','name','resname','resid','x','y','z','occupancy','beta'}
        for line in fpdb:
                if line.startswith('ATOM') or line.startswith('HETATM'):
                        fields={ 'record':line[0:6],'serial': line[6:11],'name': line[11:16],'altloc':line[16],'resname':line[17:21],
                        'chain':line[21],'resid':line[22:27],'x':line[30:38],'y':line[38:46],'z':line[46:54],'occupancy':line[54:60],
                        'beta':line[60:66],'segid':line[72:76],'element':line[76:78],'charge':line[78:80]}
                        #fields=[ '','' ,'' ,line[17:21],line[21],line[22:27],line[30:38],line[38:46],line[46:54],line[72:76]] 
                        #fields[3]:Aminoacid code, fields[4]:chain, fields[5]:resid, fields[6-8]:X,Y,Z coordinates
                        for field in fields:
                            fields[field] = fields[field].strip()

                        for field in required_fields:
                                if fields[field].strip()=='':
                                    raise ParsingError('Missing required field "'+field+'" in the PDB file at line:\n'+line)
                                        
                        if fields['resid']!=pfields['resid']: #resid has changed->new aa
                            if fields['chain']!=pfields['chain']  or fields['segid']!=pfields['segid'] or fields['segid'] == '1':
                                #resid count has been reseted by new chain, new segid or whatever. 
                                ppos='0'
                                hexflag=0
                            cpos=fields['resid'] #current position (resid) in the pdb during the present loop cycle
                            try:
                                if hexflag==1:
                                        cpos2=int(str(cpos),16)
                                        ppos2=int(str(ppos),16)
                                elif hexflag==0:
                                        cpos2=int(cpos)
                                        ppos2=int(ppos)
                                if cpos=='2710' and ppos=='9999':
                                        cpos2=int(cpos,16)
                                        hexflag=1
                            except ValueError:
                                raise ParsingError('Invalid resid format at line:\n'+line)        
                            ppos=cpos
                            pfields=fields
                            
                            protein = False
                            for rownum,row in modeled_residues.items():
                                chain = row['chain']
                                start = row['resid_from']
                                stop =  row['resid_to']
                                segid = row['segid']
                                if (fields['chain']==chain or chain == '') and cpos2 >= start and cpos2 <= stop and (segid in fields['segid'] or segid==''):
                                    protein = True
                                    break
                                    
                        if protein:
                            protein_serial +=1
                            write_entry(line,proteinpdb,protein_serial)
                        else:
                            non_protein_serial +=1
                            write_entry(line,nonproteinpdb,non_protein_serial)
        print("END", file=proteinpdb)
        print("END", file=nonproteinpdb)
        fpdb.close()
        proteinpdb.close()
        nonproteinpdb.close()

        return (proteinpdbfilename,nonproteinpdbfilename)
def split_resnames_pdb(filename,outputfolder=None):
    '''Get sequence from a PDB file in a given interval defined by a combination of Segment Identifier (segid), starting residue number (start), end residue number (stop), chain identifier (chain). All can be left in blank. Returns 1) a list of minilist: each minilist has the resid and the aminoacid code. 2) a string with the sequence.'''
    rootname,ext = path.splitext(filename)
    if outputfolder is not None:
        basename = path.basename(rootname)
        rootname = path.join(outputfolder,basename)
    fpdb=open(filename,'r')
    header = "CRYST1    0.000    0.000    0.000  90.00  90.00  90.00 P 1           1"
    fileh = open(devnull,'w')
    cpos=0 #current residue position
    ppos=0 #previous residue position
    ppos2='0' #previous position after converting hexadecimals to decimals
    data = dict()
    hexflag=0
    pfields={ 'record':None,'serial': None,'name': None,'altloc':None,'resname':None,
    'chain':None,'resid':None,'x':None,'y':None,'z':None,'occupancy':None,
    'beta':None,'segid':None,'element':None,'charge':None}
    #pfields=['','' ,'','AAA','Z','0','0','0','0','']
    required_fields = {'serial','name','resname','resid','x','y','z','occupancy','beta','element'}
    for line in fpdb:
            if line.startswith('ATOM') or line.startswith('HETATM'):
                    fields={ 'record':line[0:6],'serial': line[6:11],'name': line[11:16],'altloc':line[16],'resname':line[17:21],
                    'chain':line[21],'resid':line[22:27],'x':line[30:38],'y':line[38:46],'z':line[46:54],'occupancy':line[54:60],
                    'beta':line[60:66],'segid':line[72:76],'element':line[76:78],'charge':line[78:80]}
                    

                    for field in fields:
                        fields[field] = fields[field].strip()

                    for field in required_fields:
                            if fields[field].strip()=='':
                                    raise ParsingError('Missing required field "'+field+'" in the PDB file at line:\n'+line)
                    cresname = fields['resname']
                    if cresname!=pfields['resname']:
                        fileh.close()
                       
                        if cresname not in data:
                            rfilename = "".join((rootname,'_',cresname,'.pdb'))
                            data[cresname] = dict()
                            data[cresname]['serial'] = 0
                            data[cresname]['filename'] = rfilename
                            data[cresname]['residues'] = set()
                            fileh = open(rfilename,'w',newline='\n')
                            print(header,file=fileh)
                            
                        else:
                            fileh = open(data[cresname]['filename'],'a',newline='\n')
                    if fields['resid']!=pfields['resid']: #resid has changed->new aa

                        if fields['chain']!=pfields['chain']  or fields['segid']!=pfields['segid'] or fields['segid'] == '1':
                            #resid count has been reseted by new chain, new segid or whatever. 
                            ppos='0'
                            hexflag=0
                        cpos=fields['resid'] #current position (resid) in the pdb during the present loop cycle
                        try:
                            if hexflag==1:
                                    cpos2=int(str(cpos),16)
                                    ppos2=int(str(ppos),16)
                            elif hexflag==0:
                                    cpos2=int(cpos)
                                    ppos2=int(ppos)
                            if cpos=='2710' and ppos=='9999':
                                    cpos2=int(cpos,16)
                                    hexflag=1
                        except ValueError:
                            raise ParsingError('Invalid resid format at line:\n'+line)
                        ppos=cpos
                        pfields=fields
                    data[cresname]['residues'].add('_'.join((fields['chain'],fields['segid'],str(cpos2))))
                    data[cresname]['serial'] +=1 
                    write_entry(line,fileh,data[cresname]['serial'])

    fileh.close()
    for resname in data:
        data[resname].pop('serial')
        data[resname].pop('residues')
        fileh = open(data[resname]['filename'],'a',newline='\n')
        print("END",file=fileh)
        fileh.close()
    return data

def cmp(a,b):
    return (a > b) - (a < b)
def sort_residue(x,y):
    xlist = x.split('_')
    ylist = y.split('_')
    for xe,ye in zip(xlist,ylist):
        if xe.isdigit() and ye.isdigit():
            cmpr = cmp(int(xe),int(ye))
        else:
            cmpr = cmp(xe,ye)
        if cmpr != 0:
            return cmpr
    return cmp(len(xlist),len(ylist))


def molecule_atoms_unique_pdb(filename,outputfolder=None,logfile=devnull):
    '''Get sequence from a PDB file in a given interval defined by a combination of Segment Identifier (segid), starting residue number (start), end residue number (stop), chain identifier (chain). All can be left in blank. Returns 1) a list of minilist: each minilist has the resid and the aminoacid code. 2) a string with the sequence.'''
    rootname,ext = path.splitext(filename)
    if outputfolder is not None:
        basename = path.basename(rootname)
        rootname = path.join(outputfolder,basename)
    fpdb=open(filename,'r')
    header = "CRYST1    0.000    0.000    0.000  90.00  90.00  90.00 P 1           1"
    outfilename = rootname+'_uniq.pdb'
    fileh = open(outfilename,'w',newline='\n')
    print(header, file=fileh)
    cpos=0 #current residue position
    ppos=0 #previous residue position
    ppos2='0' #previous position after converting hexadecimals to decimals
    data = dict()
    data['names'] = dict()
    data['residues'] = dict()
    hexflag=0
    uniqlines = []
    serial = 0
    errorflag = False
    pfields={ 'record':None,'serial': None,'name': None,'altloc':None,'resname':None,
    'chain':None,'resid':None,'x':None,'y':None,'z':None,'occupancy':None,
    'beta':None,'segid':None,'element':None,'charge':None}
    #pfields=['','' ,'','AAA','Z','0','0','0','0','']
    required_fields = {'serial','name','resname','resid','x','y','z','occupancy','beta','element'}
    for line in fpdb:
            if line.startswith('ATOM') or line.startswith('HETATM'):
                    serial += 1
                    fields={ 'record':line[0:6],'serial': line[6:11],'name': line[11:16],'altloc':line[16],'resname':line[17:21],
                    'chain':line[21],'resid':line[22:27],'x':line[30:38],'y':line[38:46],'z':line[46:54],'occupancy':line[54:60],
                    'beta':line[60:66],'segid':line[72:76],'element':line[76:78],'charge':line[78:80]}

                    for field in fields:
                        fields[field] = fields[field].strip()

                    for field in required_fields:
                            if fields[field].strip()=='':
                                raise ParsingError('Missing required field "'+field+'" in the PDB file at line:\n'+line)

                    if fields['resid']!=pfields['resid']: #resid has changed->new aa
                        if fields['chain']!=pfields['chain']  or fields['segid']!=pfields['segid'] or fields['segid'] == '1':
                            #resid count has been reseted by new chain, new segid or whatever. 
                            ppos='0'
                            hexflag=0

                        cpos=fields['resid'] #current position (resid) in the pdb during the present loop cycle
                        try:
                            if hexflag==1:
                                    cpos2=int(str(cpos),16)
                                    ppos2=int(str(ppos),16)
                            elif hexflag==0:
                                    cpos2=int(cpos)
                                    ppos2=int(ppos)
                            if cpos=='2710' and ppos=='9999':
                                    cpos2=int(cpos,16)
                                    hexflag=1
                        except ValueError:
                            raise ParsingError('Invalid resid format at line:\n'+line)
                        ppos=cpos
                        pfields=fields
                    cname = fields['name']
                    residue = '_'.join((fields['chain'],fields['segid'],str(cpos2)))
                    
                    # store the first residue chain_segid_resid that have an atom name
                    if cname not in data['names']:
                        data['names'][cname] = dict()
                        data['names'][cname]['first_residue'] = residue
                        # store the lines for the first residue
                        uniqlines.append(line)
                    # store atom names for each residue and the serial of the first atom
                    if residue not in data['residues']:
                        data['residues'][residue] = dict()
                        data['residues'][residue]['serial'] = serial
                        data['residues'][residue]['names'] = set()
                    if cname in data['residues'][residue]:
                        print('Duplicated atom "'+cname+'" in chain "'+fields['chain']+'", segid "'+\
                        fields['segid']+'", resid "'+fields['resid']+'".',file=logfile)
                        errorflag = True
                    data['residues'][residue]['names'].add(cname)
    
    
    
    residue_names_count = dict()
    
    # count first atom name occurrance per residue
    for name in data['names']:
        if data['names'][name]['first_residue'] not in residue_names_count:
            residue_names_count[data['names'][name]['first_residue']] = 0
        residue_names_count[data['names'][name]['first_residue']] += 1
    
    # sort by residue chain_segid_resid
    residue_list = sorted(residue_names_count.keys(),key=cmp_to_key(sort_residue))
    
    residue_names_count_items = [ (item,residue_names_count[item]) for item in residue_list]
    del residue_list
    # sort by atom name occurrance per residue in descendent order
    residue_names_count_items = sorted(residue_names_count_items,key=itemgetter(1),reverse=True)
    ref_residue = residue_names_count_items[0][0]
    
    #sort residues by serial
    residue_items = sorted(data['residues'].items(),key=lambda x: x[1]['serial'])
    residue_list = [item[0] for item in residue_items]
    atomsref = data['residues'][ref_residue]['names']
    numatomsref = len(atomsref)

    for residue in residue_list:
        atoms = data['residues'][residue]['names']
        if atoms != atomsref:
            chain,segid,cpos2 = residue.split('_')
            cpos2 = int(cpos2)
            if cpos2 > 9999:
                cpos = hex(cpos2)
            else:
                cpos = str(cpos2)
            diff_atoms_atomsref = atoms.difference(atomsref)
            diff_atomsref_atoms = atomsref.difference(atoms)
            if diff_atoms_atomsref != set():
                msg = 'Inconsistent atom name(s)'
                frase = ''.join((msg,' "'," ".join(diff_atoms_atomsref),'" in residue with chain "',chain,\
                '", segid "',segid,'" and resid "',cpos,'".'))
                print(frase,file=logfile)
                errorflag = True
            if diff_atomsref_atoms != set():
                msg = 'Missing atom name(s)'
                frase = ''.join((msg,' "'," ".join(diff_atomsref_atoms),'" in residue with chain "',chain,\
                '", segid "',segid,'" and resid "',cpos,'".'))
                print(frase,file=logfile)
                errorflag = True
    
    newserial = 0
    for line in uniqlines:
        newserial +=1
        write_entry(line,fileh,newserial)
    print("END",file=fileh)
    fileh.close()
    return outfilename,len(data['residues']),errorflag


def trimw(string):
    w = re.compile('\s+')
    return w.sub('', string)
    
def count_implicit_hydrogens(mol):
    valdiff=0
    for atom in mol.GetAtoms():    
       valdiff +=  atom.GetNumImplicitHs()
    return valdiff

def disconnect(mol):
    edmol = Chem.EditableMol(mol)
    for atom in mol.GetAtoms():
        #if atom.GetIdx() == 22:
            #edmol.RemoveBond(atom.GetIdx(),12)
            #edmol.RemoveBond(atom.GetIdx(),10)
        if atom.GetSymbol() not in nometals:
            dbondnum = 0
            for bond in atom.GetBonds():
                edmol.RemoveBond(bond.GetBeginAtom().GetIdx(),bond.GetEndAtom().GetIdx())
                dbondnum += 1
            if dbondnum != 0:
                print("WARNING: disconnecting metal atom '"+atom.GetSymbol()+"'.")
    return edmol.GetMol()
def remove_charge_formula(formula):
    chargere = re.compile(r'[-+](\d*)')
    return chargere.sub('',formula)

def fix_formula(formula,impnum):
    n = 0
    hre = re.compile(r'H(\d*)')
    m = hre.search(formula)
    if m:
        if m.group(1) == '':
            n = 1
        else:
            n = int(m.group(1))
        hnum = n-impnum
        if hnum > 0:
            return hre.sub('H'+str(hnum),formula)
        elif hnum == 0:
            return hre.sub('',formula)
        elif hnum == 1:
            return hre.sub('H',formula)
        else:
            return None
    return formula
def truncate_inchi(inchi,options):
    ver1 = re.compile(r'^1/')
    ver2 = re.compile(r'InChI=1/')
    ver1s = re.compile(r'^1S/')
    ver2s = re.compile(r'InChI=1S/')
    iso = re.compile(r'/i.*/')
    connectl = re.compile(r'/c(.*?)/')
    tinchi = inchi
    if 'connect' in options:
         m = connectl.search(tinchi)
         if m:
            return m.group(1)
         else:
            return ''
    return tinchi
def diff_mol_pdb(mol,pdbfile,logfile=os.devnull):
    with stdout_redirected(to=logfile,stdout=sys.stderr):
        with stdout_redirected(to=logfile,stdout=sys.stdout):
            remove_isotopes(mol,sanitize=True)
            nhmol = Chem.RemoveHs(mol,implicitOnly=False, updateExplicitCount=True, sanitize=True)
            try:
                Chem.Kekulize(nhmol)
            except:
                pass
            checkconnect = True
            pdbmol = None
            try:
                pdbmol = Chem.MolFromPDBFile(pdbfile,removeHs=False, sanitize=True)
            except:
                pass
            if pdbmol is None:
                pdbmol = Chem.MolFromPDBFile(pdbfile,removeHs=False, sanitize=False)
                if pdbmol is None:
                    raise ParsingError("Cannot open PDB molecule.")
                pdbmol = disconnect(pdbmol)
                Chem.SanitizeMol(pdbmol,catchErrors=True)   
            nhpdbmol = Chem.RemoveHs(pdbmol,implicitOnly=False, updateExplicitCount=True, sanitize=False)
              
            Chem.SanitizeMol(nhpdbmol,catchErrors=True)

            try:
                nhpdbmol = AssignBondOrdersFromTemplate(nhmol,nhpdbmol)
                pdbmol = Chem.AddHs(nhpdbmol,addCoords=True,explicitOnly=True)
            except:
                print("WARNING: Cannot assign bond orders from molecule file template. Checking only non-hydrogen connectivity.")
                checkconnect = False
                pass
            #Stoichiometric formula check
            impnum = count_implicit_hydrogens(pdbmol)
            result = 'OK'
            unformula = remove_charge_formula(rdMolDescriptors.CalcMolFormula(mol))


            pdbunformula = remove_charge_formula(rdMolDescriptors.CalcMolFormula(pdbmol))
            #print(pdbunformula)
            pdbunformula = fix_formula(pdbunformula, impnum)
            if unformula != pdbunformula:
                result= 'FAIL: Molecules have different Stoichiometric formulas '+unformula+' '+pdbunformula+'.'
            print('Stoichiometric formula check (without charge): '+result)
            print('Generating Fixed H InChI for molecule file ... ')
            inchi,code,msg,log,aux = rdinchi.MolToInchi(mol,options='-FixedH -DoNotAddH')
            if code == 0:
                #print(inchi)
                pass
            if code == 1:
            # print(inchi)
                print(msg)
            else:
                print(msg)
                
            print('Generating Standard InChI for molecule file ... ')
            sinchi,code,msg,log,aux = rdinchi.MolToInchi(mol,options=' -DoNotAddH')
            if code == 0:
                #print(sinchi)
                pass
            if code == 1:
                #print(sinchi)
                print(msg)
            else:
                print(msg)

            maininchi = truncate_inchi(inchi,['connect'])
            
            print('Generating Fixed H InChI for PDB molecule ... ')
            pdbinchi,code,msg,log,aux = rdinchi.MolToInchi(pdbmol,options='-FixedH -DoNotAddH')
            if code == 0:
                pass
            if code == 1:
                print(msg)
            else:
                print(msg)
                
            print('Generating Standard InChI for PDB molecule ... ')    
            pdbsinchi,code,msg,log,aux = rdinchi.MolToInchi(pdbmol,options=' -DoNotAddH')
            if code == 0:
                pass
            if code == 1:
                print(msg)
            else:
                print(msg)
                
                
            pdbmaininchi = truncate_inchi(pdbinchi,['connect'])



            failnum = 0
            result = 'OK'
            if maininchi != pdbmaininchi:
                result= 'FAIL: Molecules have diferent scaffolds\n'+maininchi+' '+pdbmaininchi+'.'
                failnum += 1
                print('Main chain InChI check: '+result)
            else:
                print('Main chain InChI check: '+result)
                result = 'OK'
                if checkconnect:
                    if sinchi != pdbsinchi:
                        result= 'FAIL: Molecules are not the same compound or have different net charge.\n'+sinchi+'\n'+pdbsinchi+'.'
                        failnum += 1
                        print('Standard InChI check: '+result)
                    else:
                        print('Standard InChI check: '+result)
                        result = 'OK'
                        if inchi != pdbinchi:
                            result= 'FAIL: Molecules have different protonation/tautomery\n'+inchi+'\n'+pdbinchi+'.'
                            failnum += 1
                        print('Fixed H InChI check: '+result)
                        print('OK')

            del nhpdbmol

            return failnum, pdbmol