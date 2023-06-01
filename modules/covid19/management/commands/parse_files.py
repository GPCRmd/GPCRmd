from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
from covid19.models import *
import mdtraj as md
from modules.dynadb.pipe4_6_0 import useline

class Command(BaseCommand):
    help = "Extracts info from the submitted structure and trajectory."
    def add_arguments(self, parser):
        parser.add_argument(
           '--dyn',
            dest='dynamics_id',
            nargs='*',
            action='store',
            default=False,
            help='Specify covid dynamics id(s).'
        )
        parser.add_argument(
            '--no_save',
            action='store_true',
            dest='no_save',
            default=False,
            help='Show molecules found but do not save them in the datavase.',
        )
    def handle(self, *args, **options):
        def obtain_framenum(filepath):
            t=md.open(filepath)
            num_frames=t.__len__()
            return num_frames
        
        def parse_pdb(filepath):
            d={'ASPH', 'HDJ', 'CLYN', 'NASP', 'CM3L', 'CTHR', 'DGLN', 'HDK', 'CCS', 'T2P', 'HEG', 'NM3L', 'CARG', 'NY1P', 'NASH', 'HISA', 'CY6', 'HDM', 'HDB', 'OLT', 'HISB', 'HDR', 'HDG', 'CYSF', 'NLYS', 'CCY8', 'CYSP', 'HES', 'CY7', 'HDT', 'HDQ', 'SRM', 'CT2P', 'GLYM', 'NS2P', 'DMET', 'HEU', 'NCYX', 'NH2E', 'CH1D', 'HEB', 'NGLN', 'CHIE', 'H1E', 'NOLT', 'HIS2', 'CMET', 'NS1P', 'CILE', 'CCY5', 'DLYS', 'NTPO', 'NARM', 'HEN', 'NCY4', 'NY2P', 'HSC', 'NLEU', 'AP1', 'GLY', 'NCCS', 'CTPO', 'DASN', 'CY2', 'HDV', 'HEL', 'HIE', 'DGLY', 'CHIN', 'HE8', 'DPHE', 'PHEU', 'NILE', 'CTRP', 'NALA', 'NOLS', 'OLP', 'CH1E', 'MLEU', 'HER', 'NGLU', 'NGLY', 'HIS1', 'HEF', 'HEQ', 'NCYM', 'CCYS', 'CGLY', 'HD6', 'CASH', 'HED', 'HE5', 'HEP', 'NSER', 'CYSG', 'HSP', 'CYSH', 'NDAB', 'CGLH', 'NCME', 'CCYX', 'HYP', 'Y1P', 'TRP', 'ASPP', 'HDX', 'HDL', 'HDP', 'CY0', 'CCME', 'Y2P', 'NLYN', 'CYS2', 'HEM', 'HEY', 'CCY2', 'NVAL', 'CH2E', 'HD1', 'HDF', 'HISD', 'LYN', 'MLYS', 'CASN', 'HDD', 'NSRM', 'CS1P', 'HEI', 'CM2L', 'CY1P', 'NTYR', 'NCY9', 'CCY9', 'HSE', 'NPRO', 'HEE', 'HD2', 'HEJ', 'CCY7', 'NCY7', 'HE9', 'HSD', 'HD0', 'NNLN', 'HID', 'HE2', 'LSN', 'CPRO', 'HDC', 'DHIS', 'COLS', 'NCY6', 'HD5', 'PRO', 'DARG', 'ACK', 'CY3', 'ASP', 'CT1P', 'HEO', 'NGLH', 'GLUP', 'NT2P', 'CKCX', 'NHIP', 'GLH', 'HEA', 'HDE', 'CYSD', 'DTYR', 'CYSL', 'NOLP', 'CY1', 'NH2D', 'HEZ', 'HIN', 'CCYM', 'CNLN', 'HISP', 'NHYP', 'ARG', 'KCX', 'CTYR', 'CDRM', 'S1P', 'NHIE', 'TRPU', 'DTRP', 'GLN', 'HEC', 'NCY5', 'CSER', 'HD7', 'SEP', 'DAB', 'HET', 'CCY0', 'HS2', 'NHIN', 'TPO', 'ALY', 'HD9', 'HD4', 'H2E', 'ILE', 'COLP', 'NT1P', 'HDW', 'ASN1', 'SERD', 'VAL', 'NPHE', 'NLE', 'CMLY', 'HDO', 'HDH', 'NTRP', 'HDZ', 'NCY3', 'MEL', 'GLU', 'HIP', 'CSRM', 'DVAL', 'HE3', 'CPTR', 'DRM', 'CHIP', 'CPHE', 'LYS', 'HD3', 'HDY', 'DHSP', 'NCYS', 'H2D', 'HDN', 'CY8', 'CY5', 'COLT', 'NCY8', 'CYM', 'THR', 'DHSE', 'CHID', 'NCY1', 'DPRO', 'NHIS', 'CASP', 'HIS', 'MEV', 'CME', 'ZAFF', 'CYS', 'CLYS', 'ARGN', 'CYX', 'NSEP', 'MGY', 'CHYP', 'NCY2', 'DILE', 'HE6', 'DSER', 'NKCX', 'CCY4', 'OLS', 'HE0', 'CHIS', 'LEU', 'NTHR', 'MEVA', 'CGLU', 'PHE', 'GLUH', 'CVAL', 'M2L', 'NDRM', 'ALA', 'CH2D', 'HEW', 'NHID', 'DALA', 'NASN', 'NLN', 'ASH', 'NCY0', 'CY2P', 'HDA', 'PTR', 'TYR', 'MET', 'HDU', 'HISE', 'HDS', 'NACK', 'CARM', 'CSEP', 'DHSD', 'CCY6', 'S2P', 'SER', 'CLEU', 'T1P', 'M3L', 'DASP', 'CCY3', 'DLEU', 'CACK', 'CY4', 'MLY', 'NH1E', 'CGU', 'ASP1', 'DTHR', 'NM2L', 'ASN', 'HE1', 'MELE', 'CCY1', 'HEH', 'H1D', 'NPTR', 'NARG', 'NMET', 'HDI', 'HEK', 'ARM', 'CCCS', 'CS2P', 'NH1D', 'DGLU', 'HISH', 'HEX', 'HEV', 'CGUP', 'HE7', 'CDAB', 'MVAL', 'NMLY', 'CY9', 'DCYS', 'CGLN', 'CALA', 'LYSH', 'HE4', 'HD8', 'CYZ'}

            fpdb=open(filepath,'r')
            nonprot={}
            prot_chains=set()
            has_chainid=True
            for line in fpdb:
                if useline(line):
                    chain=line[21]
                    if chain==" ":
                        has_chainid=False
                    resnum=line[22:26].strip()
                    resname=line[17:21].strip()
                    if resname in d:
                        prot_chains.add(chain)
                    else:
                        if not resname in nonprot:
                            nonprot[resname]={}
                            nonprot[resname]["chainid"]=chain
                            nonprot[resname]["count"]=0
                        nonprot[resname]["count"]+=1
            nonprot_refined={}
            if has_chainid:
                for resname,resinfo in  nonprot.items():
                    if not resinfo["chainid"] in prot_chains:
                        nonprot_refined[resname]=resinfo["count"]
                return nonprot_refined
            else:
                return nonprot


        save_data=not options["no_save"]
        print("Save: %s" % save_data)
        dynobj=CovidDynamics.objects.filter(is_published=True)
        if options['dynamics_id']:
            dynobj=dynobj.filter(id__in=options['dynamics_id'])
        if dynobj == []:
            self.stdout.write(self.style.NOTICE("No dynamics found with specified conditions."))
        for dyn in dynobj:
            dyn_id=dyn.id
            print("\nDyn %s" % dyn_id)

            mycomponents=CovidDynamicsComponents.objects.filter(id_dynamics=dyn_id)
            mycomp_d={e.resname:e.numberofmol for e in mycomponents}
            extracomp=mycomponents.filter(id_dynamics=dyn_id,is_ligand=False,is_membrane=False)
            #obtain_compounds=False
            #if not extracomp.count():
            obtain_compounds=True

            myfiles=CovidFilesDynamics.objects.prefetch_related("id_files__id_file_types").filter(id_dynamics=dyn_id)
            struc_f=None
            traj_files=[]
            for f in myfiles:
                fileobj=f.id_files
                filetype=fileobj.id_file_types
                if filetype.is_trajectory:
                    framenum=f.framenum
                    if not framenum:
                        filepath=fileobj.filepath
                        traj_framenum=obtain_framenum(filepath)
                        f.framenum=traj_framenum
                        f.save()
                elif filetype.is_coordinates:
                    if obtain_compounds:
                        filepath=fileobj.filepath
                        nonprot=parse_pdb(filepath)
                        if nonprot:
                            print("Compounds found:",nonprot)
                            for resname,resdata in nonprot.items():
                                if resname in mycomp_d:
                                    if not mycomp_d[resname]:
                                        #Residue saved but unknown number of molecules
                                        print("%s - Add #mol" % resname)
                                        if save_data:
                                            thiscomp=mycomponents.get(resname=resname)
                                            thiscomp.numberofmol=resdata["count"]
                                            thiscomp.save()

                                else:
                                    #residue not saved
                                    print("%s - Save" % resname)
                                    if save_data:
                                        cdc=CovidDynamicsComponents(
                                            id_dynamics=dyn,
                                            resname=resname,
                                            molecule_name=resname,
                                            numberofmol=resdata["count"]
                                            )
                                        cdc.save()
                        else:
                            self.stdout.write(self.style.NOTICE("No non-protein molecules found"))