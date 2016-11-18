from dynadb.models import  Residue, Protein, DyndbModel, DyndbModeledResidues, DyndbProteinSequence, DyndbProtein, DyndbProteinMutations

def obtain_gen_numbering(dyn_id):
    """Given the id of the table dyndb_dynamics, obtains the generic numbering of the associated protein and returns a dict of sequence number-generic number plus the name of the used numbering scheme/method"""
    model_id=DyndbModel.objects.get(dyndbdynamics=dyn_id).id
    mod_res_li=DyndbModeledResidues.objects.filter(id_model=model_id)
    dprot_id_set=set([e.id_protein for e in mod_res_li]) #I have to pass throuch the dyndb_modeled_residues table because for the moment the id_protein field of the table dyndb_model is empty, but otherwise we could pass directly from dyndb_model to dyndb_protein, and we wouldn't need the if-else.
    if len(dprot_id_set) == 1:
        dprot_id=list(dprot_id_set)[0]
        dprot_id = 2 # PROVA: aquesta està mutada - BORRAR AIXÒ
        uniprot_id=DyndbProtein.objects.get(id=dprot_id).uniprotkbac
        prot_id=Protein.objects.get(accession=uniprot_id).id
        # Now, from the prot id, obtain the generic numbering. In the case of mutated prots, this will be modified
        rs = Residue.objects.prefetch_related('display_generic_number', 'protein_segment').filter(protein_conformation__protein=prot_id)
        numbers = {}
        for r in rs:
            if r.display_generic_number:
                numbers[r.sequence_number] = r.display_generic_number.label
        num_scheme=Protein.objects.get(pk=prot_id).residue_numbering_scheme.name
        if DyndbProtein.objects.get(id=dprot_id).is_mutated:
            print("MUTATED")
            mutations=DyndbProteinMutations.objects.filter(id_protein=dprot_id)
            for mut in mutations:
                res_position =mut.resid #rememper that in the sequence, the position is res -1
                res_from = mut.resletter_from
                res_to =  mut.resletter_to
                if res_from == "-":
                    print("insertion")               
                    if num_scheme == "gpcrdb":
                  
                if res_to == "-":
                   print("deletion")               
                



             
             # Continue!!

        else: # If the prot don't have mutations (seq = canonical seq)            
            print("NOT MUTATED")
            numbers=numbers
        #return (numbers, num_scheme)

#
    else:
        pass #RAISE ERROR
