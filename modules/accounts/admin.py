from django.contrib import admin
from modules.accounts.models import User

# admin.site.register(User)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "last_name", "first_name", "email")

