import datetime
from haystack import indexes
from dynadb.models import DyndbProtein,DyndbMolecule,DyndbComplexProtein,DyndbCompound,DyndbOtherProteinNames,DyndbComplexCompound,DyndbComplexMoleculeMolecule, DyndbOtherCompoundNames,DyndbOtherProteinNames
from django.utils import timezone

class MoleculeIndex(indexes.SearchIndex, indexes.Indexable): 
    text = indexes.CharField(document=True, use_template=True)
    inchikey=indexes.CharField(model_attr='inchikey')
    name=indexes.CharField()

    def prepare_name (self,obj):
        return obj.id_compound.name

    def get_model(self):
        return DyndbMolecule

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()


class OtherProteinNamesIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    id_protein=indexes.IntegerField() #INTEGER OR CHAR?
    name=indexes.CharField()
    def prepare_id_protein (self,obj):
        return obj.id_protein.id

    def prepare_name (self,obj):
        return obj.id_protein.name

    def get_model(self):
        return DyndbOtherProteinNames

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

class OtherCompoundNamesIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    id_compound=indexes.IntegerField() #INTEGER OR CHAR?
    name=indexes.CharField()
    iupac_name=indexes.CharField()

    def prepare_name (self,obj):
        return obj.id_compound.name

    def prepare_iupac_name (self,obj):
        return obj.id_compound.iupac_name


    def prepare_id_compound (self,obj):
        return obj.id_compound.id

    def get_model(self):
        return DyndbOtherCompoundNames

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

