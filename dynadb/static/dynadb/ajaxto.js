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
                    linkresult=linkresult+'<li> <a href=/dynadb/compound/id/'+data.compound[i][0]+'> Compound: '+data.compound[i][1]+'<br><img src="'+data.compound[i][3]+'"  height="170" width="170"/></a>   <button class="compound" value="ligand" type="button" name='+data.compound[i][0]+' >Add to complex search</button><br></li>';
                }
                for(i=0; i<data.protein.length; i++){
                    linkresult=linkresult+'<li>   <a href=/dynadb/protein/id/'+data.protein[i][0]+'> Protein: '+data.protein[i][1]+'</a>   <button class="protein" type="button" value="receptor" name='+data.protein[i][0]+' >Add to complex search</button><br></li>';
                }
                for(i=0; i<data.molecule.length; i++){
                    linkresult=linkresult+'<li>  <a href=/dynadb/molecule/id/'+data.molecule[i][0]+'> Molecule: '+data.molecule[i][3]+'<br><img src="'+data.molecule[i][2]+'"  height="170" width="170"/></a>   <button class="molecule" type="button" value="ligand" name='+data.molecule[i][0]+' >Add to complex search</button><br></li>';
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
