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
                res = data.result.split(",");
                var linkresult='';
                for (var id in res){
                    if (res[id]!=''){
                        var trueid=res[id].split('.')[2];
                        if (res[id].indexOf('moleculemolecule') !== -1){
                            linkresult=linkresult+'<a href=/dynadb/molecule/id/'+trueid+'>'+trueid+'</a> <button class="molecule" type="button" name='+trueid+' >Add to complex search</button><br>';

                        }else if (res[id].indexOf('protein') !== -1){
                             linkresult=linkresult+'<a href=/dynadb/protein/id/'+trueid+'>'+trueid+'</a> <button class="protein" type="button" name='+trueid+' >Add to complex search</button><br>';
                        }else{
                             console.log('COMPOUND FOUND, PRINT TABLE');  
                        }
                    }
                }
                $('#ajaxresults').html(linkresult);
            }else{
                alert(data.message);
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            $("#Searcher").prop("disabled",false);
            alert("Something unexpected happen.");
        }
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
