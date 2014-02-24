from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from object_permissions import register

#add email, hq location, region, area of development, images, org landline/main phone
class Organization(models.Model):
    name = models.CharField(max_length=50, unique=True)

    members = models.ManyToManyField(User)
    projects = models.ManyToManyField('Project', blank=True)

    tagline = models.CharField(max_length=100, blank=True)

    start_date = models.DateField()

    short_description = models.TextField(max_length=300)
    description = models.TextField(max_length=2000)

    website = models.URLField(blank=True)


    def __unicode__(self):
        return self.name

    class Meta:
        ordering =('name',)


    @classmethod
    def create(cls, name, short_description, tagline, start_date, description, website):
        org = cls(name=name, short_description=short_description,
                   tagline=tagline, start_date=start_date, description=description, website=website)
        return org

register(['view', 'edit', 'remove', 'add_project', 'add_member'], Organization, app_label='DevClear')

#add email, location, communities, region, images
class Project(models.Model):
    name = models.CharField(max_length=50, unique=True)
    #    #ID?

    members = models.ManyToManyField(User)
    sponsor_org = models.ForeignKey(Organization)
    #admins = models.ForeignKey(User, related_name='admins')#need constraint to ensure in org and members
    #possibly make many to many, look at permissions

    scale = models.CharField(max_length=20)

    STATUS_CHOICES=(('NS', 'Not Started'), ('I', 'In Progress'), ('NC','Near Completion'), ('C', 'Completed'))
    status = models.CharField(max_length=2,
                                      choices=STATUS_CHOICES,
                                      default='N')
    tagline = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date= models.DateField()

    description = models.TextField(max_length=2000)
    short_description = models.TextField(max_length=300)

    website = models.URLField()

    @classmethod
    def create(cls, name, sponsor_org, short_description, tagline, start_date, end_date,
               description, website, scale, status):
        org = cls(name=name, sponsor_org=sponsor_org, short_description=short_description,
                   tagline=tagline, start_date=start_date, end_date=end_date, description=description,
                   website=website, scale=scale, status=status)
        return org



    def __unicode__(self):
        return self.name

    class Meta:
        ordering =('name',)

register(['view', 'edit', 'remove', 'add_member'], Project, app_label='DevClear')

#class Post(models.Model):


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'sponsor_org','tagline','website', 'status', 'scale',
                  'start_date', 'end_date', 'short_description', 'description']

class ProjectModForm(ModelForm):


    def __init__(self, *args, **kwargs):
        super(ProjectModForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].required = False


    class Meta:
        model = Project
        fields = ['name', 'tagline','website', 'status', 'scale',
                  'start_date', 'end_date', 'short_description', 'description']

class OrganizationModForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrganizationModForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = False


    class Meta:
        model = Project
        fields = ['name', 'tagline', 'website', 'start_date', 'short_description', 'description']
        #foreign key community

class OrganizationForm(ModelForm):

    class Meta:
        model = Project
        fields = ['name', 'tagline', 'website', 'start_date', 'short_description', 'description']
        #foreign key community

# Create your models here.
