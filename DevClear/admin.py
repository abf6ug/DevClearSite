from django.contrib import admin
from DevClear.models import Organization, Project, Image

class OrganizationImageInline(admin.TabularInline):
    model = Image
    extra = 3

class OrganizationImageAdmin(admin.ModelAdmin):
    inlines = [ OrganizationImageInline, ]

admin.site.register(Organization)
admin.site.register(Project)


