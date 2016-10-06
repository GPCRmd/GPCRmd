from django import template
from django.conf import settings

register = template.Library()

@register.filter(name='retkey')
def retkey(value, arg):
    return value[int(arg)]
