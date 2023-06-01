from modules.dynadb.models import DyndbDynamics, DyndbFilesDynamics
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
	help = "Obtains accumulated simulated time in the whole database"
		
	def handle(self, *args, **options):

		totaltime = 0
		for dd in DyndbDynamics.objects.filter(is_published=True):
			delta = dd.delta
			for dfd in DyndbFilesDynamics.objects.filter(id_dynamics=dd.id, type=2):
				frames = dfd.framenum
				timesim = frames*delta
				totaltime += timesim

		print("Accumulated simulated time in GPCRmd: %s microseconds" % "{:.3f}".format(totaltime/1000))