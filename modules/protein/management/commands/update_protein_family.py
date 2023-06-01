import requests
import pandas as pd
import io
from os import path 
import sys
import re

from modules.protein.models import ProteinFamily
from django.core.management.base import BaseCommand, CommandError
from config.settings import MODULES_ROOT

class Command(BaseCommand):
    help = "Get protein family information from GPCRdb and update the table on GPCRmd database."
    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            dest='update',
            default=False,
            help='Overwrites already stored data on ../modules/protein/management/tools/prot_fam_data.py',
        )

    def handle(self, *args, **kwargs):

        from modules.protein.management.tools.prot_fam_data import prot_fam_dic

        #Get data from GPCRdb services
        url = "http://gpcrdb.org/services/proteinfamily/"
        urlData = requests.get(url).json()
        html_cleaner = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')#Clean tags and some not enclosed elements like &nsbm  
        l_errors = {} #Store possible errors & warnings to display them at the end

        if kwargs['update'] or prot_fam_dic == {}: 
            print("- UPDATE FILES STEP...")
            if prot_fam_dic == {}:
                print("     > Dictionary of families on prot_fam_data,py not found... Refreshing data...")
            else:
                print("     > Refreshing data...")

            #Read information & generate diccionary of information
            prot_fam_dic = {}
            for pfdata in urlData: # {'slug': '100_001_005', 'name': 'GPa1 family', 'parent': {'slug': '100_001', 'name': 'Alpha'}}
                slug = pfdata["slug"]
                name = re.sub(html_cleaner, '', pfdata["name"])
                try:
                    slugparent = pfdata["parent"]["slug"]
                except TypeError:
                    print (f"        > Family {name} do not have parent...")
                    if "parent_nf" not in l_errors.keys():                        
                        l_errors['parent_nf'] = [name]
                    else:
                        l_errors['parent_nf'].append(name)
                    slugparent = "-"
                prot_fam_dic[slug] = {"name": name, "slug_parent": slugparent}

            # Write information into data.py file on dynadb main directory
            print("     > Writing info into ../modules/protein/management/tools/prot_fam_data.py...")
            dic_prot_fam_file = open(mode="w", file=f"{MODULES_ROOT}/protein/management/tools/prot_fam_data.py")
            dic_prot_fam_file.write("# This information is to update the families protein table of GPCRmd database.\n")
            dic_prot_fam_file.write(f"prot_fam_dic={prot_fam_dic}")
            dic_prot_fam_file.close()
        
        # Read information from table ProteinFamily     
       
        print("- READING STEP...")
        print("     > Reading table ProteinFamily from database...")
        data_protfam = ProteinFamily.objects.all() # slug, name, parent        

        # Update table ProteinFamily
        print("- UPDATE STEP...")
        print("     > Update table ProteinFamily...")

        for f in data_protfam:
            ref_slug = f.slug
            if ref_slug in prot_fam_dic.keys():
                name = prot_fam_dic[ref_slug]["name"]
            else:
                print(f"        - Family with slug {ref_slug} not found on GPCRdb...")
                if "family_nf" not in l_errors.keys():                        
                    l_errors['family_nf'] = [f"{name}:{ref_slug}"]
                else:
                    l_errors['family_nf'].append(f"{name}:{ref_slug}")
                name = re.sub(html_cleaner, '', f.name)
            query = ProteinFamily.objects.filter(slug=ref_slug)
            query.update(name=name)
        
        # Add new entries to ProteinFamily
        print("     > Search of new entries for table ProteinFamily...")
        slug_protfam = list(ProteinFamily.objects.values_list("slug",flat=True))     
        for key in prot_fam_dic.keys():
            if key not in slug_protfam:
                print(f"        - New family {key} found on GPCRdb...")
                slug = key
                name = prot_fam_dic[slug]["name"]
                slug_parent = prot_fam_dic[slug]["slug_parent"]
                # Get slug_parent id from ProteinFamily
                try:
                    s_par = ProteinFamily.objects.get(slug=slug_parent)
                    s_par_id = s_par.id
                except Exception as e:
                    print(f"        - Error on new family with slug {slug}...")
                    if "family_new" not in l_errors.keys():                        
                        l_errors['family_new'] = [f"{name}:{slug}"]
                    else:
                        l_errors['family_new'].append(f"{name}:{slug}")
                    s_par_id = None
                query = ProteinFamily(slug = slug, name = name, parent_id = s_par_id)
                query.save()
            else:
                continue

        # Errors
        if l_errors != {}:
            print("- ERRORS & WARNINGS...")
        if "parent_nf" in l_errors.keys():                        
            print("     > List of families without parents:")
            print(f"    {l_errors['parent_nf']}")
        if "family_nf" in l_errors.keys():                        
            print("     > List of families not founded on GPCRdb:")
            print(f"    {l_errors['family_nf']}")
        if "family_new" in l_errors.keys():                        
            print("     > List of new families not added:")
            print(f"    {l_errors['family_new']}")


        
