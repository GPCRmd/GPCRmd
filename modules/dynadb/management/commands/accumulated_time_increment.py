from modules.dynadb.models import DyndbDynamics, DyndbFilesDynamics
from django.core.management.base import BaseCommand, CommandError
import pandas as pd
from django.conf import settings

class Command(BaseCommand):
	help = "Obtains accumulated simulated over time and saves info in file MEDIA_ROOT accumtime_by_month.json"
		
	def handle(self, *args, **options):

		totaltime = 0
		time_by_date = {}
		# Calculate accumulated time and classify it by month of submission
		for dd in DyndbDynamics.objects.filter(is_published=True):
			delta = dd.delta
			subm_date_obj=dd.creation_timestamp
			subm_date=subm_date_obj.strftime("%b %Y")
			time_by_date.setdefault(subm_date,0)
			for dfd in DyndbFilesDynamics.objects.filter(id_dynamics=dd.id, type=2):
				frames = dfd.framenum
				timesim = frames*delta
				totaltime += timesim
				time_by_date[subm_date] += float(format(timesim, '.1f'))

		# Put accumulated time per month info in pandas dataframe and sort by date
		st=pd.DataFrame.from_dict(time_by_date,orient="index")
		st.index=pd.to_datetime(st.index).to_period('m')
		st = st.reindex(pd.period_range(st.index.min(), st.index.max(), freq='m'), fill_value=0)
		st.index= [st.strftime("%b %Y") for st in st.index]

		# Save this in a json for future uses
		outfile = settings.MEDIA_ROOT + 'accumtime_by_month.json'
		st.to_json(outfile)