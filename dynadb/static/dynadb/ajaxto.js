//MAIN SEARCHER, sends ajax call to auto_query function. Returns: link to result + Add to table button
$("#Searcher").click(function() {
    var p=$("#protein22").val();
    $.ajax({
        type: "POST",
        data: { cmolecule: p},
        url: "/dynadb/ajaxsearch/",
        dataType: "json",
        success: function(data) {
            $("#Searcher").prop("disabled",false);
            if (data.message==''){
                var linkresult='';
                for(i=0; i<data.compound.length; i++){
                    linkresult=linkresult+'<a href=/dynadb/compound/id/'+data.compound[i]+'> Compound'+data.compound[i]+'</a> <button class="compound" type="button" name='+data.compound[i]+' >Add to complex search</button><br>';
                }
                for(i=0; i<data.protein.length; i++){
                    linkresult=linkresult+'<a href=/dynadb/protein/id/'+data.protein[i]+'> Protein:'+data.protein[i]+'</a> <button class="protein" type="button" name='+data.protein[i]+' >Add to complex search</button><br>';
                }
                for(i=0; i<data.molecule.length; i++){
                    linkresult=linkresult+'<a href=/dynadb/molecule/id/'+data.molecule[i]+'> Molecule:'+data.molecule[i]+'</a> <button class="molecule" type="button" name='+data.molecule[i]+' >Add to complex search</button><br>';
                }
                $('#ajaxresults').html(linkresult);
            }else{
                alert(data.message);
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            $("#Searcher").prop("disabled",false);
            alert("Something unexpected happen.");
        },
    });
});


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
