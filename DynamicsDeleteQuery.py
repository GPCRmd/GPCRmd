#QUERY PARA CONOCER las dinamicas involucradas. la de id=1 la mantendremos
#Si queremos borrar otras submissio 1 
from dynadb.models import DyndbSubmissionMolecule, DyndbModeledResidues, DyndbModelComponents, DyndbModel, DyndbSubmissionMolecule, DyndbSubmissionProtein, DyndbMolecule, DyndbComplexMolecule, DyndbComplexMoleculeMolecule, DyndbComplexMolecule, DyndbComplexProtein, DyndbSubmissionProtein, DyndbMolecule, DyndbSubmissionMolecule, DyndbModel, DyndbComplexCompound, DyndbSubmissionMolecule, DyndbProtein, DyndbUniprotSpecies, DyndbOtherProteinNames, DyndbProteinSequence, DyndbProteinCannonicalProtein, DyndbProteinMutations, DyndbCompound, DyndbOtherCompoundNames, DyndbDynamics, DyndbDynamicsMembraneTypes, DyndbDynamicsSolventTypes, DyndbDynamicsTags, DyndbDynamicsComponents, DyndbDynamicsMethods, DyndbDynamicsTagsList, DyndbAssayTypes, DyndbSubmissionModel, DyndbCompound, DyndbFileTypes, DyndbFiles, DyndbFilesMolecule, DyndbSubmissionModel, DyndbSubmissionProtein, DyndbSubmissionDynamicsFiles, DyndbFilesDynamics


def DynamicsDeleteQuery(submission_id=1):

    q=DyndbDynamics.objects.filter(submission_id=submission_id).exclude(id__in=[1,2,3])
    qdF=list(DyndbFiles.objects.filter(dyndbfilesdynamics__id_dynamics__in=q.values('id')).values_list('id',flat=True))
    DyndbFilesDynamics.objects.filter(id_dynamics__in=q.values('id')).delete()
    DyndbDynamicsComponents.objects.filter(id_dynamics__in=q.values('id')).delete()
    DyndbFiles.objects.filter(id__in=qdF).delete()
    q.delete()
    print("deleted")
