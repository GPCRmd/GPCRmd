import datetime
from haystack import indexes
from dynadb.models import DyndbProtein,DyndbMolecule,DyndbCompound,DyndbOtherProteinNames
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

class MoleculeIndex(indexes.SearchIndex, indexes.Indexable): #shouldn't the name be DyndbProteinIndex?
    text = indexes.CharField(document=True, use_template=True)
    inchi = indexes.CharField(model_attr='inchi')
    inchikey = indexes.CharField(model_attr='inchikey')
    smiles=indexes.CharField(model_attr='smiles')
    def get_model(self):
        return DyndbMolecule

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

class CompoundIndex(indexes.SearchIndex, indexes.Indexable): #shouldn't the name be DyndbProteinIndex?
    text = indexes.CharField(document=True, use_template=True)
    sinchi = indexes.CharField(model_attr='sinchi')
    sinchikey = indexes.CharField(model_attr='sinchikey')
    #chembleid=indexes.CharField(model_attr='chembleid')
    pubchem=indexes.CharField(model_attr='pubchem_cid')
    name=indexes.CharField(model_attr='name')
    iupacname=indexes.CharField(model_attr='iupac_name')
    def get_model(self):
        return DyndbCompound

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()


