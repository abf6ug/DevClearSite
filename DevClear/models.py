from django.db import models
from django.contrib.auth.models import User, Group
from django.forms import ModelForm
from object_permissions import register
import datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

#add email, hq location, region, area of development, org landline/main phone
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

    posts = generic.GenericRelation('Post')
    images = generic.GenericRelation('Image')


    def __unicode__(self):
        return self.name

    class Meta:
        ordering =('name',)


    @classmethod
    def create(cls, name, profile_image, short_description, tagline, start_date, description, website):
        org = cls(name=name, profile_image=profile_image, short_description=short_description,
                   tagline=tagline, start_date=start_date, description=description, website=website)
        return org

#add email, location, communities, region
class Project(models.Model):
    name = models.CharField(max_length=50)

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

    communities = models.ManyToManyField('Community')

    posts = generic.GenericRelation('Post')
    images = generic.GenericRelation('Image')

    def __unicode__(self):
        return self.name

    class Meta:
        ordering =('name',)

    @classmethod
    def create(cls, name, sponsor_org, profile_image, short_description, tagline, start_date, end_date,
               description, website, scale, status):
        proj = cls(name=name, sponsor_org=sponsor_org, profile_image=profile_image, short_description=short_description,
                   tagline=tagline, start_date=start_date, end_date=end_date, description=description,
                   website=website, scale=scale, status=status)
        return proj

class Community(models.Model):

    name  = models.CharField(max_length=50)
    profile_image = models.ImageField(upload_to="community/profile_image")
    tagline  = models.CharField(max_length=200)


    members = models.ManyToManyField(User, related_name='community_members')

    region = models.CharField(max_length=50)#county? city? locale? coordinates?
    country = models.CharField(max_length=50)

    comm_lead = models.ForeignKey(User)

    posts = generic.GenericRelation('Post')
    images = generic.GenericRelation('Image')

    #needPost


    description = models.TextField(max_length=2000)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering =('name',)

    @classmethod
    def create(cls, name, profile_image, tagline,
               region, country, description, comm_lead):
        comm = cls(name=name, profile_image=profile_image, tagline=tagline,
                   region=region, country=country, description=description, comm_lead=comm_lead)
        return comm


class Post(models.Model):

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    #org = models.ForeignKey(Organization, related_name='posts')

    text = models.TextField(max_length=2000)
    timestamp = models.DateTimeField()
    user = models.ForeignKey(User)

    comments = generic.GenericRelation('Post')


    @classmethod
    def create(cls, user, profile, text):
       post = cls(user=user, content_object = profile, text=text, timestamp=datetime.datetime.now())

       return post

class Image(models.Model):

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    image = models.ImageField(upload_to='images',max_length=500,blank=True,null=True)
    thumbnail = models.ImageField(upload_to='thumbnails',max_length=500,blank=True,null=True)

    def create_thumbnail(self):
        # original code for this method came from
        # http://snipt.net/danfreak/generate-thumbnails-in-django-with-pil/

        # If there is no image associated with this.
        # do not create thumbnail
        if not self.image:
            return


        from PIL import Image
        from cStringIO import StringIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        import os

        # Set our max thumbnail size in a tuple (max width, max height)
        THUMBNAIL_SIZE = (200,200)

        DJANGO_TYPE = self.image.file.content_type

        if DJANGO_TYPE == 'image/jpeg':
            PIL_TYPE = 'jpeg'
            FILE_EXTENSION = 'jpg'
        elif DJANGO_TYPE == 'image/png':
            PIL_TYPE = 'png'
            FILE_EXTENSION = 'png'

        # Open original photo which we want to thumbnail using PIL's Image
        image = Image.open(StringIO(self.image.read()))

        # Convert to RGB if necessary
        # Thanks to Limodou on DjangoSnippets.org
        # http://www.djangosnippets.org/snippets/20/
        #
        # I commented this part since it messes up my png files
        #
        #if image.mode not in ('L', 'RGB'):
        #    image = image.convert('RGB')

        # We use our PIL Image object to create the thumbnail, which already
        # has a thumbnail() convenience method that contrains proportions.
        # Additionally, we use Image.ANTIALIAS to make the image look better.
        # Without antialiasing the image pattern artifacts may result.
        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

        # Save the thumbnail
        temp_handle = StringIO()
        image.save(temp_handle, PIL_TYPE)
        temp_handle.seek(0)

        # Save image to a SimpleUploadedFile which can be saved into
        # ImageField
        suf = SimpleUploadedFile(os.path.split(self.image.name)[-1],
        temp_handle.read(), content_type=DJANGO_TYPE)
        # Save SimpleUploadedFile into image field
        self.thumbnail.save('%s_thumbnail.%s'%(os.path.splitext(suf.name)[0],FILE_EXTENSION), suf, save=False)

    def save(self):
        # create a thumbnail
        self.create_thumbnail()

        super(Image, self).save()


    @classmethod
    def create(cls, attach, image):
        image_instance = cls(content_object=attach, image=image)
        return image_instance




register(['view_org',

              'add_member', 'join_proj', 'can_post', 'can_comment',

              'edit_org', 'remove_member', 'downgrade_low_admin', 'make_low_admin', 'remove_low_admin',
              'create_proj', 'delete_proj', 'post_as_org', 'comment_as_org',  'upload_image', 'delete_image',
              'delete_comment', 'delete_post',

              'remove_org',  'downgrade_high_admin', 'make_high_admin', 'remove_high_admin'


             ], Organization, app_label='DevClear')


register(['view_proj',

          'add_member', 'can_post', 'can_comment',

          'edit_proj', 'remove_member', 'downgrade_low_admin', 'make_low_admin', 'remove_low_admin',
          'delete_proj', 'post_as_proj', 'comment_as_proj', 'upload_image', 'delete_image',
          'delete_comment', 'delete_post',

          'remove_proj',  'downgrade_high_admin', 'make_high_admin', 'remove_high_admin'


         ], Project, app_label='DevClear')


register(['can_post', 'can_comment',

              'add_member', 'edit_comm', 'remove_member', 'post_as_comm', 'comment_as_comm',  'upload_image', 'delete_image',
              'delete_comment', 'delete_post', 'swap_admin', 'remove_comm'#?


             ], Community, app_label='DevClear')



class ImageForm(ModelForm):
    class Meta:
        model = Image
        fields = ['image']

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text']

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

class CommunityForm(ModelForm):

    class Meta:
        model = Community
        fields = ['name', 'profile_image', 'tagline', 'region', 'country','description']
        #foreign key community


class CommunityModForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommunityModForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = False

    class Meta:
        model = Community
        fields = ['name', 'profile_image', 'tagline', 'region', 'country', 'description']
# Create your models here.

class ProjCommLinkForm(ModelForm):
    class Meta:
        model = Project
        fields = ['communities']