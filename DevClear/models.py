from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from object_permissions import register


class Organization(models.Model):
    name = models.CharField(max_length=50)

    members = models.ManyToManyField(User)
    projects = models.ManyToManyField('Project', blank=True)

    short_description = models.CharField(max_length=300, blank=True)
    tagline = models.CharField(max_length=100, blank=True)

    start_date = models.DateField()

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


class Project(models.Model):
    name = models.CharField(max_length=50)
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
    short_description = models.CharField(max_length=300)
    start_date = models.DateField()
    end_date= models.DateField()

    description = models.TextField(max_length=2000)

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

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'sponsor_org', 'scale', 'status', 'tagline', 'short_description',
                  'start_date', 'end_date', 'description', 'website']

    #foreign key community

# Create your models here.
