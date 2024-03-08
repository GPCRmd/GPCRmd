from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html

from django.contrib import admin
from .models import *
from modules.accounts.models import User as Users

# Register your models here.
from django.contrib.auth.models import Group, User
admin.site.unregister(Group)
@admin.register(DyndbDynamics)
class DyndbDynamicsAdmin(admin.ModelAdmin):
    list_display = ("id", "id_model_link", "submission_id_link", "username")

    def id_model_link(self, obj):
        url = (
            reverse("admin:dynadb_dyndbmodel_changelist")
            + f"{obj.id_model.id}/change"
        )
        return format_html('<a href="{}">Model Id {} </a>', url, obj.id_model.id)

    def submission_id_link(self, obj):
        url = (
            reverse("admin:dynadb_dyndbsubmission_changelist")
            + f"{obj.submission_id.id}/change"
        )
        return format_html('<a href="{}">Submission Id {} </a>', url, obj.submission_id.id)

    def username(self, obj):
        result = DyndbDynamics.objects.filter(id=obj.id).values_list("created_by", flat = True)
        usrid = result[0]
        usrn = Users.objects.filter(id=usrid).values_list("username", flat=True)[0]
        return format_html('<p>{} ({}) </p>', usrn, usrid)

@admin.register(DyndbProtein)
class DyndbProteinAdmin(admin.ModelAdmin):
    list_display = ("id", "uniprotkbac", "name", "isoform", "receptor_id_protein_link", "id_uniprot_species_link", "is_mutated")

    def receptor_id_protein_link(self, obj):
        url = (
            reverse("admin:protein_protein_changelist")
            + f"{obj.receptor_id_protein}/change"
        )
        return format_html('<a href="{}">Protein Id {} </a>', url, obj.receptor_id_protein)
    
    def id_uniprot_species_link(self, obj):
        url = (
            reverse("admin:dynadb_dyndbuniprotspecies_changelist")
            + f"{obj.id_uniprot_species}/change"
        )
        return format_html('<a href="{}">Specie Id {} </a>', url, obj.id_uniprot_species)
    
admin.site.register(DyndbModel) 
@admin.action(description="Close selected submissions")
def close_submission(modeladmin, request, queryset):
    queryset.update(is_closed=True)
    
@admin.action(description="Open selected submissions")
def open_submission(modeladmin, request, queryset):
    queryset.update(is_closed=False)

@admin.action(description="Ready for precomputing selected submissions")
def ready_submission(modeladmin, request, queryset):
    query = DyndbDynamics.objects.filter(submission_id=queryset.values_list('id', flat=True)[0])
    query.update(is_published = True)

@admin.action(description="Unready for precomputing selected submissions")
def unready_submission(modeladmin, request, queryset):
    query = DyndbDynamics.objects.filter(submission_id=queryset.values_list('id', flat=True)[0])
    query.update(is_published = False)

@admin.action(description="Publish selected submissions")
def published_submission(modeladmin, request, queryset):
    queryset.update(is_published=True)

@admin.action(description="Unpublish selected submissions")
def unpublished_submission(modeladmin, request, queryset):
    queryset.update(is_published=False)
@admin.register(DyndbSubmission)
class DyndbSubmissionAdmin(admin.ModelAdmin):
    
    search_fields = ["=id"]
    list_display = ("id", "is_closed", "is_published", "is_published_dyn", "id_model_link", "username")
    list_filter = ["is_closed", "is_published"]
    actions = [close_submission, open_submission, published_submission, unpublished_submission]

    def id_model_link(self, obj):
        try:
            id_model = DyndbDynamics.objects.filter(submission_id=obj.id).values_list("id_model", flat = True)[0]
            url = (
                reverse("admin:dynadb_dyndbmodel_changelist")
                + f"{id_model}/change"
            )
            return format_html('<a href="{}">Model Id {} </a>', url, id_model)
        except:
            return ""

    def is_published_dyn(self,obj):
        try:
            is_published_dyn = DyndbDynamics.objects.filter(submission_id=obj.id).values_list("is_published", flat = True)[0]
            if is_published_dyn:
                return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
            else:
                return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')

        except:
            return ""
        
    def username(self, obj):
        usrid = Users.objects.filter(username=obj.user_id).values_list("id", flat=True)[0]
        return format_html('<p>{} ({}) </p>', usrid, obj.user_id)

admin.site.register(DyndbCannonicalProteins)
admin.site.register(DyndbModeledResidues)
admin.site.register(DyndbProteinSequence)
admin.site.register(DyndbProteinMutations)
admin.site.register(DyndbComplexExp)
admin.site.register(DyndbFiles)
admin.site.register(DyndbReferences)
admin.site.register(DyndbComplexMolecule)
admin.site.register(DyndbMolecule)
admin.site.register(DyndbUniprotSpecies) 
admin.site.register(DyndbSubmissionDynamicsFiles)
admin.site.register(DyndbCompound)
admin.site.register(DyndbFilesMolecule)
