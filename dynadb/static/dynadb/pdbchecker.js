
function sendpar() {
    //Gets the segments the user has defined in the model section of the submission and calls the PDBcheck function.

    var bigarray=[];
    $("#pElement1 tr").each(function () {
        var postarray=[];
        $('td', this).each(function () {
            var value = $(this).find(":input").val();
            if (postarray.length==7){
                value = $(this).find('[type=checkbox]').prop('checked');
            }            
            postarray.push(value);
        })
        bigarray.push(postarray);
    })
    var goon=true;

    counter=1;
    for (i=0,lenout=bigarray.length;i<lenout;i++){
        for (j=0,len=bigarray.length;j<len;j++){
            if (i!=j){
                console.log(i,j);
                console.log('segid and chain match',bigarray[i][1]==bigarray[j][1] && bigarray[i][2]==bigarray[j][2]);
                console.log('overlap numbers',parseInt(bigarray[i][3],10)>=parseInt(bigarray[j][3],10) && parseInt(bigarray[i][3],10)<=parseInt(bigarray[j][4],10));
                console.log('overlap numbers2',parseInt(bigarray[i][4],10)>=parseInt(bigarray[j][3],10) && parseInt(bigarray[i][4],10)<=parseInt(bigarray[j][4],10));

                // From 300 to 320
                //from 301 to 304
                //if 301 or 304 is inside 300 to 320, then there is overlap: (301>300? AND 301 < 320? ) OR (304>300 AND 304<320)
                
                if ( (parseInt(bigarray[i][3],10)>=parseInt(bigarray[j][3],10) && parseInt(bigarray[i][3],10)<=parseInt(bigarray[j][4],10) && bigarray[i][1]==bigarray[j][1] && bigarray[i][2]==bigarray[j][2]) || (parseInt(bigarray[i][4],10)>=parseInt(bigarray[j][3],10) && parseInt(bigarray[i][4],10)<=parseInt(bigarray[j][4],10) && bigarray[i][1]==bigarray[j][1] && bigarray[i][2]==bigarray[j][2]) ) {
                    alert('There is overlapping between the range '+bigarray[i]+' and ' +bigarray[j]);
                    return false;
                    //goon=false;
                }
                
                //check if there is more than one pdb segment aligned to the same sequence segment: overlapping.
                if (( (parseInt(bigarray[i][5],10)>=parseInt(bigarray[j][5],10) && parseInt(bigarray[i][5],10)<=parseInt(bigarray[j][6],10) && bigarray[i][0]==bigarray[j][0]) || (parseInt(bigarray[i][6],10)>=parseInt(bigarray[j][5],10) && parseInt(bigarray[i][6],10)<=parseInt(bigarray[j][6],10) && bigarray[i][0]==bigarray[j][0]) )) {
                    alert('Two different PDB segments partially or totally aligned with the same protein interval. This is not allowed');
                    return false;
                }    
                
            }
        }
        
        
        
        
        
        
//      if there is a number that is not zero, remove all zeros on left except the one that next to an 'x' or 'X'  
        bigarray[i][3] = bigarray[i][3].trim().replace('^(?!0+$)0+(?![xX])');
        bigarray[i][4] = bigarray[i][4].trim().replace('^(?!0+$)0+(?![xX])');
//      parseInt: If the first non-whitespace character is 0, the number is in octal (only in old browsers). 
//      If the two first non-whitespace characters are '0x' or '0X', the number is in hexadecimal.
//      Otherwise, the number is in decimal. A base can be forced by adding an extra parameter.
        if (parseInt(bigarray[i][3])>parseInt(bigarray[i][4])){
            alert('Res from is bigger than or equal to Res to');
            goon=false;
        }
        if (parseInt(bigarray[i][5],10)>parseInt(bigarray[i][6],10)){
            alert('Seq Res from is bigger than or equal to Seq Res to');
            goon=false;
        }   
        counter=counter+1;
    }
    if (goon==true){
        $.ajax({
            type: "POST",
            data: { "bigarray[]": bigarray},
            url:"./ajax_pdbchecker/",
            dataType: "json",
            success: function(data) {
                $("#pdbchecker2").prop("disabled",false);
                console.log(data);
                if (data.message==''){
                    newwindow=window.open('./ajax_pdbchecker/');
                    if (window.focus) {newwindow.focus()}
                }else{
                    console.log(data.message);
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

$('#pdbchecker2').click(function(){
    sendpar();
});
