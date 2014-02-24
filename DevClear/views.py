from django.shortcuts import render_to_response
# Create your views here.
from django.core.urlresolvers import reverse
from django.views.generic import CreateView
from django.template import RequestContext, loader
from django.http import request, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User, Group
from django.forms.models import model_to_dict
from DevClear.models import Organization,  OrganizationForm,  OrganizationModForm, OrganizationImage,  OrgImageForm, Project, ProjectImage, ProjectImageForm, ProjectForm, ProjectModForm
import object_permissions as perm


ORG_MEMBER_PERMS = ['add_member', 'join_proj', 'can_post', 'can_comment']

ORG_LOW_ADMIN_PERMS = ORG_MEMBER_PERMS + ['edit_org', 'downgrade_low_admin', 'make_low_admin', 'remove_low_admin',
                                          'remove_member', 'create_proj', 'delete_proj', 'post_as_org', 'comment_as_org',
                                          'delete_comment', 'delete_post',  'upload_image', 'delete_image',]

ORG_HIGH_ADMIN_PERMS = ORG_LOW_ADMIN_PERMS + ['remove_org',  'downgrade_high_admin', 'make_high_admin', 'remove_high_admin']

PROJ_MEMBER_PERMS = ['add_member', 'can_post', 'can_comment']

PROJ_LOW_ADMIN_PERMS = PROJ_MEMBER_PERMS + ['edit_proj', 'downgrade_low_admin', 'make_low_admin', 'remove_low_admin',
                                          'remove_member', 'post_as_proj', 'comment_as_proj', 'upload_image', 'delete_image',
                                          'delete_comment', 'delete_post']

PROJ_HIGH_ADMIN_PERMS = PROJ_LOW_ADMIN_PERMS + ['remove_proj',  'downgrade_high_admin', 'make_high_admin', 'remove_high_admin']




def main(request):
    if(request.user.is_authenticated()):
        return HttpResponseRedirect("/home/")
    return render_to_response('index.html', {}, context_instance=RequestContext(request))

def register(request):
    response=''
    if request.method =='POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if not User.objects.filter(username=username).count():
            if password1==password2:
                user = User.objects.create_user(username,
                                                request.POST['email'], password1)
                user.first_name = request.POST['fn']
                user.last_name = request.POST['ln']
                if(request.POST['email']):
                    user.email = request.POST['email']
                user.save()
                user = authenticate(username=username, password=password1)
                login(request, user)
                return HttpResponseRedirect('/home/')
            else:
                response="Sorry, your passwords didn't match"
        else:
            response='Sorry, cell phone number is already in use'

    return render_to_response('register.html', {'response':response}, context_instance=RequestContext(request))

@login_required
def home(request):
    return render_to_response('home.html', {'all_org': Organization.objects.all()},
                              context_instance=RequestContext(request))

@login_required
def settings(request):
    response =""


    if request.method == 'POST' and request.POST.get('fn') and request.POST.get('ln'):
        request.user.first_name        =request.POST.get('fn')
        request.user.last_name    =request.POST.get('ln')
        request.user.save()
        response = "Your name was succesfully changed to " + request.user.get_full_name()

    elif request.method == 'POST' and 'oldPass' in request.POST:
        if(request.user.check_password(request.POST.get('oldPass'))):
            if(request.POST.get('newPass1') == request.POST.get('newPass2')):
                request.user.set_password(request.POST.get('newPass1'))
                request.user.save()
                response = "Password Successfully Changed!"
            else:
                response = "Your confirmation password did not match"
        else:
            response = "You entered your old password incorrectly"
    elif request.method == 'POST' and request.POST.get('newEmail'):
        request.user.email=request.POST.get('newEmail')
        request.user.save()
        response = "Your email was successfully changed to " + request.user.email

    return render_to_response('settings.html', {'response' : response}, context_instance=RequestContext(request))

@login_required
def inbox(request):

    return render_to_response('inbox.html', {}, context_instance=RequestContext(request))

@login_required
def create_project(request, org_name=''):

    org = Organization.objects.get(name=org_name)
    if request.method == 'POST':

        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            sponsor_org = org
            scale = form.cleaned_data['scale']
            status = form.cleaned_data['status']
            tagline = form.cleaned_data['tagline']
            short = form.cleaned_data['short_description']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            description = form.cleaned_data['description']
            website = form.cleaned_data['website']

            image = form.cleaned_data['profile_image']

            project = Project.create(name, sponsor_org, image, short, tagline,
                                     start_date, end_date, description, website, scale, status)
            project.save()
            project.members.add(request.user)
            request.user.set_perms(PROJ_HIGH_ADMIN_PERMS, project)

            profile_url = "/profile/" + sponsor_org.name + '/' + name
            return HttpResponseRedirect(profile_url)  # Redirect after POST
    else:
        form = ProjectForm()  # An unbound form

    return render_to_response('create_proj.html', {
        'form': form,
        'org': org
        }, context_instance=RequestContext(request))

@login_required
def register_org(request):
    if request.method == 'POST':

        form = OrganizationForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            tagline = form.cleaned_data['tagline']
            website = form.cleaned_data['website']
            start_date = form.cleaned_data['start_date']
            short = form.cleaned_data['short_description']
            description = form.cleaned_data['description']


            image = form.cleaned_data['profile_image']

            organization = Organization.create(name, image, short, tagline, start_date, description, website)
            organization.save()
            organization.members.add(request.user)




            request.user.set_perms(ORG_HIGH_ADMIN_PERMS, organization)

            profile_url = '/profile/' + name + '/'

            return HttpResponseRedirect(profile_url)#go to profile page normally

    else:
        form = OrganizationForm()

    return render_to_response('register_org.html', {'form': form}, context_instance=RequestContext(request))

@login_required
def view_profile(request, org_name=""):
    org = Organization.objects.get(name=org_name)
    #print perm.get_user_perms(request.user, org)
    response = ''
    mod_form = None
    image_form = None




    #perm.set_user_perms(User.objects.get_by_natural_key('AustinFry'), HIGH_ADMIN_PERMS, org)
    #Organization.objects.get


    if request.method == 'POST' and request.POST.get("type") == "add_user":
        org.members.add(request.user)
        request.user.set_perms(ORG_MEMBER_PERMS, org)
        profile_url = '/profile/' + org.name + '/'
        return HttpResponseRedirect(profile_url)

    elif request.method == 'POST' and request.POST.get("type") == "upload_image":
        image_form = OrgImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            image_file = request.FILES['image']
            image = OrganizationImage.create(org, image_file)
            image.save()
            profile_url = '/profile/' + org.name + '/'
            return HttpResponseRedirect(profile_url)

    elif request.method == 'POST' and request.POST.get("type") == "remove_image":
        image = OrganizationImage.objects.get(pk=request.POST.get("image"))
        image.image.delete(save=True)
        image.delete()

        profile_url = '/profile/' + org.name + '/'
        return HttpResponseRedirect(profile_url)

    elif request.method == 'POST' and request.POST.get("type") == "remove":
        user = User.objects.get(username=request.POST.get("user"))
        org.members.remove(user)
        user.revoke_all(org)
        profile_url = '/profile/' + org.name + '/'
        return HttpResponseRedirect(profile_url)
        #check permissions in html

    elif request.method == 'POST' and request.POST.get("type") == "make_high_admin":
        user = User.objects.get(username=request.POST.get("user"))
        user.set_perms(ORG_HIGH_ADMIN_PERMS, org)
        profile_url = '/profile/' + org.name + '/'
        return HttpResponseRedirect(profile_url)

    elif request.method == 'POST' and request.POST.get("type") == "make_low_admin":
        user = User.objects.get(username=request.POST.get("user"))
        user.set_perms(ORG_LOW_ADMIN_PERMS, org)
        profile_url = '/profile/' + org.name + '/'
        return HttpResponseRedirect(profile_url)

    elif request.method == 'POST' and request.POST.get("type") == "downgrade_high_admin":
        user = User.objects.get(username=request.POST.get("user"))
        user.set_perms(ORG_LOW_ADMIN_PERMS, org)
        profile_url = '/profile/' + org.name + '/'
        return HttpResponseRedirect(profile_url)

    elif request.method == 'POST' and request.POST.get("type") == "downgrade_low_admin":
        user = User.objects.get(username=request.POST.get("user"))
        user.set_perms(ORG_MEMBER_PERMS, org)
        profile_url = '/profile/' + org.name + '/'
        return HttpResponseRedirect(profile_url)

    elif request.method == 'POST' and request.POST.get("type") == "remove_org":
        org.delete()
        return HttpResponseRedirect('/home/')

    elif request.method == 'POST' and request.POST.get("type") == "change_pref":
        mod_form = OrganizationModForm(request.POST, request.FILES)

        if mod_form.is_valid():
            new_name = mod_form.cleaned_data['name']
            new_tagline = mod_form.cleaned_data['tagline']
            new_website = mod_form.cleaned_data['website']
            new_start_date = mod_form.cleaned_data['start_date']
            new_short = mod_form.cleaned_data['short_description']
            new_description = mod_form.cleaned_data['description']

            new_image = mod_form.cleaned_data['profile_image']
            if not new_name == org.name:
                if not Organization.objects.filter(name=new_name).count():
                    org.name = new_name
            if not new_tagline == org.tagline:
                org.tagline = new_tagline
            if not new_start_date == org.start_date :
                org.start_date = new_start_date
            if not new_website == org.website:
                org.website = new_website
            if not new_short == org.short_description:
                org.short_description = new_short
            if not new_description == org.description:
                org.description = new_description

            if new_image is not None:
                org.profile_image.delete()
                org.profile_image = new_image

            org.save()

        profile_url = '/profile/' + org.name + '/'
        return HttpResponseRedirect(profile_url)

    else:
        fields_dict = model_to_dict(org)
        mod_form = OrganizationModForm(fields_dict, instance=org)
        image_form = OrgImageForm()

    high_admin = []
    low_admin = []
    member = []

    for user in org.members.all():
        if user.has_object_perm('make_high_admin', org):
            high_admin.append(user)
        elif user.has_object_perm('make_low_admin', org):
            low_admin.append(user)
        else:
            member.append(user)


    return render_to_response('profile.html', {'org': org,
                                               'mod_form': mod_form,
                                               'response': response,
                                               'image_form':image_form,
                                               'high_admin': high_admin,
                                               'low_admin': low_admin,
                                               'members':member},
                              context_instance=RequestContext(request))

@login_required
def view_project_profile(request, org_name="", proj_name=""):
    org = Organization.objects.get(name=org_name)
    proj = Project.objects.get(name=proj_name, sponsor_org=org)
    image_form = None
    mod_form = None

    if request.method == 'POST':

        if request.POST.get("type") == "add_user":
            proj.members.add(request.user)
            request.user.set_perms(PROJ_MEMBER_PERMS, proj)
            profile_url = '/profile/' + org.name + '/' + proj.name
            return HttpResponseRedirect(profile_url)
    #Fix
        elif request.POST.get("type") == "upload_image":
            image_form = ProjectImageForm(request.POST, request.FILES)
            if image_form.is_valid():
                image_file = request.FILES['image']
                image = ProjectImage.create(proj, image_file)
                image.save()

                profile_url = '/profile/' + org.name + '/' + proj.name
                return HttpResponseRedirect(profile_url)

        elif request.POST.get("type") == "remove_image":
            image = ProjectImage.objects.get(pk=request.POST.get("image"))
            image.image.delete(save=True)
            image.delete()

            profile_url = '/profile/' + org.name + '/' + proj.name
            return HttpResponseRedirect(profile_url)

        elif request.POST.get("type") == "remove":
            user = User.objects.get(username=request.POST.get("user"))
            proj.members.remove(user)
            user.revoke_all(proj)
            profile_url = '/profile/' + org.name + '/' + proj.name
            return HttpResponseRedirect(profile_url)

        elif request.POST.get("type") == "make_high_admin":
            user = User.objects.get(username=request.POST.get("user"))
            user.set_perms(PROJ_HIGH_ADMIN_PERMS, proj)
            profile_url = '/profile/' + org.name + '/' + proj.name
            return HttpResponseRedirect(profile_url)

        elif request.POST.get("type") == "make_low_admin":
            user = User.objects.get(username=request.POST.get("user"))
            user.set_perms(PROJ_LOW_ADMIN_PERMS, proj)
            profile_url = '/profile/' + org.name + '/' + proj.name
            return HttpResponseRedirect(profile_url)

        elif request.POST.get("type") == "downgrade_high_admin":
            user = User.objects.get(username=request.POST.get("user"))
            user.set_perms(PROJ_LOW_ADMIN_PERMS, proj)
            profile_url = '/profile/' + org.name + '/' + proj.name
            return HttpResponseRedirect(profile_url)


        elif request.POST.get("type") == "downgrade_low_admin":
            user = User.objects.get(username=request.POST.get("user"))
            user.set_perms(PROJ_MEMBER_PERMS, proj)
            profile_url = '/profile/' + org.name + '/' + proj.name
            return HttpResponseRedirect(profile_url)

        elif request.POST.get("type") == "remove_proj":
            proj.delete()
            return HttpResponseRedirect('/home/')

        elif request.POST.get("type") == "change_pref":
            mod_form = ProjectModForm(request.POST, request.FILES)

            if mod_form.is_valid():
                new_name = mod_form.cleaned_data['name']
                new_tagline = mod_form.cleaned_data['tagline']
                new_website = mod_form.cleaned_data['website']
                new_status = mod_form.cleaned_data['status']
                new_scale = mod_form.cleaned_data['scale']

                new_start_date = mod_form.cleaned_data['start_date']
                new_end_date = mod_form.cleaned_data['end_date']

                new_short = mod_form.cleaned_data['short_description']
                new_description = mod_form.cleaned_data['description']

                new_image = mod_form.cleaned_data['profile_image']

                if not new_name == proj.name:
                    if not Project.objects.filter(name=new_name).count():
                        proj.name = new_name
                if not new_tagline == proj.tagline:
                    proj.tagline = new_tagline
                if not new_website == proj.website:
                    proj.website = new_website
                if not new_status == proj.status:
                    proj.status = new_status
                if not new_scale == proj.scale:
                    proj.scale = new_scale
                if not new_start_date == proj.start_date:
                    proj.start_date = new_start_date
                if not new_end_date == proj.end_date:
                    proj.end_date = new_end_date
                if not new_short == proj.short_description:
                    proj.short_description = new_short
                if not new_description == proj.description:
                    proj.description = new_description

                if new_image is not None:
                    proj.profile_image.delete()
                    proj.profile_image = new_image


                proj.save()
                profile_url = '/profile/' + org.name + '/' +proj.name
                return HttpResponseRedirect(profile_url)
    else:
            fields_dict = model_to_dict(proj)
            mod_form = ProjectModForm(fields_dict, instance=proj)
            image_form = ProjectImageForm()



    high_admin = []
    low_admin = []
    member = []

    for user in proj.members.all():
        if user.has_object_perm('make_high_admin', proj):
            high_admin.append(user)
        elif user.has_object_perm('make_low_admin', proj):
            low_admin.append(user)
        else:
            member.append(user)

    return render_to_response('project_profile.html', {'proj': proj,
                                                        'mod_form': mod_form,
                                                        'image_form': image_form,
                                                        'high_admin': high_admin,
                                                       'low_admin': low_admin,
                                                       'members':member}, context_instance=RequestContext(request))
