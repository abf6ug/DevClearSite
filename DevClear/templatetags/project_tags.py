__author__ = 'austi_000'

from django import template
from django.contrib.auth.models import User
from object_permissions import get_user_perms
from DevClear.models import Project

register = template.Library()

@register.assignment_tag()
def has_perm(user, perm, proj):
    return perm in get_user_perms(user, proj)

