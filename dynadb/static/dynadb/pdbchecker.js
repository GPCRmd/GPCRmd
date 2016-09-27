$(document).ready(function() {

    $('#pdbchecker').click(function(){
      console.log('am i called');
        $.ajax({
            type: "POST",
            url: "/dynadb/ajax_pdbchecker/",
            dataType: "json",
            data: { "chain": $("#id_chain").val(), "segid": $("#id_segid").val() , "restart": $("#id_resid_from").val() , "restop": $("#id_resid_to").val() },
            success: function(data) {
                if (data.error!=''){
                    newwindow=window.open('/dynadb/ajax_pdbchecker/','{{title}}','height=500,width=700');
                    if (window.focus) {newwindow.focus()}
                }else{
                    alert(data.message);
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                alert("some error");
            }
        });

    });



    // CSRF code
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


});

