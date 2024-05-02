from django import template
from django.conf import settings

register = template.Library()

@register.filter(name='retkey')
def retkey(value, arg):
    return value[int(arg)]


@register.filter(name='limitlength')
def limitlength(value,maxlen): 
    try:
        if len(value) > maxlen:
            fullhtml='<span data-toggle="tooltip" title="%s">%s...<span>' % (value,value[:(maxlen-2)])
            return fullhtml
        else:
            return value
    except:
        return maxlen
    
@register.filter(name='list_item')
def list_item(lst, i):
    try:
        return lst[i]
    except:
        return None