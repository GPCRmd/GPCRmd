
function searchtop() {
    var bigarray=[];
    $("#pElement1 tr").each(function () {
        var postarray=[];
        $('td', this).each(function () {
            var value = $(this).find(":input").val();
            postarray.push(value);
        })
        bigarray.push(postarray);
    })

    $.ajax({
        type: "POST",
        data: { "bigarray[]": bigarray,"url": window.location.href},
        url: "/dynadb/search_top/",
        dataType: "json",
        success: function(data) {
            $("#pdbchecker1").prop("disabled",false);
            if (data.message==''){
                trcount=0;
                $("#pElement1 tr").each(function () {
                    tdcount=0;
                    $('td', this).each(function () {
                        if (tdcount==5){
                            $(this).find(":input").val(data[trcount][0]);
                        }else if(tdcount==6){
                            $(this).find(":input").val(data[trcount][1]);
                        }
                        tdcount=tdcount+1;  
                    })
                 trcount=trcount+1;
                 })
            }else{
                alert(data.message);
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            $("#pdbchecker1").prop("disabled",false);
                alert('Error ocurred: PDB file numbering is corrupted (50,51,32); or resid interval is too short.');
        }
    });
}


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