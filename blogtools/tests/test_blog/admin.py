from django.contrib import admin
from feincms.admin.item_editor import FEINCMS_CONTENT_FIELDSET
from feincmstools.admin import ChunkyContentAdmin
from blogtools.admin import CategoryEntryModelAdmin, CategoryModelAdmin
from .models import Entry, Category

class EntryAdmin(CategoryEntryModelAdmin, ChunkyContentAdmin):
    list_filter = list(CategoryEntryModelAdmin.list_filter) + ['category']
    fieldsets = tuple(list(CategoryEntryModelAdmin.fieldsets) + [
        ('Appearance in listings', {
            'fields': ('summary',),
        }),
        FEINCMS_CONTENT_FIELDSET,
    ])

admin.site.register(Category, CategoryModelAdmin)
admin.site.register(Entry, EntryAdmin)