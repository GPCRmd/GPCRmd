from dynadb.models import  Residue, Protein, DyndbModel, DyndbModeledResidues, DyndbProteinSequence, DyndbProtein, DyndbProteinMutations, ResidueGenericNumber
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




def obtain_gpcr_num_alt(alt_class,res_gpcr_li,rgn_ids):
    """Creates a list where each element corresponds to an AA of the seq and the generic GPCR number of that position. Uses the numbering of the class specified at the argiments"""
    alt_scheme="gpcrdb"+ alt_class.lower()
    alt_rgn=ResidueGenericNumber.objects.filter(residuealternativegenericnumbers__residue_id__in=rgn_ids, scheme_id__slug=alt_scheme)
    alt_res_gpcr_li=res_gpcr_li.copy()
    res_gpcr_n=0
    rgn_n=0
    if alt_rgn:
        if len(alt_rgn)==len(rgn_ids):
            while res_gpcr_n<len(alt_res_gpcr_li):
                if alt_res_gpcr_li[res_gpcr_n][1]:
                    (res, gpcr_old)=alt_res_gpcr_li[res_gpcr_n]
                    alt_res_gpcr_li[res_gpcr_n]=(res,alt_rgn[rgn_n].label)
                    rgn_n+=1
                res_gpcr_n+=1
            return alt_res_gpcr_li
    return False


def obtain_gpcr_num_of_cannonical(num_scheme,sorted_rs,gpcr_class):
    """Creates a list where each element corresponds to an AA of the seq and the generic GPCR number of that position. If the numbering scheme is not a GPCR generic numbering, obtains the numeration in that system."""
    seq_num=[]
    rgn_ids=[]
    for r in sorted_rs:
        if r.display_generic_number:
            t = (r.amino_acid, r.display_generic_number.label)
            seq_num.append(t)
            rgn_ids.append(r.id)
        else:
            t=(r.amino_acid, None)
            seq_num.append(t)
    if "gpcr" not in num_scheme: 
        seq_num=obtain_gpcr_num_alt(gpcr_class,seq_num,rgn_ids)
        num_scheme="gpcrdb"+ gpcr_class.lower()
    return(seq_num, num_scheme, rgn_ids)





def obtain_gen_numbering(dyn_id, dprot_gpcr, gprot_gpcr):
    """Given the id of the table dyndb_dynamics, obtains the generic numbering of the associated protein and returns a dict of residue position-generic number for all the GPCR classes plus the name of the used numbering scheme/method, the sequence of the protein and the GPCR class (A, B, C or F)."""
    dprot_id = dprot_gpcr.id  #[!] UNCOMMENT
    prot_id = gprot_gpcr.id  #[!] UNCOMMENT
    #prot_id="935"   #[!] REMOVE
    #dprot_id=1  #[!] REMOVE

    num_scheme_obj=Protein.objects.get(pk=prot_id).residue_numbering_scheme
    num_scheme=num_scheme_obj.slug
    num_scheme_name=num_scheme_obj.name
    gpcr_class_pre=re.search("Class ([ABCF])", num_scheme_name)
    if gpcr_class_pre:
        gpcr_class=gpcr_class_pre.group(1)
    else:
        print(1)
        error = "Error: GPCR generic numbering cannot be used."
        seq_db= DyndbProteinSequence.objects.get(id_protein=dprot_id).sequence
        return (error , seq_db)
    # Now, from the prot id, obtain the generic numbering. In the case of mutated prots, this will be modified
    rs = Residue.objects.prefetch_related('display_generic_number', 'protein_segment').filter(protein_conformation__protein=prot_id)
    sorted_rs=sorted(rs, key=lambda r: r.sequence_number)
    (res_gpcr_li, num_scheme,  rgn_ids)=obtain_gpcr_num_of_cannonical(num_scheme,sorted_rs,gpcr_class) 
    if not res_gpcr_li:
        seq_db= DyndbProteinSequence.objects.get(id_protein=dprot_id).sequence
        return ("Error: GPCR generic numbering cannot be used.",seq_db)
    all_num_schemes={}
    all_num_schemes[gpcr_class]=res_gpcr_li
    other_classes=list({"A","B","C","F"} - set(gpcr_class))
    for alt_class in other_classes: 
        all_num_schemes[alt_class]=obtain_gpcr_num_alt(alt_class,res_gpcr_li,rgn_ids)
    if DyndbProtein.objects.get(id=dprot_id).is_mutated:
        mutations=DyndbProteinMutations.objects.filter(id_protein=dprot_id)
        mutations_s=sorted(mutations, key=lambda m: m.id)
        for seq_num in all_num_schemes.values():
            if seq_num:
                for mut in mutations_s:
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
                    elif res_to == "-": # Would this work for double deletions?
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
                    else: #SNP - Does not affect GPCR num
                        gpcr_n = seq_num[res_position -1][1] 
                        seq_num[res_position -1] = (res_to, gpcr_n)
    numbers_final = {"A":{},"B":{},"C":{},"F":{}}
    seq_final=""
    for gpcr_cl in all_num_schemes:
        i=1
        seq_num=all_num_schemes[gpcr_cl]
        if seq_num:
            for e in seq_num:
                if gpcr_cl==gpcr_class:
                    seq_final += e[0]
                numbers_final[gpcr_cl][i]=e
                i+=1
        else:
            numbers_final[gpcr_cl]=False

    seq_db= DyndbProteinSequence.objects.get(id_protein=dprot_id).sequence 
    #return (numbers_final, num_scheme, seq_final, gpcr_class) ################# [!] TEST : BORRAR!!!!!!!!!
    if seq_final == seq_db:
        return (numbers_final, num_scheme, seq_db, gpcr_class)
    else:
        error = "Error: GPCR generic numbering cannot be used."
        return (error, seq_db)
#    else:
#        error = "Error: GPCR generic numbering cannot be used."
#        return (error,False)
