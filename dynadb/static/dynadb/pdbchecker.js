
function sendpar() {
    var bigarray=[];
    $("#pElement1 tr").each(function () {
        var postarray=[];
        $('td', this).each(function () {
            var value = $(this).find(":input").val();
            postarray.push(value);
        })
        bigarray.push(postarray);
    })
    var goon=true;
    counter=1;
    for (i=0,lenout=bigarray.length;i<lenout;i++){
        for (j=counter,len=bigarray.length;j<len;j++){
            if ( (parseInt(bigarray[i][3],10)>=parseInt(bigarray[j][3],10) && parseInt(bigarray[i][3],10)<=parseInt(bigarray[j][4],10)) || (parseInt(bigarray[i][4],10)>=parseInt(bigarray[j][3],10) && parseInt(bigarray[i][4],10)<=parseInt(bigarray[j][4],10)) ) {
                alert('There is overlapping between the range'+bigarray[i]+' and ' +bigarray[j]);
                goon=false;
            }
        }
//      if there is a number that is not zero, remove all zeros on left except the one that next to an 'x' or 'X'  
        bigarray[i][3] = bigarray[i][3].trim().replace('^(?!0+$)0+(?![xX])');
        bigarray[i][4] = bigarray[i][4].trim().replace('^(?!0+$)0+(?![xX])');
//      parseInt: If the first non-whitespace character is 0, the number is in octal (only in old browsers). 
//      If the two first non-whitespace characters are '0x' or '0X', the number is in hexadecimal.
//      Otherwise, the number is in decimal. A base can be forced by adding an extra parameter.
        if (parseInt(bigarray[i][3])>=parseInt(bigarray[i][4])){
            alert('Res from is bigger than or equal to Res to');
            goon=false;
        }
        if (parseInt(bigarray[i][5],10)>=parseInt(bigarray[i][6],10)){
            alert('Seq Res from is bigger than or equal to Seq Res to');
            goon=false;
        }   
        counter=counter+1;
    }
    if (goon==true){
        $.ajax({
            type: "POST",
            data: { "bigarray[]": bigarray,"url": window.location.href},
            //data: { "id_prot": postarray[0],"chain": postarray[1], "segid": postarray[2], "restart": postarray[3], "restop": postarray[4], "seqstart": postarray[5], "seqstop": postarray[6], "url": window.location.href },
            url: "/dynadb/ajax_pdbchecker/"+'c'+bigarray[0][0]+'_'+bigarray[0][1]+'_'+bigarray[0][2]+'_'+bigarray[0][3]+'_'+bigarray[0][4]+'_'+bigarray[0][5]+'_'+bigarray[0][6],
            dataType: "json",
            success: function(data) {
                $("#pdbchecker2").prop("disabled",false);
                if (data.message==''){
                    newwindow=window.open('/dynadb/ajax_pdbchecker/'+'c'+bigarray[0][0]+'_'+bigarray[0][1]+'_'+bigarray[0][2]+'_'+bigarray[0][3]+'_'+bigarray[0][4]+'_'+bigarray[0][5]+'_'+bigarray[0][6],'','height=500,width=700');
                    if (window.focus) {newwindow.focus()}
                }else{
                    alert(data.message);
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
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
            },
            complete: function(XMLHttpRequest, textStatus, errorThrown) {
                $("#pdbchecker2").prop("disabled",false);
            }
        });
    }else{
        $("#pdbchecker2").prop("disabled",false);
    }
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
