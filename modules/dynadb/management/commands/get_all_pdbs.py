from modules.dynadb.models import DyndbSubmission, DyndbModel
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
	help = "Get all PDBids in GPCRmd"
		
	def handle(self, *args, **options):
		pdbs = set()
		for a in DyndbSubmission.objects.filter(is_published=True):
			DM = DyndbModel.objects.filter(dyndbsubmissionmodel__submission_id=a.id)
			for dm in DM:
				pdbs.add(dm.pdbid)

		print(pdbs)