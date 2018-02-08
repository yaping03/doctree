from django.contrib import admin

# Register your models here.

from doctree.models import Book, Chapter, Knowledge

admin.site.register(Book)
admin.site.register(Chapter)
admin.site.register(Knowledge)
