from django import template
import json

register = template.Library()

@register.filter(name='firstchar')
def firstchar(value):
    print("\n\n",value)
    return value[0]

@register.filter(name='lower')
def lower(value): # Only one argument.
    """Converts a string into all lowercase"""
    return value.lower()


@register.filter(name='get_item')
def get_item(dictionary, key):
    if type(dictionary)==dict:
        return dictionary.get(key)
    else:
        return None


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


@register.filter(name='tunnel_color_from_clusternum')
def tunnel_color_from_clusternum(cluster_num):
    tun_color_li=["#0080ff","#009900","#ff0000" ,"#00ffff","#ffff00","#ff00ff","#ffa500","#d2b48c","#ffc0cb","#990099","#00ff00","#b784a7",'#ADB57B', '#16BF33', '#1DE1DF', '#A30E0A', '#94EF24', '#01296D', '#E46EA6', '#41B664', '#A4CDD8', '#3682AA', '#C107E4', '#C7A5AA', '#CB3851', '#6C6010', '#BB8298', '#25A811', '#8EAAAE', '#F355DB']
    if  cluster_num>=len(tun_color_li):
        color_num=cluster_num % len(tun_color_li);
    else:
        color_num=cluster_num
    color_code=tun_color_li[color_num];
    return color_code


@register.filter(name='sort_dict_by_key_pos')
def sort_dict_by_key_pos(dictionary):
    return sorted(dictionary.items(),key=lambda x:(x[0].split(":")[1], int(x[0].split(":")[0])  ))
    #return sorted(dictionary.items(),key=lambda x:x[0])

@register.filter(name='split_by')
def split_by(mystr, splitby):
    return mystr.split(splitby)


@register.filter
def replace(value, arg):
    """
    Replacing filter
    Use `{{ "aaa"|replace:"a|b" }}`
    """
    if len(arg.split('|')) != 2:
        return value

    what, to = arg.split('|')
    return value.replace(what, to)


@register.filter
def to_lowercase(mystr):
    if type(mystr) == str:
        return mystr.lower()
    else:
        return mystr