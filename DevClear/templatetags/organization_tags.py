__author__ = 'austi_000'

from django import template
from django.contrib.auth.models import User
from object_permissions import get_user_perms
from DevClear.models import Organization

register = template.Library()

@register.assignment_tag()
def has_perm(user, perm, org):
    return perm in get_user_perms(user, org)

@register.simple_tag()
def list(user, perm, org):
    return perm in get_user_perms(user, org)