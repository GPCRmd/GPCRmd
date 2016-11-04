from dynadb.models import  Residue, Protein, DyndbModel, DyndbModeledResidues, DyndbProteinSequence, DyndbProtein, DyndbProteinMutations
import re 


def modify_helix_num(seq_num, aa, num, helix_pos, exp, exp2, rel_to_50):
    """When the gpcr numeration is a combination of sequence-based (BW) and structure-based, in case of insertion or deletion the numeration of the residues between the in/del and the beginning or end of the sequence change (depending if the in/del has occurred before or after the conserved residue (50)) changes. For this use, this function takes a "bw x gpcr" number and adds or substracts 1 to the bw part."""
    if num:
        (bw_p, gpcr_p)=exp.split(num)
        (helix, bw_rel_p)=exp2.split(bw_p)
        if helix == helix_pos:
            if rel_to_50 =="minus":
                new_bw_rel_p = (int(bw_rel_p)-1)
            else:
                new_bw_rel_p = (int(bw_rel_p)+1)
            new_gpcr_n = helix + "."+ str(new_bw_rel_p)+"x"+gpcr_p
            i=seq_num.index((aa,num))
            seq_num[i]=(aa,new_gpcr_n)


def gpcr_num_insertion(gpcr_n):
    """Adds the +1 to the GPCR generic num when there is an insertion. 
    Takes into account that the position previous to the insertion may also be an insertion"""
    exp=re.compile("x")
    (bw, gpcr)=exp.split(gpcr_n)
    if len(gpcr) > 2:
        new_gpcr= gpcr[:2]+str(int(gpcr[2]) +1)
        final_num = bw + "x" + new_gpcr 
    else:
        final_num=gpcr_n+"1"
    return final_num


def obtain_gen_numbering(dyn_id):
    """Given the id of the table dyndb_dynamics, obtains the generic numbering of the associated protein and returns a dict of residue position-generic number plus the name of the used numbering scheme/method and the sequence of the protein."""
    mod_res_li=DyndbModeledResidues.objects.filter(id_model__dyndbdynamics=dyn_id)
    dprot_id_set=set([e.id_protein for e in mod_res_li]) #I have to pass through the dyndb_modeled_residues table because for the moment the id_protein field of the table dyndb_model is empty, but otherwise we could pass directly from dyndb_model to dyndb_protein, and we wouldn't need the if-else.
    if len(dprot_id_set) == 1:
        dprot_id=list(dprot_id_set)[0]
        #dprot_id = 2 # PROVA: aquesta està mutada - BORRAR AIXÒ
        uniprot_id=DyndbProtein.objects.get(id=dprot_id).uniprotkbac
        prot_id=Protein.objects.get(accession=uniprot_id).id
        # Now, from the prot id, obtain the generic numbering. In the case of mutated prots, this will be modified
        rs = Residue.objects.prefetch_related('display_generic_number', 'protein_segment').filter(protein_conformation__protein=prot_id)
        sorted_rs=sorted(rs, key=lambda r: r.sequence_number)
        seq_num=[]
        for r in sorted_rs:
            if r.display_generic_number:
                t = (r.amino_acid, r.display_generic_number.label)
                seq_num.append(t)
            else:
                t=(r.amino_acid, None)
                seq_num.append(t)
        num_scheme=Protein.objects.get(pk=prot_id).residue_numbering_scheme.slug
        if DyndbProtein.objects.get(id=dprot_id).is_mutated:
            mutations=DyndbProteinMutations.objects.filter(id_protein=dprot_id)
            for mut in sorted(mutations, key=lambda m: m.id):
                res_position =mut.resid #rememper that in the sequence, the position is res -1
                res_from = mut.resletter_from
                res_to =  mut.resletter_to

                #### Testing - REMOVE THIS

                #res_position =48
                #res_from = "-"
                #res_to =  "!"

                ##########################

                if res_from == "-": # Would this work for double insertions?
                    gpcr_n = seq_num[res_position -2][1] 
                    if gpcr_n is None: # If it's None it means that it's outside of the helixes
                        seq_num.insert(res_position -1, (res_to, None))
                    else:
                        if "gpcr" in num_scheme: 
                            if "." in gpcr_n: #Format n.nn x nn
                                final_num= gpcr_num_insertion(gpcr_n)
                                seq_num.insert(res_position -1 , (res_to, final_num))
                                #Now we need to modify the rest of bw num of the helix
                                exp=re.compile("x")
                                (bw, gpcr)=exp.split(gpcr_n)
                                exp2=re.compile("\.")
                                (helix_pos, bw_pos) = exp2.split(bw)
                                if int(bw_pos) < 50:
                                    for (aa, num) in seq_num[:res_position-1]:
                                        modify_helix_num(seq_num, aa, num, helix_pos, exp, exp2, "minus")
                                else:
                                    for (aa, num) in seq_num[res_position-1:]:
                                        modify_helix_num(seq_num, aa, num, helix_pos, exp, exp2, "plus") 
                            else: #Format nxnn
                                final_num= gpcr_num_insertion(gpcr_n)
                                seq_num.insert(res_position -1 , (res_to, final_num))

                        else:
                            error = "Error: GPCR generic numbering cannot be used."
                            return error                                
                            # continue with other num systems?? I could do it with ballesteros!
                  
                elif res_to == "-": # Would this work for double deletions?
                    if "gpcr" in num_scheme:
                        gpcr_n = seq_num[res_position -1][1]
                        if gpcr_n is None or "." not in gpcr_n: # If it's not in an helix or the numbering doesn't include the BW
                            del seq_num[res_position -1]
                        else:
                            exp=re.compile("x")
                            (bw, gpcr)=exp.split(gpcr_n)
                            exp2=re.compile("\.")
                            (helix_pos, bw_pos) = exp2.split(bw)
                            if int(bw_pos) < 50:
                                for (aa, num) in seq_num[:res_position-1]:
                                    modify_helix_num(seq_num, aa, num, helix_pos, exp, exp2, "plus")
                            else:
                                for (aa, num) in seq_num[res_position:]:
                                    modify_helix_num(seq_num, aa, num, helix_pos, exp, exp2, "minus")
                            del seq_num[res_position -1]
                    else:
                        error = "Error: GPCR generic numbering cannot be used."
                        return error                              
                        # continue with other num systems?? I could do it with ballesteros!

                else: #SNP - Does not affect GPCR num
                    gpcr_n = seq_num[res_position -1][1] 
                    seq_num[res_position -1] = (res_to, gpcr_n)

        numbers_final = {}
        seq_final=""
        i=1
        for e in seq_num:
            numbers_final[i] = e
            seq_final += e[0]
            i+=1
        seq_db= DyndbProteinSequence.objects.get(id_protein=dprot_id).sequence
        if seq_final == seq_db:
            return (numbers_final, num_scheme, seq_db)
        else:
            error = "Error: GPCR generic numbering cannot be used."
            return error
    else:
        error = "Error: GPCR generic numbering cannot be used."
        return error
