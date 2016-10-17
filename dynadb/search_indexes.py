import datetime
from haystack import indexes
from dynadb.models import DyndbProtein
from django.utils import timezone

class ProteinIndex(indexes.SearchIndex, indexes.Indexable): #shouldn't the name be DyndbProteinIndex?
    text = indexes.CharField(document=True, use_template=True)
    code = indexes.CharField(model_attr='uniprotkbac')
    name = indexes.CharField(model_attr='name')
    species=indexes.CharField(model_attr='id_uniprot_species')
    pub_date=indexes.DateTimeField(model_attr='creation_timestamp')
    def get_model(self):
        return DyndbProtein

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all() #return self.get_model().objects.filter(creation_timestamp__lte=timezone.now())


