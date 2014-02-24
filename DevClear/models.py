from django.db import models
from django.contrib.auth.models import User, Group
from django.forms import ModelForm
from object_permissions import register
import object_permissions
import os

#add email, hq location, region, area of development, images, org landline/main phone, profile image
class Organization(models.Model):
    name = models.CharField(max_length=50, unique=True)

    profile_image = models.ImageField(upload_to="organization/profile_image")

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
    def create(cls, name, profile_image, short_description, tagline, start_date, description, website):
        org = cls(name=name, profile_image=profile_image, short_description=short_description,
                   tagline=tagline, start_date=start_date, description=description, website=website)
        return org

class OrganizationImage(models.Model):

    org = models.ForeignKey(Organization, related_name='images')
    image = models.ImageField(upload_to='organization')

    @classmethod
    def create(cls, org, image):
        image_instance = cls(org=org, image=image)
        return image_instance


register(['view_org',

              'add_member', 'join_proj', 'can_post', 'can_comment',

              'edit_org', 'remove_member', 'downgrade_low_admin', 'make_low_admin', 'remove_low_admin',
              'create_proj', 'delete_proj', 'post_as_org', 'comment_as_org',  'upload_image', 'delete_image',
              'delete_comment', 'delete_post',

              'remove_org',  'downgrade_high_admin', 'make_high_admin', 'remove_high_admin'


             ], Organization, app_label='DevClear')







#add email, location, communities, region, images
class Project(models.Model):
    name = models.CharField(max_length=50, unique=True)

    profile_image = models.ImageField(upload_to="project/profile_image")

    members = models.ManyToManyField(User)
    sponsor_org = models.ForeignKey(Organization)


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
    def create(cls, name, sponsor_org, profile_image, short_description, tagline, start_date, end_date,
               description, website, scale, status):
        org = cls(name=name, sponsor_org=sponsor_org, profile_image=profile_image, short_description=short_description,
                   tagline=tagline, start_date=start_date, end_date=end_date, description=description,
                   website=website, scale=scale, status=status)
        return org



    def __unicode__(self):
        return self.name

    class Meta:
        ordering =('name',)

class ProjectImage(models.Model):
    proj = models.ForeignKey(Project, related_name='images')
    image = models.ImageField(upload_to='project')

    @classmethod
    def create(cls, proj, image):
        image_instance = cls(proj=proj, image=image)
        return image_instance

register(['view_proj',

          'add_member', 'can_post', 'can_comment',

          'edit_proj', 'remove_member', 'downgrade_low_admin', 'make_low_admin', 'remove_low_admin',
          'delete_proj', 'post_as_proj', 'comment_as_proj', 'upload_image', 'delete_image',
          'delete_comment', 'delete_post',

          'remove_proj',  'downgrade_high_admin', 'make_high_admin', 'remove_high_admin'


         ], Project, app_label='DevClear')



class OrgImageForm(ModelForm):
    class Meta:
        model = OrganizationImage
        fields = ['image']

class ProjectImageForm(ModelForm):
    class Meta:
        model = ProjectImage
        fields = ['image']


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'profile_image', 'tagline','website', 'status', 'scale',
                  'start_date', 'end_date', 'short_description', 'description']

class ProjectModForm(ModelForm):


    def __init__(self, *args, **kwargs):
        super(ProjectModForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].required = False


    class Meta:
        model = Project
        fields = ['name', 'profile_image', 'tagline','website', 'status', 'scale',
                  'start_date', 'end_date', 'short_description', 'description']

class OrganizationModForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrganizationModForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = False

    class Meta:
        model = Project
        fields = ['name', 'profile_image', 'tagline', 'website', 'start_date', 'short_description', 'description']
        #foreign key community

class OrganizationForm(ModelForm):

    class Meta:
        model = Project
        fields = ['name', 'profile_image', 'tagline', 'website', 'start_date', 'short_description', 'description']
        #foreign key community



class Message(models.Model):
    #id = models.CharField(max_length=50, unique=True)
    sender = models.OneToOneField(User)
    #receivers = models.ManyToManyField(User)

    date = models.DateField()
    time = models.TimeField()

    received = models.BooleanField()
    content = models.TextField(max_length=160)

    PLATFORM_CHOICES=(('W', 'Web'), ('S', 'SMS'))
    platform = models.CharField(max_length=1,
                                      choices=PLATFORM_CHOICES
                                      )


    def __unicode__(self):
        return self.id

    class Meta:
        ordering =('id',)


# Create your models here.
