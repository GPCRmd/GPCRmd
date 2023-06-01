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
    if dictionary:        
        return dictionary.get(key)
    else: 
        return None

@register.filter(name='sort_dict_by_key')
def sort_dict_by_key(dictionary):
    return sorted(dictionary.items(),key=lambda x:x[0])

@register.filter(name='sort_lod_by_key')
def sort_lod_by_key(mylist,key):
    return sorted(mylist,key=lambda x:x[key])

@register.filter(name='sort_list')
def sort_list(mylist):
    if mylist:
        any_not_number=[e for e in mylist if not str(e).isnumeric()]
        if any_not_number:
            return sorted(mylist)
        else:
            return sorted(mylist,key=lambda x:float(x))
    else: 
        return mylist

@register.filter(name='json_dump')
def json_dump(myvar):
    if type(myvar)==dict:
        for k,v in myvar.items():
            if type(v)==dict:
                for kk,vv in v.items():
                    if type(vv)==set:
                        myvar[k][kk]=list(vv)
    return  json.dumps(myvar)

@register.filter(name='recursive_json_dump')
def recursive_json_dump(myvar):
    if type(myvar)==dict:
        for k,v in myvar.items():
            myvar[k]=recursive_json_dump(v)
    elif type(myvar)==set:
        myvar= list(myvar)
    return json.dumps(myvar)


@register.filter(name='extract_all_isolates')
def extract_all_isolates(pos_variants):
    all_pos_iso=set()
    for myvar in pos_variants.values():
        all_pos_iso=all_pos_iso.union(myvar["isolate_id"])
    return all_pos_iso

@register.filter(name='addtostr')
def addtostr(cont_type, toadd):
    return cont_type+ toadd


@register.filter(name='str_to_ref')
def str_to_ref(myvar):
    return myvar.replace(" ", "_")

@register.filter(name='create_finprot_tooltip_data')
def create_finprot_tooltip_data(prot_dict, prot_id):
    if prot_id in prot_dict:
        prot_data=prot_dict[prot_id]
        prot_name=prot_data["name"]
        numdyn=prot_data["numdyn"]
    else:
        if "nsp" in prot_id:
            prot_name=prot_id.replace("nsp","NSP")
        elif "orf" in prot_id:
            prot_name=prot_id.replace("orf","ORF")
        else:
            prot_name=prot_id.capitalize().replace("_"," ")
        numdyn=0
    tooltip="""
      <div style='text-align: left;margin:5px'>
        <p style='margin:2'><strong>%s</strong></p>
        <p style='margin:0'><strong># systems:</strong> %s</p>
      </div>
        """ % (prot_name,numdyn)
    return tooltip


@register.filter(name='toint')
def toint(myvar):
    try:
        return int(myvar)
    except:
        return myvar