from django import template
from django.template.defaultfilters import stringfilter
from ..models import Role

register = template.Library()

@register.filter
@stringfilter
def has_role(user, role_name):
    return user.profile.roles.filter(name=role_name).exists()

@register.filter
def is_student(user):
    return user.profile.roles.filter(name='student').exists()

@register.filter
def is_admin(user):
    return user.profile.roles.filter(name='admin').exists()

@register.filter
def is_guest(user):
    return user.profile.roles.filter(name='guest').exists() 