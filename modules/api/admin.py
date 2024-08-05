from django.contrib import admin
from django.utils.html import format_html

# Register your models here.
from modules.api.models import AllDownloads
from modules.accounts.models import User as Users

@admin.register(AllDownloads)
class AllDownloadsAdmin(admin.ModelAdmin):
    list_display = ("id", "tmpname", "dyn_ids", "username")
    def username(self, obj):
        result = AllDownloads.objects.filter(id=obj.id).values_list("created_by", flat = True)
        usrid = result[0]
        usrn = Users.objects.filter(id=usrid).values_list("username", flat=True)[0]
        return format_html('<p>{} ({}) </p>', usrn, usrid)