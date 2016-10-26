import os
import re
import io
import sys
from .customized_errors import ParsingError,MultipleMoleculesinSDF,InvalidMoleculeFileExtension
from django.conf import settings
from subprocess import Popen, PIPE
from rdkit import Chem
from rdkit.Chem import rdinchi 
from rdkit import rdBase
from rdkit.Chem import Draw
from rdkit.Chem.Draw.MolDrawing import DrawingOptions
from rdkit.Chem import rdForceFieldHelpers
from rdkit.Chem import rdDistGeom
from rdkit.Chem import Draw
from rdkit.Chem.Draw.MolDrawing import DrawingOptions
from contextlib import contextmanager
from rdkit import RDLogger 


class Geometry3DGenerationError(Exception):
    def __init__(*args,**kwargs):
        msg = 'Cannot generate 3D coordinates'
        super(Geometry3DGenerationError,self).__init__(msg,*args,**kwargs)


MOLECULE_EXTENSION_TYPES = {'sdf':'sdf','sd':'sdf','mol':'mol'}

inchiheaderre = re.compile(r'InChI=')

rdBase.EnableLog('rdApp.debbug')
rdBase.EnableLog('rdApp.info')
rdBase.EnableLog('rdApp.warning')
rdBase.EnableLog('rdApp.error')
rdBase.EnableLog('rdApp.critical')





def fileno(file_or_fd):
    fd = getattr(file_or_fd, 'fileno', lambda: file_or_fd)()
    if not isinstance(fd, int):
        raise ValueError("Expected a file (`.fileno()`) or a file descriptor")
    return fd


@contextmanager
def stdout_redirected(to=os.devnull, stdout=None):
    if stdout is None:
       stdout = sys.stdout

    stdout_fd = fileno(stdout)
    # copy stdout_fd before it is overwritten
    #NOTE: `copied` is inheritable on Windows when duplicating a standard stream
    with os.fdopen(os.dup(stdout_fd), 'wb') as copied: 
        stdout.flush()  # flush library buffers that dup2 knows nothing about
        try:
            os.dup2(fileno(to), stdout_fd)  # $ exec >&to
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




def open_molecule_file(uploadedfile,logfile):
    
    #charset = 'utf-8'
    #if "charset" in uploadedfile and uploadedfile.charset is not None:
            #charset = uploadedfile.charset
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
        
    uploadedfile.seek(0)
    membuffer = io.StringIO()
    with stdout_redirected(to=logfile,stdout=sys.stderr):
        with stdout_redirected(to=logfile,stdout=sys.stdout):
            print('Loading molecule...')
            if filetype == 'sdf' or filetype == 'mol':
                suppl = Chem.ForwardSDMolSupplier(uploadedfile,removeHs=False)
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
            Chem.AssignAtomChiralTagsFromStructure(mol,replaceExistingTags=False)
            print('Finished loading molecule.')

    return mol
def generate_inchi(mol, FixedH=False, RecMet=False):
    logger = RDLogger.logger()
    options = "-DoNotAddH"
    if FixedH:
        options += " -FixedH"
    if RecMet:
        options += " -RecMet"
    inchi,code,msg,log,aux = rdinchi.MolToInchi(mol,options=options)
    
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

def generate_smiles(mol,logfile):
    with stdout_redirected(to=logfile,stdout=sys.stderr):
        with stdout_redirected(to=logfile,stdout=sys.stdout):
            smi = Chem.MolToSmiles(mol,isomericSmiles=True,canonical=False)
    smi,smierr = cannonicalize_smiles_openbabel(smi)
    print(smierr,file=logfile)
    return smi
                                          
def generate_inchikey(inchi):
    return Chem.InchiToInchiKey(inchi)

def get_net_charge(mol):
    return Chem.GetFormalCharge(mol)
    
    
def get_charge_from_inchi(inchi,removeHs=False):
    mol = Chem.MolFromInchi(inchi)
    netc = Chem.GetFormalCharge(mol)
    return netc

def generate_png(mol,pngpath,logfile,size=300):
    with stdout_redirected(to=sys.stdout,stdout=sys.stderr):
        with stdout_redirected(to=logfile,stdout=sys.stdout):
            nhmol = Chem.RemoveHs(mol,implicitOnly=False, updateExplicitCount=True, sanitize=True)
            op = DrawingOptions()
            op.atomLabelFontSize = size/25
            Draw.MolToFile(Draw.PrepareMolForDrawing(nhmol,forceCoords=True,addChiralHs=True),\
                pngpath,fitImage=True,size=(size, size),options=op)


def write_sdf(mol,path):
    writer = Chem.SDWriter(path)
    writer.write(mol)
    writer.close()

def get_charge_from_smiles(smi):
    mol = Chem.MolFromSmiles(smi)
    netc = Chem.GetFormalCharge(mol)
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
    

def standarize_inchi(inchi):
    ver1 = re.compile(r'^1/')
    fix = re.compile(r'/f.*$')
    rec = re.compile(r'/r.*$')
    sinchi = inchiheaderre.sub('', inchi)
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

    





#ext = ext.lower()
#ext = ext.strip('.')
#sinchierr=None
#inchierr=None
#smierr=None
#pngerr=None
#netcerr=None
#wspc = re.compile(r'\s+')

    #Chem.AssignAtomChiralTagsFromStructure(mol,replaceExistingTags=False)
    #print('Implicit hydrogens:')
    #print(check_implicit_hydrogens(mol))
    
    #nhmol = Chem.RemoveHs(mol,implicitOnly=False, updateExplicitCount=True, sanitize=True)
    
    #print('Standard InChI generation:')
    #sinchi,code,msg,log,aux = rdinchi.MolToInchi(mol,options='-DoNotAddH')
    #if code == 0:
        #print(sinchi)
    #if code == 1:
        #print(sinchi)
        #print(msg)
    #else:
        #print(msg)
    #print('InChI generation:')
    #inchi,code,msg,log,aux = rdinchi.MolToInchi(mol,options='-FixedH -DoNotAddH')
    #if code == 0:
        #print(inchi)
    #if code == 1:
        #print(inchi)
        #print(msg)
    #else:
        #print(msg)
    
    #print('SMILES generation:')
    #smi = Chem.MolToSmiles(mol,isomericSmiles=True,canonical=False)
    #print(smi)
    #smi2,smierr= cannonicalize_smiles_openbabel(smi,obabelcmd)
    #print(smi2)
    
    #print('PNG generation:')
    #size = 300
    #op = DrawingOptions()
    #op.atomLabelFontSize = size/25
    #Draw.MolToFile(Draw.PrepareMolForDrawing(nhmol,forceCoords=True,addChiralHs=True), os.path.join(pngpath,"CLZ.png"),fitImage=True,size=(size, size),options=op)
    #print('Net charge:')
    #netc=Chem.GetFormalCharge(mol)
    #print(netc)
    #sinchikey = Chem.InchiToInchiKey(sinchi)
    #print("Standard keyed InChI:")
    #print(sinchikey)
    #inchikey = Chem.InchiToInchiKey(inchi)
    #print("Keyed InChI:")
    #print(inchikey)
    #sinchi2 = standarize_inchi(inchi)
    #print('InChI standaritzation:')
    #print(sinchi2)
    #print("Net charge from InChI")
    #netc = get_charge_from_inchi(inchi)
    #print(netc)
    #print("Net charge from smiles")
    #netc = get_charge_from_smiles(smi)
    #print(netc)
    
    #suppl = Chem.SDMolSupplier('../test/ferrocene.sdf',removeHs=False)
    #imol = next(suppl)
    #convertimplicttosdf(imol,'../test/ferrocene3.sdf')

    
    
        