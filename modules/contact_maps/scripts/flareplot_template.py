import pandas as pd
from json import loads, dump
import sys

if len(sys.argv) == 1:
    print("""================flareplot_tepmlate.py=================

                python flareplot_template.py ITYPE

                Creates a GPCR flareplot json template for the 
                contact table with the specified ITYPE.

                """)

itype = sys.argv[1]

#Declaring dictionaries with types
basepath = "/GPCRmd/media/files/Precomputed/get_contacts_files/"
typelist =  {
    'sb' : 'salt bridge',
    "pc" : 'pi-cation',
    "ps" : 'pi-stacking',
    'ts' : 't-stacking',
    "vdw" : 'van der waals',
    'hp' : 'hydrophobic',
    "hbbb" : 'backbone to backbone HB',
    "hbsb" : 'sidechain to backbone HB',
    "hbss" : 'sidechain to sidechain HB',
    "hbls" : 'ligand to sidechain HB',
    "hblb" : 'ligand to backbone HB',
    "wb" : 'water bridge',
    "wb2" : 'extended water bridge',
    "hb" : 'hydrogen bonds',
    'all' : 'all types',
}
hb_itypes = {
    "hbbb" : 'backbone to backbone',
    "hbsb" : 'sidechain to backbone',
    "hbss" : 'sidechain to sidechain',
    "hbls" : 'ligand to sidechain',
    "hblb" : 'ligand to backbone',
}
other_itypes = {
    'hp' : 'hydrophobic',
    'sb' : 'salt bridge',
    "pc" : 'pi-cation',
    "ps" : 'pi-stacking',
    'ts' : 't-stacking',
    "vdw" : 'van der waals',
    "wb" : 'water bridge',
    "wb2" : 'extended water bridge',

}

itypes_order = [
    ("Non-polar", 
        (
            ("vdw","van der waals"),
            ('hp', "hydrophobic")
        )
    ),
    ("Polar/Electrostatic", 
        (
            ("hb", "hydrogen bond"),
            ("wb", "water bridge"),
            ("wb2", "extended water bridge"),
            ('sb', "salt bridge"),
            ("pc", "pi-cation")
        )
    ),
    ("Stacking",
        (
            ("ps", "pi-stacking"),
            ('ts', "t-stacking")
        )
    )
]

# Creating set_itypes, with all in case it is not still in it
if itype == "all":
    set_itypes =  set(("sb", "pc", "ps", "ts", "vdw", "hp", "hb", "hbbb", "hbsb", "hbss", "wb", "wb2", "hbls", "hblb", "all"))
else: 
    set_itypes = set(itype.split("_"))
    set_itypes.add('all')

#Loading files
df = pd.read_csv(str(basepath + "contact_tables/compare_all.tsv"), sep="\s+")
for itype_df in set_itypes:
    if itype_df == "all": 
        continue
    df_itype = pd.read_csv(str(basepath + "contact_tables/compare_" + itype_df + ".tsv"), sep="\s+")
    df = pd.concat([df, df_itype])

# Passing frequencies from decimal to percentage
nocols = (("Position1","Position2","itype","Position"))
for colname in df:
    if colname not in nocols:
        df[colname] = df[[colname]].apply(lambda x: x*100)

#'track' entry for json file
helix_colors = {'1':"#78C5D5",'12':"#5FB0BF",'2':"#459BA8",'23':"#5FAF88",'3':"#79C268",'34':"#9FCD58",'4':"#C5D747",'45':"#DDD742",'5':"#F5D63D",'56':"#F3B138",'6':"#F18C32",'67':"#ED7A6A",'7':"#E868A1",'78':"#D466A4",'8':"#BF63A6",'Ligand--1':'#FF5050', 'Ligand': '#FF5050'}        
allpos = set(df['Position1']).union(set(df['Position2']))
tracks = [{
    'trackLabel': 'Degree centrality',
    "trackProperties": []
}]
trees = [{
    'treeLabel': 'Helices',
    'treePaths': []
}]

for pos in allpos:
    helix = pos.split('x')[0]
    color = helix_colors[helix]
    trackprop = {
        'color' : color,
        'size' : 1.0,
        'nodeName': pos
    }
    tracks[0]['trackProperties'].append(trackprop)

    if str(pos).startswith('Ligand'):
        trees[0]['treePaths'].append([1, pos])
    elif len(helix) == 2:
        newhelix = int(helix[0]) + int(helix[1])
        trees[0]['treePaths'].append([newhelix, pos])
    else:
        newhelix = int(helix)*2
        trees[0]['treePaths'].append([newhelix, pos])

#Sort trees
treePaths_sorted = sorted(trees[0]['treePaths'], key=lambda l: (l[0],l[1]))
treePaths_sorted = [ str(x[0])+"."+x[1] for x in treePaths_sorted ]
trees[0]['treePaths'] = treePaths_sorted

#Output jsondict to store
jsondict = { 'trees' : trees, 'tracks' : tracks }


jsonpath = basepath + "../flare_plot/contact_maps/template.json"
with open(jsonpath, 'w') as jsonfile:
    dump(jsondict, jsonfile, ensure_ascii=False, indent = 4)