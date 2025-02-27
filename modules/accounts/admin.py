from django.contrib import admin
from django.utils.html import format_html

from modules.accounts.models import User

# admin.site.register(User)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "last_name", "first_name", "email", "is_active", "is_admin")
    def is_active(self,obj):
        try:
            is_active = User.objects.filter(id=obj.id).values_list("is_active", flat = True)[0]
            if is_active:
                return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
            else:
                return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')
        except:
            return ""
        
    def is_admin(self,obj):
        try:
            is_admin = User.objects.filter(id=obj.id).values_list("is_admin", flat = True)[0]
            if is_admin:
                return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
            else:
                return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')
        except:
            return ""

