$(document).ready(function() {
    $('#simpletype').children('option[value=complex]').attr('disabled', true);
    $('#simpletype').children('option[value=model]').attr('disabled', true);
    $('#simpletype').children('option[value=dynamics]').attr('disabled', true);

    $('#idsearch').on('change', function() {
        if ( $("#idsearch").prop('checked') ){
            $('#simpletype').children('option[value=complex]').attr('disabled', false);
            $('#simpletype').children('option[value=model]').attr('disabled', false);
            $('#simpletype').children('option[value=dynamics]').attr('disabled', false);
        } else {
            $('#simpletype').children('option[value=complex]').attr('disabled', true);
            $('#simpletype').children('option[value=model]').attr('disabled', true);
            $('#simpletype').children('option[value=dynamics]').attr('disabled', true);
        }
    });

});
