from django.shortcuts import render_to_response
# Create your views here.
from django.core.urlresolvers import reverse
from django.views.generic import CreateView
from django.template import RequestContext, loader
from django.http import request, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from DevClear.models import Organization, Project, ProjectForm, OrganizationForm
import object_permissions as perm

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
def createProject(request):
    if request.method == 'POST':

        form = ProjectForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            sponsor_org = form.cleaned_data['sponsor_org']
            scale = form.cleaned_data['scale']
            status = form.cleaned_data['status']
            tagline = form.cleaned_data['tagline']
            short = form.cleaned_data['short_description']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            description = form.cleaned_data['description']
            website = form.cleaned_data['website']

            project = Project.create(name, sponsor_org, short, tagline,
                                     start_date, end_date, description, website, scale, status)
            project.save()
            project.members.add(request.user)
            perm.set_user_perms(request.user, ['view', 'edit', 'remove', 'add_project', 'add_member']
                                , sponsor_org)

            profile_url = "/profile/" + sponsor_org.name + '/' + name
            return HttpResponseRedirect(profile_url)  # Redirect after POST
    else:
        form = ProjectForm()  # An unbound form

    return render_to_response('create_proj.html', {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def register_org(request):
    if request.method == 'POST':
        name= request.POST.get('name')

        if not Organization.objects.filter(name=name).count():
            short= request.POST.get('short')
            tagline= request.POST.get('tagline')
            date= request.POST.get('date')
            description= request.POST.get('description')
            website= request.POST.get('website')

            organization = Organization.create(name, short, tagline, date, description, website)
            organization.save()
            organization.members.add(request.user)
            perm.set_user_perms(request.user,['view', 'edit', 'remove', 'add_project', 'add_member'], organization)

            profile_url = '/profile/' + name + '/'

            return HttpResponseRedirect(profile_url)#go to profile page normally

    return render_to_response('register_org.html', {}, context_instance=RequestContext(request))


@login_required
def view_profile(request, org_name=""):
    org = Organization.objects.get(name=org_name)
    response = ''


    #perm.set_user_perms(User.objects.get_by_natural_key('AustinFry'), ['view', 'edit', 'remove', 'add_project', 'add_member'], org)
    #Organization.objects.get

    if request.method == 'POST' and request.POST.get("type") == "add_user":
        org.members.add(request.user)
        perm.grant(request.user, 'view', org)
        profile_url = '/profile/' + org.name + '/'
        return HttpResponseRedirect(profile_url)

    elif request.method == 'POST' and request.POST.get("type") == "remove":
        user = User.objects.get(username=request.POST.get("user"))
        org.members.remove(user)
        perm.revoke_all(user, org)
        profile_url = '/profile/' + org.name + '/'
        return HttpResponseRedirect(profile_url)


    elif request.method == 'POST' and request.POST.get("type") == "upgrade":
        user = User.objects.get(username=request.POST.get("user"))
        perm.set_user_perms(user, ['view', 'edit', 'remove', 'add_project', 'add_member'], org)
        profile_url = '/profile/' + org.name + '/'
        return HttpResponseRedirect(profile_url)

    elif request.method == 'POST' and request.POST.get("type") == "downgrade":
        user = User.objects.get(username=request.POST.get("user"))
        perm.set_user_perms(user, ['view'], org)
        profile_url = '/profile/' + org.name + '/'
        return HttpResponseRedirect(profile_url)

    elif request.method == 'POST' and request.POST.get("type") == "remove_org":
        org.delete()
        return HttpResponseRedirect('/home/')

    elif request.method == 'POST' and request.POST.get("type") == "change_pref":
        new_name = request.POST.get('name')
        new_tagline = request.POST.get('tagline')
        new_start_date = request.POST.get('start_date')
        new_website = request.POST.get('website')
        if not org.name == new_name:
            if not Organization.objects.filter(name=new_name).count():
                org.name = new_name
                response += "Your organization's name has been changed to " + new_name + "\n"
            else:
                response += "There is already an organization with this name! Sorry!" + "\n"
        if not org.tagline == new_tagline:
            org.tagline = new_tagline
            response += "Your organization's motto has been changed to " + new_tagline + "\n"

        if not new_start_date == '':
            org.start_date = new_start_date
            response += "Your organization's start date has been changed to " + new_start_date + "\n"
        if not org.website == new_website:
            org.website = new_website
            response += "Your organization's website has been changed to " + new_website + "\n"

        org.save()
        profile_url = '/profile/' + org.name + '/'
        return HttpResponseRedirect(profile_url)

    else:
        form = OrganizationForm()

    return render_to_response('profile.html', {'org': org, 'form':form, 'response': response},
                              context_instance=RequestContext(request))


def view_project_profile(request, org_name="", proj_name=""):
    org = Organization.objects.get(name=org_name)
    proj = Project.objects.get(name=proj_name, sponsor_org=org)

    if request.method == 'POST' and request.POST.get("type") == "add_user":
        if 'view' in perm.get_user_perms(request.user, org):#change to join project
            proj.members.add(request.user)
            perm.grant(request.user, 'view', org)
            profile_url = '/profile/' + org.name + '/' + proj.name
            return HttpResponseRedirect(profile_url)

    return render_to_response('project_profile.html', {'proj': proj}, context_instance=RequestContext(request))
