from django.shortcuts import render
from django.conf import settings

from common.views import AbsReferenceSelection
from common.views import AbsSegmentSelection
from common.views import AbsTargetSelection
# from common.alignment_SITE_NAME import Alignment
Alignment = getattr(__import__('common.alignment_' + settings.SITE_NAME, fromlist=['Alignment']), 'Alignment')

from collections import OrderedDict


class ReferenceSelection(AbsReferenceSelection):
    step = 1
    number_of_steps = 3
    target_input = False
    docs = 'sequences.html#similarity-search-gpcrdb'
    buttons = {
        'continue': {
            'label': 'Continue to next step',
            'url': '/similaritysearch/segmentselection',
            'color': 'success',
        },
    }


class SegmentSelection(AbsSegmentSelection):
    step = 2
    number_of_steps = 3
    docs = 'sequences.html#similarity-search-gpcrdb'
    selection_boxes = OrderedDict([
        ('reference', True),
        ('segments', True),
        ('targets', False),
    ])
    buttons = {
        'continue': {
            'label': 'Continue to next step',
            'url': '/similaritysearch/targetselection',
            'color': 'success',
        },
    }


class TargetSelection(AbsTargetSelection):
    step = 3
    number_of_steps = 3
    docs = 'sequences.html#similarity-search-gpcrdb'
    selection_boxes = OrderedDict([
        ('reference', True),
        ('segments', True),
        ('targets', True),
    ])
    buttons = {
        'continue': {
            'label': 'Show similarity',
            'url': '/similaritysearch/render',
            'color': 'success',
        },
    }

def render_alignment(request):
    # get the user selection from session
    simple_selection = request.session.get('selection', False)
    
    # create an alignment object
    a = Alignment()

    # load data from selection into the alignment
    a.load_reference_protein_from_selection(simple_selection)
    a.load_proteins_from_selection(simple_selection)
    a.load_segments_from_selection(simple_selection)

    # build the alignment data matrix
    a.build_alignment()

    # calculate consensus sequence + amino acid and feature frequency
    a.calculate_statistics()

    # calculate identity and similarity of each row compared to the reference
    a.calculate_similarity()

    num_of_sequences = len(a.proteins)
    num_residue_columns = len(a.positions) + len(a.segments)

    return render(request, 'similaritysearch/alignment.html', {'a': a, 'num_of_sequences': num_of_sequences,
        'num_residue_columns': num_residue_columns})

def render_fasta_alignment(request):
    # get the user selection from session
    simple_selection = request.session.get('selection', False)
    
    # create an alignment object
    a = Alignment()
    a.show_padding = False

    # load data from selection into the alignment
    a.load_reference_protein_from_selection(simple_selection)
    a.load_proteins_from_selection(simple_selection)
    a.load_segments_from_selection(simple_selection)

    # build the alignment data matrix
    a.build_alignment()

    # calculate identity and similarity of each row compared to the reference
    a.calculate_similarity()

    num_of_sequences = len(a.proteins)
    num_residue_columns = len(a.positions) + len(a.segments)
    
    response = render(request, 'alignment/alignment_fasta.html', {'a': a, 'num_of_sequences': num_of_sequences,
        'num_residue_columns': num_residue_columns}, content_type='text/fasta')
    response['Content-Disposition'] = "attachment; filename=" + settings.SITE_TITLE + "_alignment.fasta"
    return response

def render_csv_alignment(request):
    # get the user selection from session
    simple_selection = request.session.get('selection', False)
    
    # create an alignment object
    a = Alignment()
    a.show_padding = False

    # load data from selection into the alignment
    a.load_reference_protein_from_selection(simple_selection)
    a.load_proteins_from_selection(simple_selection)
    a.load_segments_from_selection(simple_selection)

    # build the alignment data matrix
    a.build_alignment()

    # calculate consensus sequence + amino acid and feature frequency
    a.calculate_statistics()

    # calculate identity and similarity of each row compared to the reference
    a.calculate_similarity()

    num_of_sequences = len(a.proteins)
    num_residue_columns = len(a.positions) + len(a.segments)
    
    response = render(request, 'alignment/alignment_csv.html', {'a': a, 'num_of_sequences': num_of_sequences,
        'num_residue_columns': num_residue_columns}, content_type='text/fasta')
    response['Content-Disposition'] = "attachment; filename=" + settings.SITE_TITLE + "_alignment.csv"
    return response
