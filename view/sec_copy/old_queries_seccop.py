
### From prot_id
#===============
    prot_id = 1 #This may be passed by post
    f=DyndbFiles.objects.get(pk=prot_id).filepath
###
    rs = Residue.objects.prefetch_related('display_generic_number', 'protein_segment').filter(protein_conformation__protein=prot_id)
    numbers = {}
    for r in rs:
        if r.display_generic_number:
            numbers[r.sequence_number] = r.display_generic_number.label
    num_scheme=Protein.objects.get(pk=prot_id).residue_numbering_scheme.name


