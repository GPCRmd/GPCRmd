from django import template
import json

register = template.Library()

@register.filter(name='list_to_str')
def list_to_str(value): # Only one argument.
    try:
        res=", ".join(value)
    except:
        res=value
    return res

@register.filter(name='list_to_str_break')
def list_to_str_break(value): # Only one argument.
    try:
        res=",<br>".join(value)
    except:
        res=value
    return res
    
@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='sort_dict_by_key')
def sort_dict_by_key(dictionary):
    return sorted(dictionary.items(),key=lambda x:x[0])

@register.filter(name='sort_lod_by_key')
def sort_lod_by_key(mylist,key):
    return sorted(mylist,key=lambda x:x[0])

@register.filter(name='json_dump')
def json_dump(myvar):
    if type(myvar)==dict:
        for k,v in myvar.items():
            if type(v)==dict:
                for kk,vv in v.items():
                    if type(vv)==set:
                        myvar[k][kk]=list(vv)
    return  json.dumps(myvar)


@register.filter(name='extract_all_isolates')
def extract_all_isolates(pos_variants):
    all_pos_iso=set()
    for myvar in pos_variants.values():
        all_pos_iso=all_pos_iso.union(myvar["isolate_id"])
    return all_pos_iso

@register.filter(name='addtostr')
def addtostr(cont_type, toadd):
    return cont_type+ toadd