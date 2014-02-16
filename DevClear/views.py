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
from DevClear.models import Organization,Project
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
    return render_to_response('home.html', {}, context_instance=RequestContext(request))

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
        name= request.POST.get('name')
        short= request.POST.get('short')
        tagline= request.POST.get('tagline')
        start_date= request.POST.get('sdate')
        end_date= request.POST.get('edate')
        description= request.POST.get('description')
        website= request.POST.get('website')
        scale= request.POST.get('scale')
        status= request.POST.get('status')

        org= request.user.organization_set.get(id=1)

        project = Project.create(name, org, short, tagline,
                                 start_date, end_date, description, website, scale, 'NS')
        project.save()
        project.members.add(request.user)

        return HttpResponseRedirect('/home/')#go to profile page normally



    return render_to_response('create_proj.html', {}, context_instance=RequestContext(request))

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

def view_profile(request, org_name=""):
    org = Organization.objects.get(name=org_name)

    if request.method == 'POST' and request.get.POST("username"):
        username = request.get.POST("username")
        Organization.members.remove(username)
        perm.revoke_all(username, org)


    return render_to_response('profile.html', {'org': org}, context_instance=RequestContext(request))


