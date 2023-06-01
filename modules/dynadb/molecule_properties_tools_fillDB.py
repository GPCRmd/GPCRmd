import os
import re
import io
import sys
from modules.dynadb.customized_errors import ParsingError,MultipleMoleculesinSDF,InvalidMoleculeFileExtension
from django.conf import settings
from subprocess import Popen, PIPE
from rdkit.Chem import ForwardSDMolSupplier, AssignAtomChiralTagsFromStructure, MolToSmiles, InchiToInchiKey, GetFormalCharge, RemoveHs, MolFromInchi, MolFromSmiles, SDWriter
from rdkit.Chem import MolFromInchi, AddHs, EditableMol, SanitizeMol, Kekulize, Mol, MolToMolBlock
from rdkit.Chem.rdinchi import MolToInchi
from rdkit.rdBase import EnableLog
from rdkit.Chem.Draw.MolDrawing import DrawingOptions
from rdkit.Chem import rdForceFieldHelpers
from rdkit.Chem import rdDistGeom
from rdkit.Chem.Draw import MolToFile, PrepareMolForDrawing
from rdkit.Chem.Draw.MolDrawing import DrawingOptions
from contextlib import contextmanager
from rdkit import RDLogger 


class Geometry3DGenerationError(Exception):
    def __init__(*args,**kwargs):
        msg = 'Cannot generate 3D coordinates'
        super(Geometry3DGenerationError,self).__init__(msg,*args,**kwargs)


MOLECULE_EXTENSION_TYPES = {'sdf':'sdf','sd':'sdf','mol':'mol'}

inchiheaderre = re.compile(r'InChI=')

EnableLog('rdApp.debbug')
EnableLog('rdApp.info')
EnableLog('rdApp.warning')
EnableLog('rdApp.error')
EnableLog('rdApp.critical')





def fileno(file_or_fd):
    fd = getattr(file_or_fd, 'fileno', lambda: file_or_fd)()
    if not isinstance(fd, int):
        raise ValueError("Expected a file (`.fileno()`) or a file descriptor")
    return fd


@contextmanager
def stdout_redirected(to=os.devnull, stdout=None):
    if stdout is None:
       stdout = sys.__stdout__

    stdout_fd = fileno(stdout)
    # copy stdout_fd before it is overwritten
    #NOTE: `copied` is inheritable on Windows when duplicating a standard stream
    with os.fdopen(os.dup(stdout_fd), 'wb') as copied: 
        stdout.flush()  # flush library buffers that dup2 knows nothing about
        try:
            
            os.dup2(fileno(to), stdout_fd)  # $ exec >&to
            to.flush()
        except ValueError:  # filename
            with open(to, 'ab') as to_file:
                os.dup2(to_file.fileno(), stdout_fd)  # $ exec > to
        try:
            yield stdout # allow code to be run with the redirected stdout
        finally:
            # restore stdout to its previous value
            #NOTE: dup2 makes stdout_fd inheritable unconditionally
            stdout.flush()
            os.dup2(copied.fileno(), stdout_fd)  # $ exec >&copied




def open_molecule_file(uploadedfile,logfile=os.devnull,filetype=None):
    
    #charset = 'utf-8'
    #if "charset" in uploadedfile and uploadedfile.charset is not None:
            #charset = uploadedfile.charset
    if filetype is None:
        if "filetype" not in uploadedfile or uploadedfile.filetype is None:
            basename, ext = os.path.splitext(uploadedfile.name)
            ext = ext.lower()
            ext = ext.strip('.')
            if ext in MOLECULE_EXTENSION_TYPES.keys():
                filetype = MOLECULE_EXTENSION_TYPES[ext]
                uploadedfile.filetype = filetype
            else:
                raise InvalidMoleculeFileExtension(ext=ext)
        
        else:
            filetype = uploadedfile.filetype
        
    
    with stdout_redirected(to=logfile,stdout=sys.__stderr__):
        with stdout_redirected(to=logfile,stdout=sys.__stdout__):
            print('Loading molecule...')
            uploadedfile.seek(0)
            if filetype == 'sdf' or filetype == 'mol':
                
                suppl = ForwardSDMolSupplier(uploadedfile,removeHs=False)
                mol = next(suppl)
                try:
                    next(suppl)
                except StopIteration:
                    pass
                except:
                    raise
                else:
                    raise MultipleMoleculesinSDF()
                finally:
                    del suppl
                if mol is None:
                    if filetype == 'sdf':
                        raise ParsingError("Invalid SDFile file.")
                    else:
                        raise ParsingError("Invalid MDL Mol file.")
            print('Assigning chirality from struture...')
            AssignAtomChiralTagsFromStructure(mol,replaceExistingTags=False)
            print('Finished loading molecule.')

    return mol
def generate_inchi(mol, FixedH=False, RecMet=False):
    options = "-DoNotAddH"
    if FixedH:
        options += " -FixedH"
    if RecMet:
        options += " -RecMet"
    inchi,code,msg,log,aux = MolToInchi(mol,options=options)
    
    if code == 0:
        msg = ''
    elif code == 1:
       pass
    else:
       inchi = ''
    return (inchi,code,msg)
def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

def which(program):

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def cannonicalize_smiles_openbabel(smiles,obabelcmd = "/usr/bin/obabel"):
    wspc = re.compile("\s+")
    if which("obabel"):
        obabelcmd = "obabel"
    smierr=None
    p = Popen([obabelcmd,"-ismi", "-ocan"],bufsize=-1,stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate(input=smiles.encode('UTF-8'))
    if stderr:
        smierr = stderr.decode('UTF-8')
        smierr = smierr.strip()
    smi = stdout.decode('UTF-8')
    smi = wspc.sub("",smi)
    return (smi,smierr)
    
def generate_smiles_openbabel(molblock,obabelcmd = "/usr/bin/obabel"):
    wspc = re.compile("\s+")
    if which("obabel"):
        obabelcmd = "obabel"
    smierr=None
    p = Popen([obabelcmd,"-imol", "-ocan"],bufsize=-1,stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate(input=molblock.encode('UTF-8'))
    if stderr:
        smierr = stderr.decode('UTF-8')
        smierr = smierr.strip()
    smi = stdout.decode('UTF-8')
    smi = wspc.sub("",smi)
    return (smi,smierr)

def generate_smiles2(mol,logfile=os.devnull):
    with stdout_redirected(to=logfile,stdout=sys.__stderr__):
        with stdout_redirected(to=logfile,stdout=sys.__stdout__):
            molnoar = Mol(mol)
            try:
                Kekulize(molnoar,clearAromaticFlags=True)
            except:
                pass
            smi = MolToSmiles(molnoar,isomericSmiles=True,kekuleSmiles=True,canonical=False)
            
    smi,smierr = cannonicalize_smiles_openbabel(smi)
    if isinstance(logfile,str):
        with open(logfile, 'a') as to_file:
            print(smierr,file=to_file)
    else:
        print(smierr,file=logfile)   
    return smi
    
def generate_smiles(mol,logfile=os.devnull):
    with stdout_redirected(to=logfile,stdout=sys.__stderr__):
        with stdout_redirected(to=logfile,stdout=sys.__stdout__):
            mol2 = Mol(mol) 
            mol2.SetProp("_Name","")
            molblock = MolToMolBlock(mol2,includeStereo=True)
            del mol2
            
    smi,smierr = generate_smiles_openbabel(molblock)
    if isinstance(logfile,str):
        with open(logfile, 'a') as to_file:
            print(smierr,file=to_file)
    else:
        print(smierr,file=logfile)   
    return smi
                                          
def generate_inchikey(inchi):
    return InchiToInchiKey(inchi)

def get_net_charge(mol):
    return GetFormalCharge(mol)
    
    
def get_charge_from_inchi(inchi,removeHs=False):
    mol = MolFromInchi(inchi,removeHs=removeHs)
    netc = GetFormalCharge(mol)
    del mol
    return netc

def generate_png(mol,pngpath,logfile=os.devnull,size=300):
    with stdout_redirected(to=sys.__stdout__,stdout=sys.__stderr__):
        with stdout_redirected(to=logfile,stdout=sys.__stdout__):
            nhmol = RemoveHs(mol,implicitOnly=False, updateExplicitCount=True, sanitize=False)
            SanitizeMol(nhmol,catchErrors=True)
            op = DrawingOptions()
            op.atomLabelFontSize = size/25
            MolToFile(PrepareMolForDrawing(nhmol,forceCoords=True,addChiralHs=True),\
                pngpath,fitImage=True,size=(size, size),options=op)

def neutralize_inchi(inchi):
    pmid = re.compile(r'/p([^/]*?)/')
    pend = re.compile(r'/p([^/]*?)$')
    
    m = pmid.search(inchi)
    if m:
        newinchi = inchi
        newinchi = pmid.sub('/',newinchi)
    else:
        m = pend.search(inchi)
        if m:
            newinchi = inchi + '/'
            newinchi = pmid.sub('',newinchi)
        else:
            return inchi
    return newinchi
    
def neutralize_inchikey(inchikey):
    return inchikey[:-1]+'N'
    
def validate_inchikey(inchikey):
    inchikeyre = re.compile(r'^[A-Z]{14}[-][A-Z]{10}[-][A-Z]$')
    return bool(inchikeyre.search(inchikey))
    
def standarize_mol_by_inchi(mol,neutralize=True):
    newmol = AddHs(mol)
    sinchi,code,msg = generate_inchi(newmol, FixedH=False, RecMet=False)
    if neutralize:
        nsinchi = neutralize_inchi(sinchi)
    else:
        nsinchi = sinchi
    newmol = MolFromInchi(nsinchi,removeHs=False)
    newmol = AddHs(newmol,explicitOnly=True)
    return newmol
def compare_eq_inchi_without_protonation(inchi1,inchi2):
    return bool(neutralize_inchi(inchi1) == neutralize_inchi(inchi2))
    
def compare_eq_inchikey_without_protonation(inchikey1,inchikey2):
    return bool(neutralize_inchikey(inchikey1) == neutralize_inchikey(inchikey2))

def write_sdf(mol,path):
    writer = SDWriter(path)
    writer.write(mol)
    writer.close()

def get_charge_from_smiles(smi):
    mol = MolFromSmiles(smi)
    netc = GetFormalCharge(mol)
    return netc

def check_implicit_hydrogens(mol):
    valdiff=0
    for atom in mol.GetAtoms():    
       valdiff +=  atom.GetNumImplicitHs()
    return bool(valdiff > 0)

def check_non_accepted_bond_orders(mol):
    for bond in mol.GetBonds():
        if bond.GetBondTypeAsDouble() not in [1.0,1.5,2.0,3.0]:
            return True
    return False
    

def remove_inchi_non_standard_layers(inchi,fake_standard=False):
    ver1 = re.compile(r'^1/')
    fix = re.compile(r'/f.*$')
    rec = re.compile(r'/r.*$')
    sinchi = inchiheaderre.sub('', inchi)
    if fake_standard:
        sinchi = ver1.sub('1S/', inchi)
    sinchi = fix.sub('', sinchi)
    sinchi = rec.sub('', sinchi)
    return sinchi

def convertimplicttosdf(imol,sdffile):
    if check_implicit_hydrogens(imol) or not imol.GetConformer().Is3D():
        msg = ''
        
        rdDistGeom.EmbedMolecule(imol)
        if rdForceFieldHelpers.MMFFHasAllMoleculeParams(imol):
            
            res = rdForceFieldHelpers.MMFFOptimizeMolecule(imol)
            if res < 0:
                raise Geometry3DGenerationError('Cannot generate 3D coordinates')
            elif res > 0:
                msg = 'WARNING: Optimitzation has not converged.'
        elif rdForceFieldHelpers.UFFHasAllMoleculeParams(imol):
            res = rdForceFieldHelpers.UFFOptimizeMolecule(imol)
            if res < 0:
                raise Geometry3DGenerationError('Cannot generate 3D coordinates')
            elif res > 0:
                msg = 'WARNING: Optimitzation has not converged.'

    return (imol,msg)

def remove_isotopes(mol,sanitize=True):
    edmol = EditableMol(mol)
    for atom in mol.GetAtoms():
        atom.SetIsotope(0)
        if sanitize:
            SanitizeMol(mol)

        
