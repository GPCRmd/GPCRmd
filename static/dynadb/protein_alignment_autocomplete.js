//When "Align" button is clicked in the Protein step of the submission process, the sequence from the cannonical Uniprot protein and the mutant sequence of a given protein are extracted and an aligning function is called, which performs a sequence alignment between the two sequences. The alignment fills the alignment box of the protein and a pop up with a visually esthetic alignment appears.


$('body').on('click', "[id$=get_align]", function(){ //react to clicked elements with id ending in get_mutations (a button)
	var id_present_button=$(this).attr('id');  //get its full ID
    if (id_present_button.indexOf("-") >= 0) { //check if it is the only one or there are more. The hyphen tells.
	    var regex=/(id_form-)([0-9]+)-get_align/;
	    var show=id_present_button.replace(regex,"$1$2-alignment");
        show='#'+show;
	    var mutant_sequence=id_present_button.replace(regex,"$1$2-msequence");
	    var uniprot_sequence=id_present_button.replace(regex,"$1$2-sequence");
	    uniprot_sequence=$('#'+uniprot_sequence).val();
	    mutant_sequence=$('#'+mutant_sequence).val();
    }else{
        var uniprot_sequence=$('#id_sequence').val();
	    var mutant_sequence=$('#id_msequence').val();
        var show='#id_alignment';
    }
	$.ajax({
	    type: "POST",
	    data: { "wtseq":uniprot_sequence,"mutant":mutant_sequence},
	    url: "./alignment/",
	    dataType: "json",
	    success: function(data) {
	         if (data.message==''){
	             $(show).val(data.alignment);
                 newwindow=window.open('./alignment/','','height=500,width=700');
                 if (window.focus) {newwindow.focus()}
	         }else{
	             alert(data.message);
	         }
	    },
	    error: function(XMLHttpRequest, textStatus, errorThrown) {
	        alert("Something unexpected happen.");
	    }
	});
}); //click binded function end
//});

function getCookie(name) {
    var cookieValue = null;
    var i = 0;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (i; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
}); 
