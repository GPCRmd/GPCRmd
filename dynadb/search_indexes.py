import datetime
from haystack import indexes
from dynadb.models import DyndbProtein,DyndbMolecule,DyndbComplexProtein,DyndbCompound,DyndbOtherProteinNames,DyndbComplexCompound,DyndbComplexMoleculeMolecule
from django.utils import timezone


class ComplexProteinIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    is_receptor=indexes.BooleanField(model_attr='is_receptor')
    content_auto = indexes.EdgeNgramField(use_template=True)
    def get_model(self):
        return DyndbComplexProtein

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

class ComplexMoleculeMoleculeIndex(indexes.SearchIndex, indexes.Indexable): 
    text = indexes.CharField(document=True, use_template=True)
    content_auto = indexes.EdgeNgramField(use_template=True)
    def get_model(self):
        return DyndbComplexMoleculeMolecule

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

class ComplexCompoundIndex(indexes.SearchIndex, indexes.Indexable): 
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return DyndbComplexCompound

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()


