from django.contrib import admin

class CategoryModelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

class EntryModelAdmin(admin.ModelAdmin):
    date_hierarchy = 'byline_date'
    list_filter = ('is_active', 'author')
    list_display = ('title', 'byline_date', 'author', 'publication_date', 'publication_end_date', 'is_active', 'is_public')
    prepopulated_fields = {'slug': ('title',)}
    save_on_top = True
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'byline_date',),
            }),
        ('Publication', {
            'fields': (
                'is_active',
                'author',
                'publication_date',
                'publication_end_date',
            ),
        }),
    )

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        # Set the currently logged-in user as the author.
        if db_field.name == "author":
            kwargs["initial"] = request.user
        return super(EntryModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class CategoryEntryModelAdmin(EntryModelAdmin):
    list_display = ('title', 'byline_date', 'author', 'publication_date', 'publication_end_date', 'is_active', 'is_public')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'byline_date',),
            }),
        ('Publication', {
            'fields': (
                'category',
                'is_active',
                'author',
                'publication_date',
                'publication_end_date',
            ),
        }),
    )