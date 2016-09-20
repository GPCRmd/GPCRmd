from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.views import generic
from django.core.cache import cache
from django.views.decorators.cache import cache_page

from common.diagrams_gpcr import DrawHelixBox, DrawSnakePlot

from protein.models import Protein, ProteinFamily, ProteinSegment, ProteinConformation
from residue.models import Residue,ResidueGenericNumber
from mutation.models import MutationExperiment
from structure.models import Structure
from interaction.models import ResidueFragmentInteraction
Alignment = getattr(__import__('common.alignment_' + settings.SITE_NAME, fromlist=['Alignment']), 'Alignment')

import json

@cache_page(60 * 60 * 24)
def detail(request, slug):
    # get family
    pf = ProteinFamily.objects.get(slug=slug)

    # get family list
    ppf = pf
    families = [ppf.name]
    while ppf.parent.parent:
        families.append(ppf.parent.name)
        ppf = ppf.parent
    families.reverse()

    # number of proteins
    proteins = Protein.objects.filter(family__slug__startswith=pf.slug, sequence_type__slug='wt')
    no_of_proteins = proteins.count()
    no_of_human_proteins = Protein.objects.filter(family__slug__startswith=pf.slug, species__id=1,
        sequence_type__slug='wt').count()
    list_proteins = list(proteins.values_list('pk',flat=True))


    # get structures of this family
    structures = Structure.objects.filter(protein_conformation__protein__parent__family__slug__startswith=slug
        ).order_by('-representative', 'resolution').prefetch_related('pdb_code__web_resource')

    mutations = MutationExperiment.objects.filter(protein__in=proteins).prefetch_related('residue__generic_number',
                                'exp_qual', 'ligand')


    interactions = ResidueFragmentInteraction.objects.filter(
        structure_ligand_pair__structure__protein_conformation__protein__parent__in=proteins, structure_ligand_pair__annotated=True).exclude(interaction_type__type ='hidden').order_by('rotamer__residue__sequence_number')
    interaction_list = {}
    for interaction in interactions:
        if interaction.rotamer.residue.generic_number:
            gn = interaction.rotamer.residue.generic_number.label
            aa = interaction.rotamer.residue.amino_acid
            interactiontype = interaction.interaction_type.name
            if gn not in interaction_list:
                interaction_list[gn] = []
            interaction_list[gn].append([aa, interactiontype])

    mutations_list = {}
    for mutation in mutations:
        if not mutation.residue.generic_number: continue #cant map those without display numbers
        if mutation.residue.generic_number.label not in mutations_list: mutations_list[mutation.residue.generic_number.label] = []
        if mutation.ligand:
            ligand = mutation.ligand.name
        else:
            ligand = ''
        if mutation.exp_qual:
            qual = mutation.exp_qual.qual
        else:
            qual = ''
        mutations_list[mutation.residue.generic_number.label].append([mutation.foldchange,ligand.replace("'", "\\'"),qual])

    try:
        pc = ProteinConformation.objects.get(protein__family__slug=slug, protein__sequence_type__slug='consensus')
    except ProteinConformation.DoesNotExist:
        pc = ProteinConformation.objects.get(protein__family__slug=slug, protein__species_id=1,
            protein__sequence_type__slug='wt')

    residues = Residue.objects.filter(protein_conformation=pc).order_by('sequence_number').prefetch_related(
        'protein_segment', 'generic_number', 'display_generic_number')

    jsondata = {}
    jsondata_interaction = {}
    for r in residues:
        if r.generic_number:
            if r.generic_number.label in mutations_list:
                jsondata[r.sequence_number] = [mutations_list[r.generic_number.label]]
            if r.generic_number.label in interaction_list:
                jsondata_interaction[r.sequence_number] = interaction_list[r.generic_number.label]

    HelixBox = DrawHelixBox(residues,'Class A','family_diagram_preloaded_data')
    SnakePlot = DrawSnakePlot(residues,'Class A','family_diagram_preloaded_data') ## was str(list_proteins)

    # process residues and return them in chunks of 10
    # this is done for easier scaling on smaller screens
    chunk_size = 10
    r_chunks = []
    r_buffer = []
    last_segment = False
    border = False
    title_cell_skip = 0
    for i, r in enumerate(residues):
        # title of segment to be written out for the first residue in each segment
        segment_title = False

        # keep track of last residues segment (for marking borders)
        if r.protein_segment.slug != last_segment:
            last_segment = r.protein_segment.slug
            border = True

        # if on a border, is there room to write out the title? If not, write title in next chunk
        if i == 0 or (border and len(last_segment) <= (chunk_size - i % chunk_size)):
            segment_title = True
            border = False
            title_cell_skip += len(last_segment) # skip cells following title (which has colspan > 1)

        if i and i % chunk_size == 0:
            r_chunks.append(r_buffer)
            r_buffer = []

        r_buffer.append((r, segment_title, title_cell_skip))

        # update cell skip counter
        if title_cell_skip > 0:
            title_cell_skip -= 1
    if r_buffer:
        r_chunks.append(r_buffer)

    context = {'pf': pf, 'families': families, 'structures': structures, 'no_of_proteins': no_of_proteins,
        'no_of_human_proteins': no_of_human_proteins, 'HelixBox':HelixBox, 'SnakePlot':SnakePlot,
        'mutations':mutations, 'r_chunks': r_chunks, 'chunk_size': chunk_size, 'mutations_pos_list' : json.dumps(jsondata),'interaction_pos_list' : json.dumps(jsondata_interaction)}

    return render(request, 'family/family_detail.html', context)
