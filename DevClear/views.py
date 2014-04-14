from django.shortcuts import render_to_response
# Create your views here.
from django.core.urlresolvers import reverse
from django.views.generic import CreateView
from django.template import RequestContext, loader
from django.http import request, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User, Group
from django.forms.models import model_to_dict
from DevClear.models import Organization,  OrganizationForm,  OrganizationModForm, Post, PostForm, Image,  ImageForm, Message, MessageForm, \
    Project, ProjectForm, ProjectModForm, Community, CommunityForm, CommunityModForm, ProjCommLinkForm, Conversation
from django.db.models.query import QuerySet
import datetime
from django.contrib.contenttypes.generic import ContentType
from object_permissions import get_users_all


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

COMM_MEMBER_PERMS = ['can_post', 'can_comment']

COMM_LEAD_PERMS = COMM_MEMBER_PERMS + ['add_member', 'edit_comm', 'remove_member', 'post_as_comm', 'comment_as_comm',  'upload_image', 'delete_image',
                                       'delete_comment', 'delete_post', 'swap_admin', 'remove_comm']





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

    feed = []

    for org in request.user.organization_set.all():
        for post in org.posts.all():
            feed.append(post)


    for proj in request.user.project_set.all():
        for post in proj.posts.all():
            feed.append(post)


    for comm in request.user.community_set.all():
        for post in comm.posts.all():
            feed.append(post)

    feed.sort(key=lambda x: x.timestamp, reverse=False)

    return render_to_response('home.html', {'feed':feed},
                              context_instance=RequestContext(request))

@login_required
def all_org(request):
    return render_to_response('list_profiles.html', {'list': Organization.objects.all()},
                              context_instance=RequestContext(request))

def all_comm(request):
    return render_to_response('list_profiles.html', {'list': Community.objects.all()},
                              context_instance=RequestContext(request))

@login_required
def user_org_list(request):

    return render_to_response('list_profiles.html', {'list': request.user.organization_set.all()},
                              context_instance=RequestContext(request))

@login_required
def user_proj_list(request):

    return render_to_response('list_profiles.html', {'list': request.user.project_set.all()},
                              context_instance=RequestContext(request))
@login_required
def all_users(request):
    if request.method == 'POST':
        if request.user.is_staff:
            username = request.POST.get('user')
            user=User.objects.get(username=username)
            user.is_staff=True
            user.save()
            for prof in Organization.objects.all():
                prof.members.remove(user)
                user.set_perms(ORG_HIGH_ADMIN_PERMS, prof)
            for prof in Community.objects.all():
                prof.members.remove(user)
                user.set_perms(COMM_LEAD_PERMS, prof)
            for prof in Project.objects.all():
                prof.members.remove(user)
                user.set_perms(PROJ_HIGH_ADMIN_PERMS, prof)

    member_list=[]
    for member in User.objects.all():
        if not member.is_staff:
            member_list.append(member)

    return render_to_response('list_users.html', {'list': member_list},
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
def inbox(request, conv_id=""):

    admin_profiles = []
    admin_convos = []
    #create list of profiles user has admin rights to
    for profile in request.user.get_objects_all_perms(Organization, ORG_LOW_ADMIN_PERMS):
        admin_profiles.append(profile)
    for profile in request.user.get_objects_all_perms(Project, PROJ_LOW_ADMIN_PERMS):
        admin_profiles.append(profile)
    for profile in request.user.get_objects_all_perms(Community, COMM_LEAD_PERMS):
        admin_profiles.append(profile)




    convo_msg_list =[]
    convo_profiles=[]
    all_profiles = []
    message_form=None
    conversation=None
    if conv_id != "":
        conversation = Conversation.objects.get(pk=conv_id)

    if conversation != None:
        message_form = MessageForm()
        if request.user.has_perm('can_view', conversation):#restrain to only admins of tis conv

            #create ordered message list
            for message in conversation.message_set.order_by('timestamp').all():
                convo_msg_list.append(message)

            #create list of profiles in the conversation
            for prof in conversation.organizations.all():
                convo_profiles.append(prof)
            for prof in conversation.projects.all():
                convo_profiles.append(prof)
            for prof in conversation.communities.all():
                convo_profiles.append(prof)

            #create list of addable profiles to the conversation
            for prof in Organization.objects.all():
                if prof not in convo_profiles:
                    all_profiles.append(prof)
            for prof in Project.objects.all():
                if prof not in convo_profiles:
                    all_profiles.append(prof)
            for prof in Community.objects.all():
                if prof not in convo_profiles:
                    all_profiles.append(prof)

            if request.method == 'POST':
                if request.POST.get("type") == "message":
                    message_form = MessageForm(request.POST)
                    if message_form.is_valid():
                        msg = Message.create(request.user, request.POST.get('text'), conversation)
                        msg.save()

                if request.POST.get("type") == "add_participant":
                    participants = request.POST.getlist("participants")
                    for prof in participants:
                        temp = prof.split(': ')
                        prof_type= temp[0]
                        prof_name=temp[1]

                        #get actual instance of profile from selection
                        if prof_type=="Organization":
                            prof_obj = Organization.objects.get(name=prof_name)
                            conversation.organizations.add(prof_obj)
                        elif prof_type=="Project":
                            prof_obj = Project.objects.get(name=prof_name)
                            conversation.projects.add(prof_obj)
                        elif prof_type=="Community":
                            prof_obj = Community.objects.get(name=prof_name)
                            conversation.communities.add(prof_obj)

                        #add viewing permissions to the new profile's admin users
                        for temp_user in get_users_all(prof_obj, perms=['remove_member']):
                            temp_user.set_perms(['can_view'], conversation)

                return HttpResponseRedirect("/home/inbox/" + conv_id)

        else:
            return HttpResponseRedirect("/home/inbox/" )


    return render_to_response('inbox.html', {'message_form':message_form,
                                             'admin_profiles':admin_profiles,
                                             "conversation":convo_msg_list,
                                             "convo_profiles":convo_profiles,
                                             "all_profiles":all_profiles,
                                             }, context_instance=RequestContext(request))

    #for prof in Organization.objects.all():
    #           if prof not in convo_profiles:
    #              all_profiles+(prof.__class__.__name__ + ": " + prof.name, prof.__class__.__name__ + ": " + prof.name)
    #     for prof in Project.objects.all():
    #        if prof not in convo_profiles:
    #           all_profiles+(prof.__class__.__name__ + ": " + prof.name, prof.__class__.__name__ + ": " + prof.name)
    #  for prof in Community.objects.all():
    #     if prof not in convo_profiles:
    #        all_profiles+(prof.__class__.__name__ + ": " + prof.name, prof.__class__.__name__ + ": " + prof.name)
    # add_participants_form = MultipleChoiceField(widget=CheckboxSelectMultiple, choices=all_profiles)

@login_required
def create_project(request, org_name=""):

    sponsor_org = Organization.objects.get(name=org_name)

    if request.method == 'POST':

        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            if not Project.objects.filter(name=name):
                scale = form.cleaned_data['scale']
                status = form.cleaned_data['status']
                tagline = form.cleaned_data['tagline']
                short = form.cleaned_data['short_description']
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                description = form.cleaned_data['description']
                website = form.cleaned_data['website']

                image = form.cleaned_data['profile_image']
                profile_url = "/project/" + name + "/"


                project = Project.create(name, sponsor_org, image, short, tagline,
                                         start_date, end_date, description, website, scale, status, profile_url)
                if request.user.is_staff:
                    project.is_verified=True

                project.save()

                if not request.user.is_staff:
                    project.members.add(request.user)

                request.user.set_perms(PROJ_HIGH_ADMIN_PERMS, project)
                for member in User.objects.all():
                    if member.is_staff:
                        member.set_perms(PROJ_HIGH_ADMIN_PERMS, project)



                return HttpResponseRedirect(project.profile_url)  # Redirect after POST


    else:
        form = ProjectForm()  # An unbound form

    return render_to_response('create_proj.html', {
        'form': form,
        'org': sponsor_org,
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
            profile_url = '/organization/' + name + '/'


            organization = Organization.create(name, image, short, tagline, start_date, description, website, profile_url)
            if request.user.is_staff:
                organization.is_verified=True
            organization.save()

            if not request.user.is_staff:
                organization.members.add(request.user)

            request.user.set_perms(ORG_HIGH_ADMIN_PERMS, organization)
            for member in User.objects.all():
                if member.is_staff:
                    member.set_perms(ORG_HIGH_ADMIN_PERMS, organization)

            return HttpResponseRedirect(organization.profile_url)#go to profile page normally

    else:
        form = OrganizationForm()

    return render_to_response('register_org.html', {'form': form}, context_instance=RequestContext(request))

def register_community(request):
    if request.method == 'POST':

        form = CommunityForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            tagline = form.cleaned_data['tagline']
            region = form.cleaned_data['region']
            country = form.cleaned_data['country']

            description = form.cleaned_data['description']


            image = form.cleaned_data['profile_image']
            profile_url = '/community/' + name + '/'


            community = Community.create(name, image, tagline, region, country, description, request.user, profile_url)
            if request.user.is_staff:
                community.is_verified=True
            community.save()

            if request.user.is_staff:
                community.members.add(request.user)



            request.user.set_perms(COMM_LEAD_PERMS, community)
            for member in User.objects.all():
                if member.is_staff:
                    member.set_perms(COMM_LEAD_PERMS, community)


            return HttpResponseRedirect(community.profile_url)#go to profile page normally

    else:
        form = CommunityForm()

    return render_to_response('register_comm.html', {'form': form}, context_instance=RequestContext(request))

#unused
@login_required
def profile_feed(request, org_name=""):
    org = Organization.objects.get(name=org_name)
    response = ''

    post_form = None


    if request.method == 'POST':
        if request.POST.get("type") == "delete_post":
            post = Post.objects.get(pk=request.POST.get("post_id"))
            post.delete()

        elif request.POST.get("type") == "comment":
            post_form = PostForm(request.POST)
            if post_form.is_valid():
                feed_post = Post.objects.get(pk=request.POST.get('feed_post'))
                post = Post.create(request.user, feed_post, request.POST.get('text'))
                post.save()

        elif request.POST.get("type") == "post":
            post_form = PostForm(request.POST)
            if post_form.is_valid():
                post = Post.create(request.user, org, request.POST.get('text'))
                post.save()

        return HttpResponseRedirect(org.profile_url)

    else:
        post_form= PostForm()


    return render_to_response('profile_feed.html', {'org': org,

                                                    'response': response,
                                                    'post_form':post_form,
                                                    },
                              context_instance=RequestContext(request))

def send_message(user, receiver_profile, s_profile_string, msg_txt):
    conversation = None
    sender_profile = None


    temp = s_profile_string.split(': ')
    sender_prof_type= temp[0]
    sender_prof_name=temp[1]

    if sender_prof_type=="Organization":
        sender_profile=Organization.objects.get(name=sender_prof_name)
    elif sender_prof_type=="Project":
        sender_profile=Project.objects.get(name=sender_prof_name)
    elif sender_prof_type=="Community":
        sender_profile=Community.objects.get(name=sender_prof_name)
    else:
        return HttpResponseRedirect('/home/')

    for temp_convo in Conversation.objects.all():#check if convo exists
        master_list= []
        for prof in temp_convo.organizations.all():
            master_list.append(prof)
        for prof in temp_convo.projects.all():
            master_list.append(prof)
        for prof in temp_convo.communities.all():
            master_list.append(prof)

        if (sender_profile in master_list) and (receiver_profile in master_list) and (len(master_list)==2):
            conversation=temp_convo


    if conversation == None:
        conversation = Conversation.create()
        conversation.save()

        r_prof_type = receiver_profile.__class__.__name__

        if r_prof_type=="Organization":
            conversation.organizations.add(receiver_profile)
        elif r_prof_type=="Project":
            conversation.projects.add(receiver_profile)
        elif r_prof_type=="Community":
            conversation.communities.add(receiver_profile)

        for temp_user in get_users_all(receiver_profile, perms=['remove_member']):
            temp_user.set_perms(['can_view'], conversation)
            print "granting to receiver prof admins"

        if sender_prof_type=="Organization":
            conversation.organizations.add(sender_profile)
        elif sender_prof_type=="Project":
            conversation.projects.add(sender_profile)
        elif sender_prof_type=="Community":
            conversation.communities.add(sender_profile)

        for temp_user in get_users_all(sender_profile, perms=['remove_member']):
            temp_user.set_perms(['can_view'], conversation)
            print "granting to sender prof admins"


    conversation.save()
    msg = Message.create(user, msg_txt, conversation)
    msg.save()
    return str(conversation.pk)


@login_required
def view_profile(request, org_name=""):
    org = Organization.objects.get(name=org_name)
    response = ''

    image_form =ImageForm()
    fields_dict = model_to_dict(org)
    mod_form = OrganizationModForm(fields_dict)
    post_form = PostForm()
    message_form = MessageForm()

    admin_profiles=[]
    for profile in request.user.get_objects_all_perms(Organization, ORG_LOW_ADMIN_PERMS):
        admin_profiles.append(profile)
    for profile in request.user.get_objects_all_perms(Project, PROJ_LOW_ADMIN_PERMS):
        admin_profiles.append(profile)
    for profile in request.user.get_objects_all_perms(Community, COMM_LEAD_PERMS):
        admin_profiles.append(profile)

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

    #perm.set_user_perms(User.objects.get_by_natural_key('AustinFry'), ORG_HIGH_ADMIN_PERMS, org)
    #Organization.objects.get
    if request.method == 'POST':
        if request.POST.get("type") == "change_verification":
            if org.is_verified==True:
                org.is_verified=False
            else:
                org.is_verified=True

            org.save()

        elif request.POST.get("type") == "message":
            message_form = MessageForm(request.POST)
            if message_form.is_valid():
                convo_id = send_message(request.user, org,  request.POST.get('profile'), request.POST.get('text'))
                return HttpResponseRedirect("/home/inbox/" + str(convo_id))


        elif request.POST.get("type") == "delete_post":
            post = Post.objects.get(pk=request.POST.get("post_id"))
            post.delete()

        elif request.POST.get("type") == "comment":
            post_form = PostForm(request.POST)
            if post_form.is_valid():
                feed_post = Post.objects.get(pk=request.POST.get('feed_post'))
                post = Post.create(request.user, feed_post, request.POST.get('text'))
                post.save()

        elif request.POST.get("type") == "post":
            post_form = PostForm(request.POST)
            if post_form.is_valid():
                post = Post.create(request.user, org, request.POST.get('text'))
                post.save()

        elif request.POST.get("type") == "add_user":
            org.members.add(request.user)
            request.user.set_perms(ORG_MEMBER_PERMS, org)

        elif request.POST.get("type") == "upload_image":
            image_form = ImageForm(request.POST, request.FILES)
            if image_form.is_valid():
                image_file = request.FILES['image']
                image = Image.create(org, image_file)
                image.save()


        elif request.POST.get("type") == "remove_image":
            image = Image.objects.get(pk=request.POST.get("image"))
            image.image.delete(save=True)
            image.delete()

        elif request.POST.get("type") == "remove":
            user = User.objects.get(username=request.POST.get("user"))
            if user not in high_admin or len(high_admin)>1:
                org.members.remove(user)
                user.revoke_all(org)
                for proj in org.project_set.all():
                    user.revoke_all(proj)

                    #check permissions in html

        elif request.POST.get("type") == "make_high_admin":
            user = User.objects.get(username=request.POST.get("user"))
            user.set_perms(ORG_HIGH_ADMIN_PERMS, org)

        elif request.POST.get("type") == "make_low_admin":
            user = User.objects.get(username=request.POST.get("user"))
            for convo in org.conversation_set.all():
                user.set_perms(['can_view'], convo)
            user.set_perms(ORG_LOW_ADMIN_PERMS, org)

        elif request.POST.get("type") == "downgrade_high_admin":
            user = User.objects.get(username=request.POST.get("user"))
            user.set_perms(ORG_LOW_ADMIN_PERMS, org)

        elif request.POST.get("type") == "downgrade_low_admin":
            user = User.objects.get(username=request.POST.get("user"))
            user.set_perms(ORG_MEMBER_PERMS, org)
            for convo in org.conversation_set.all():
                user.revoke_all(convo)
            for proj in org.project_set.all():
                if user.has_all_perms(proj, PROJ_HIGH_ADMIN_PERMS) or user.has_all_perms(proj, PROJ_LOW_ADMIN_PERMS):
                    print 'downgrade project perms'
                    user.set_perms(PROJ_MEMBER_PERMS, proj)

        elif request.POST.get("type") == "remove_org":
            org.delete()
            return HttpResponseRedirect('/home/')

        elif request.POST.get("type") == "change_pref":
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
                        org.profile_url = "/organization/" + new_name +"/"

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



        return HttpResponseRedirect(org.profile_url)







    return render_to_response('profile.html', {'org': org,
                                               'admin_profiles':admin_profiles,

                                               'response': response,
                                               'image_form':image_form,
                                               'mod_form': mod_form,
                                               'post_form':post_form,
                                               'message_form':message_form,
                                               'high_admin': high_admin,
                                               'low_admin': low_admin,
                                               'members':member},
                              context_instance=RequestContext(request))

@login_required
def view_project_profile(request, proj_name=""):
    proj = Project.objects.get(name=proj_name)
    org = proj.sponsor_org

    image_form =ImageForm()
    fields_dict = model_to_dict(proj)
    mod_form = OrganizationModForm(fields_dict)
    post_form = PostForm()
    message_form = MessageForm()
    link_form = ProjCommLinkForm()

    admin_profiles=[]
    for profile in request.user.get_objects_all_perms(Organization, ORG_LOW_ADMIN_PERMS):
        admin_profiles.append(profile)
    for profile in request.user.get_objects_all_perms(Project, PROJ_LOW_ADMIN_PERMS):
        admin_profiles.append(profile)
    for profile in request.user.get_objects_all_perms(Community, COMM_LEAD_PERMS):
        admin_profiles.append(profile)



    #perm.set_user_perms(User.objects.get_by_natural_key('AustinFry'), ORG_HIGH_ADMIN_PERMS, org)
    #Organization.objects.get
    if request.method == 'POST':
        if request.POST.get("type") == "change_verification":
            if proj.is_verified==True:
                proj.is_verified=False
            else:
                proj.is_verified=True

            proj.save()

        if request.POST.get("type") == "message":
            message_form = MessageForm(request.POST)
            if message_form.is_valid():
                convo_id = send_message(request.user, proj,  request.POST.get('profile'), request.POST.get('text'))
                return HttpResponseRedirect("/home/inbox/" + str(convo_id))


        elif request.POST.get('type') == "link":
            link_form = ProjCommLinkForm(request.POST)
            if link_form.is_valid():
                for comm in proj.communities.all():
                    print "removing"
                    proj.communities.remove(comm)
                for comm in link_form.cleaned_data['communities']:
                    comm=Community.objects.get(name=comm)
                    proj.communities.add(comm)

        elif request.POST.get("type") == "delete_post":
            post = Post.objects.get(pk=request.POST.get("post_id"))
            post.delete()
            profile_url = '/project/' + proj.name

        elif request.POST.get("type") == "comment":
            post_form = PostForm(request.POST)
            if post_form.is_valid():
                feed_post = Post.objects.get(pk=request.POST.get('feed_post'))
                post = Post.create(request.user, feed_post, request.POST.get('text'))
                post.save()

        elif request.POST.get("type") == "post":
            post_form = PostForm(request.POST)
            if post_form.is_valid():
                post = Post.create(request.user, proj, request.POST.get('text'))
                post.save()

        elif request.POST.get("type") == "add_user":
            proj.members.add(request.user)
            request.user.set_perms(PROJ_MEMBER_PERMS, proj)

        elif request.POST.get("type") == "upload_image":
            image_form = ImageForm(request.POST, request.FILES)
            if image_form.is_valid():
                image_file = request.FILES['image']
                image = Image.create(proj, image_file)
                image.save()

        elif request.POST.get("type") == "remove_image":
            image = Image.objects.get(pk=request.POST.get("image"))
            image.image.delete(save=True)
            image.delete()

        elif request.POST.get("type") == "remove":
            user = User.objects.get(username=request.POST.get("user"))
            proj.members.remove(user)
            user.revoke_all(proj)

        elif request.POST.get("type") == "make_high_admin":
            user = User.objects.get(username=request.POST.get("user"))
            user.set_perms(PROJ_HIGH_ADMIN_PERMS, proj)

        elif request.POST.get("type") == "make_low_admin":
            user = User.objects.get(username=request.POST.get("user"))
            for convo in proj.conversation_set.all():
                user.set_perms(['can_view'], convo)
            user.set_perms(PROJ_LOW_ADMIN_PERMS, proj)

        elif request.POST.get("type") == "downgrade_high_admin":
            user = User.objects.get(username=request.POST.get("user"))
            user.set_perms(PROJ_LOW_ADMIN_PERMS, proj)

        elif request.POST.get("type") == "downgrade_low_admin":
            user = User.objects.get(username=request.POST.get("user"))
            for convo in proj.conversation_set.all():
                user.revoke_all(convo)
            user.set_perms(PROJ_MEMBER_PERMS, proj)

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
                        proj.profile_url = "/project/" + new_name +"/"
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

        return HttpResponseRedirect(proj.profile_url)


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
                                                       'message_form': message_form,
                                                       'link_form' : link_form,
                                                       'image_form': image_form,
                                                       'mod_form': mod_form,
                                                       'post_form': post_form,
                                                       'high_admin': high_admin,
                                                       'low_admin': low_admin,
                                                       'admin_profiles':admin_profiles,
                                                       'members':member}, context_instance=RequestContext(request))
@login_required()
def view_community_profile(request, comm_name=""):
    comm = Community.objects.get(name=comm_name)
    response = ''

    image_form =ImageForm()
    fields_dict = model_to_dict(comm)
    mod_form = CommunityModForm(fields_dict)
    post_form = PostForm()
    message_form = MessageForm()

    admin_profiles=[]
    for profile in request.user.get_objects_all_perms(Organization, ORG_LOW_ADMIN_PERMS):
        admin_profiles.append(profile)
    for profile in request.user.get_objects_all_perms(Project, PROJ_LOW_ADMIN_PERMS):
        admin_profiles.append(profile)
    for profile in request.user.get_objects_all_perms(Community, COMM_LEAD_PERMS):
        admin_profiles.append(profile)



    #perm.set_user_perms(User.objects.get_by_natural_key('AustinFry'), ORG_HIGH_ADMIN_PERMS, org)
    #Organization.objects.get
    if request.method == 'POST':
        if request.POST.get("type") == "change_verification":
            if comm.is_verified==True:
                comm.is_verified=False
            else:
                comm.is_verified=True
            comm.save()

        if request.POST.get("type") == "message":
            message_form = MessageForm(request.POST)
            if message_form.is_valid():
                convo_id = send_message(request.user, comm,  request.POST.get('profile'), request.POST.get('text'))
                return HttpResponseRedirect("/home/inbox/" + str(convo_id))

        elif request.POST.get("type") == "delete_post":
            post = Post.objects.get(pk=request.POST.get("post_id"))
            post.delete()

        elif request.POST.get("type") == "comment":
            post_form = PostForm(request.POST)
            if post_form.is_valid():
                feed_post = Post.objects.get(pk=request.POST.get('feed_post'))
                post = Post.create(request.user, feed_post, request.POST.get('text'))
                post.save()

        elif request.POST.get("type") == "post":
            post_form = PostForm(request.POST)
            if post_form.is_valid():
                post = Post.create(request.user, comm, request.POST.get('text'))
                post.save()

        elif request.POST.get("type") == "add_user":
            comm.members.add(request.user)
            request.user.set_perms(COMM_MEMBER_PERMS, comm)

        elif request.POST.get("type") == "upload_image":
            image_form = ImageForm(request.POST, request.FILES)
            if image_form.is_valid():
                image_file = request.FILES['image']
                image = Image.create(comm, image_file)
                image.save()

        elif request.POST.get("type") == "remove_image":
            image = Image.objects.get(pk=request.POST.get("image"))
            image.image.delete(save=True)
            image.delete()

        elif request.POST.get("type") == "remove":
            user = User.objects.get(username=request.POST.get("user"))
            if user != comm.comm_lead:
                comm.members.remove(user)
                user.revoke_all(comm)

        elif request.POST.get("type") == "swap_admin":
            for convo in comm.conversation_set.all():
                comm.comm_lead.revoke_all(convo)
            comm.comm_lead.set_perms(COMM_MEMBER_PERMS, comm)


            comm.comm_lead = User.objects.get(username=request.POST.get("user"))
            comm.save()
            comm.comm_lead.set_perms(COMM_LEAD_PERMS, comm)
            for convo in comm.conversation_set.all():
                comm.comm_lead.set_perms(['can_view'], convo)

        elif request.POST.get("type") == "remove_comm":
            comm.delete()
            return HttpResponseRedirect('/home/')

        elif request.POST.get("type") == "change_pref":
            mod_form = CommunityModForm(request.POST, request.FILES)

            if mod_form.is_valid():
                new_name = mod_form.cleaned_data['name']
                new_tagline = mod_form.cleaned_data['tagline']
                new_region = mod_form.cleaned_data['region']
                new_country = mod_form.cleaned_data['country']
                new_description = mod_form.cleaned_data['description']

                new_image = mod_form.cleaned_data['profile_image']

                if not new_name == comm.name:
                    if not Community.objects.filter(name=new_name).count():
                        comm.name = new_name
                        comm.profile_url = "/community/" + new_name +"/"

                if not new_tagline == comm.tagline:
                    comm.tagline = new_tagline
                if not new_region == comm.region :
                    comm.region = new_region
                if not new_country == comm.country:
                    comm.country = new_country
                if not new_description == comm.description:
                    comm.description = new_description

                if new_image is not None:
                    comm.profile_image.delete()
                    comm.profile_image = new_image

                comm.save()



        return HttpResponseRedirect(comm.profile_url)


    return render_to_response('community_profile.html', {'comm': comm,
                                                         'message_form':message_form,
                                                         'response': response,
                                                         'image_form':image_form,
                                                         'mod_form': mod_form,
                                                         'post_form':post_form,
                                                         'comm_lead': comm.comm_lead,
                                                         'admin_profiles': admin_profiles,
                                                         'members': comm.members.all()},
                              context_instance=RequestContext(request))