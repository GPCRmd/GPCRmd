from django.db.models import Count
from modules.dynadb.models import *
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Creates precomputed datafiles of ligand-residue interactons in the GPCRs stored at the database for posterior creation of comparaive plots. Only considers published data."
    def add_arguments(self, parser):
        parser.add_argument(
            '--dynid',
            action='store',
            nargs='*',            
            type = int,
            dest='dyn_id_li',
            default=False,
            help='List of dynamic ids to fix',
        )

    def handle(self, *args, **options):

        if options['dyn_id_li']:
            dyn_id_li = options['dyn_id_li']
        else:
            raise CommandError("Neither dynid(s) nor --all options have been specified. Use --help for more details.")

        for dyn_id in dyn_id_li:
            # we need to relate our model to the complex molecule
            # to find the right DyndbComplexMolecule we use DyndbComplexExp
            d=DyndbDynamics.objects.get(id=dyn_id)
            model=d.id_model
            if model.id_complex_molecule:
                print("Dyn %s has a correct assignation already" % dyn_id)
                continue
            #proteins in this simulations
            prot_in_sim={sp.protein_id for sp in d.submission_id.dyndbsubmissionprotein_set.all()}
            # find the DyndbComplexExp (CE) that has exactly the proteins in this submission
            ce_li = DyndbComplexExp.objects.annotate(count=Count('proteins')).filter(count=len(prot_in_sim))
            for prot in prot_in_sim:
                ce_li = ce_li.filter(proteins=prot)
            if len(ce_li)>1:
                raise Error("More than 1 CE found")
            ce=ce_li[0]
            #from the CE, obtain the complex molecule (CM)
            cm_l=ce.dyndbcomplexmolecule_set.all()
            if len(cm_l)>1:
                raise Error("More than 1 CM found")
            cm=cm_l[0]
            # assign to dyn
            model=d.id_model
            model.id_complex_molecule=cm
            model.save()