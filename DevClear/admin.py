from django.contrib import admin
from DevClear.models import Organization, Project, OrganizationImage

class OrganizationImageInline(admin.TabularInline):
    model = OrganizationImage
    extra = 3

class OrganizationImageAdmin(admin.ModelAdmin):
    inlines = [ OrganizationImageInline, ]

admin.site.register(Organization)
admin.site.register(Project)
admin.site.register(OrganizationImage)


