#!/usr/bin/bash

# Example script for generating contact information. 

pymol -c -d 'fetch 1crn, async=0; h_add; save 1crn_h.pdb'
rm -f 1crn.cif
python3 ../get_static_contacts.py --structure 1crn_h.pdb --itypes all --output 1crn_all-contacts.tsv
