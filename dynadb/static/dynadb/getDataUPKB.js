
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
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
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready(function(){
    $(document).on('click',"[id='id_get_data_upkb'],[id|=id_form][id$='-get_data_upkb']",function(){
        var uniprotkbac_isoform;
	var protform = $(this).parents("[id|=protform]");
        var uniprotkbac = protform.find("[id='id_uniprotkbac'],[id|=id_form][id$='-uniprotkbac']");
	var uniprotkbacval = uniprotkbac.val();
        var isoform = protform.find("[id='id_isoform'],[id|=id_form][id$='-isoform']");
	var isoformval = isoform.val();
        if (isoformval == '') {
          uniprotkbac_isoform = uniprotkbacval;
        } else {
          uniprotkbac_isoform = uniprotkbacval + '-' + isoformval;
        }
	
	var sequence = protform.find("[id='id_sequence'],[id|=id_form][id$='-sequence']");
        var name = protform.find("[id='id_name'],[id|=id_form][id$='-name']");
        var aliases = protform.find("[id='id_other_names'],[id|=id_form][id$='-other_names']");
        name.val('Retriving...');
        aliases.text('Retriving...');
        sequence.text('Retriving...');
        
        $.post("get_data_upkb/",
        {
            uniprotkbac:uniprotkbac_isoform
        },
        function(data){
          uniprotkbac.val(data.Entry);
          isoform.val(data.Isoform)
	  name.val(data.Name);
          aliases.text(data.Aliases);
	  sequence.text(data.Sequence);
          
        }, 'json')

        .fail(function(xhr) {
           alert("Error "+ "\nStatus: " + xhr.status+"\n"+xhr.responseText);
           name.val('');
           aliases.text('');
           sequence.text('');
        })

    });
});
