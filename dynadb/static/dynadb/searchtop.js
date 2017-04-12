
function searchtop() {
    //works when autocomplete is clicked. fills the 'seq from' and 'seq to' fields automatically.
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
        data: { "bigarray[]": bigarray},
        url: "./search_top/", // url: "/dynadb/search_top/"+subid+"/",
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
                        else if(tdcount==7){
                            $(this).find('[type=checkbox]').prop('checked', false);
                            if (data['bonds'][trcount]!=undefined){
                                $(this).find('[type=checkbox]').prop('checked',data['bonds'][trcount]);
                            }
                        }
                        tdcount=tdcount+1;  
                    })
                 trcount=trcount+1;
                 })
                 if (data.warningmess.length>1){
                    $('#aligcontent').html( "<pre>"+data.warningmess+"</pre>" );
                    $('#showerroralig').show();
                 }
            }else{
                $('#aligcontent').html( "<pre>"+data.message+"</pre>" );
                $('#showerroralig').show();
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            $("#pdbchecker1").prop("disabled",false);
                if (XMLHttpRequest.readyState == 4) {
                    var responsetext = XMLHttpRequest.responseText;

                    alert(textStatus.substr(0,1).toUpperCase()+textStatus.substr(1)+":\nStatus: " + XMLHttpRequest.textStatus+". "+errorThrown+".\n"+responsetext);
                }
                else if (XMLHttpRequest.readyState == 0) {
                    alert("Connection error. Please, try later and check that your file is not larger than 50 MB.");
                }
                else {
                    alert("Unknown error");
                }
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

$("#pdbchecker1").click(function() {
    $('#showerroralig').hide();
    searchtop();
});

$('#showerroralig').hide();
$('#hidealig').click(function(){
    $('#showerroralig').hide();    
});
