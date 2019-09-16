'''
This file defines indexes for haystack search indexer manager.
If the definition of any of these indexes is modified,
the solr schema.xml file must be regenerated,
sorl engine must be restarted and the indexes rebuilt.
Also, the HTTP server must be restarted. 

To generate the schema.xml file run:

    python manage.py build_solr_schema > solr/collection_gpcrmd/conf/schema.xml   

To rebuilt the indexes run:

    python manage.py rebuild_index
    
'''



import datetime
from haystack import indexes
from dynadb.models import DyndbProtein,DyndbMolecule,DyndbComplexProtein,DyndbCompound,DyndbOtherProteinNames,DyndbComplexCompound,DyndbComplexMoleculeMolecule, DyndbOtherCompoundNames,DyndbOtherProteinNames
from django.utils import timezone



class MoleculeIndex(indexes.SearchIndex, indexes.Indexable): 
    text = indexes.CharField(document=True, use_template=True)
    inchikey=indexes.CharField(model_attr='inchikey')
    inchi=indexes.CharField(model_attr='inchi')
    name=indexes.CharField(model_attr='id_compound__name')

    def get_model(self):
        return DyndbMolecule

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.select_related('id_compound').all()


class ProteinIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    mainnames = indexes.EdgeNgramField(model_attr='name')
    id_protein = indexes.IntegerField(model_attr='id')
    uniprotkbac = indexes.CharField(model_attr='uniprotkbac')
    uniprot_species_scientific_name = indexes.CharField(model_attr='id_uniprot_species__scientific_name')

    def get_model(self):
        return DyndbProtein

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.select_related('id_uniprot_species').all()


class OtherProteinNamesIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    other_names = indexes.EdgeNgramField(model_attr='other_names')
    id_protein=indexes.IntegerField(model_attr='id_protein_id')

    def get_model(self):
        return DyndbOtherProteinNames

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

class CompoundIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    id_compound = indexes.IntegerField(model_attr='id')
    name = indexes.CharField(model_attr='name')
    iupac_name = indexes.CharField(model_attr='iupac_name',null=True)
    mainnames = indexes.EdgeNgramField(model_attr='name')
    pubchem_cid = indexes.IntegerField(model_attr='pubchem_cid',null=True)
    chemblid = indexes.IntegerField(model_attr='chemblid',null=True)
    sinchi = indexes.CharField(model_attr='sinchi')
    sinchikey = indexes.CharField(model_attr='sinchikey')
    std_id_molecule = indexes.IntegerField(null=True)

    # Workarround for nullable FKs
    def prepare_std_id_molecule(self,obj):
        if obj.std_id_molecule is not None:
            return obj.std_id_molecule.id
        return None

    def get_model(self):
        return DyndbCompound

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()


class OtherCompoundNamesIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    other_names = indexes.EdgeNgramField(model_attr='other_names')
    id_compound=indexes.IntegerField(model_attr='id_compound__id')

    def get_model(self):
        return DyndbOtherCompoundNames

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

