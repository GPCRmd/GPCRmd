from django.contrib import admin

# Register your models here.
from modules.news.models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "doi", "authors", "title", "url")