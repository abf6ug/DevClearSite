from django.contrib import admin
from DevClear.models import *

class OrganizationImageInline(admin.TabularInline):
    model = Image
    extra = 3

class OrganizationImageAdmin(admin.ModelAdmin):
    inlines = [ OrganizationImageInline, ]

admin.site.register(Organization)
admin.site.register(Project)
admin.site.register(Community)

admin.site.register(Post)
admin.site.register(Image)
admin.site.register(Message)
admin.site.register(Conversation)

admin.site.register(DevUser)


