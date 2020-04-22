from django import template
import json

register = template.Library()

@register.filter(name='lower')
def lower(value): # Only one argument.
    """Converts a string into all lowercase"""
    return value.lower()


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='json_dump')
def json_dump(value):
    return  json.dumps(value)

@register.simple_tag(name='my_tag')
def get_tunnel_list(dod, key1, key2):
    res=None
    mydict=dod.get(key1)
    if mydict:
        res= mydict.get(key2)
    return res


