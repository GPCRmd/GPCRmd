//MAIN SEARCHER, sends ajax call to auto_query function. Returns: link to result + Add to table button


function CreateTable(){
    if ( $.fn.dataTable.isDataTable( '#ajaxresults22' ) ) {
        table = $('#ajaxresults22').DataTable();
    }
    else {
        table = $('#ajaxresults22').DataTable( {
            "sPaginationType" : "full_numbers",
            "lengthMenu": [[5, 25, 50, -1], [5, 25, 50, "All"]],
            "oLanguage": {
                "oPaginate": {
                    "sPrevious": "<",
                    "sNext": ">",
                    "sFirst": "<<",
                    "sLast": ">>",
                 }
            }
        } );
    }   
}
$("#Searcher").click(function(e) {
    $('#ajaxresults22').DataTable().clear().draw();
    e.preventDefault(); //not helping, still GET error sometimes...
    var p=$("#protein22").val();
    var return_type=$("#simpletype").find(":selected").val();
    $("#Searcher").prop('disabled', true);
    $.ajax({
        type: "POST",
        data: { cmolecule: p, return_type:return_type},
        headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        },
        url: "/dynadb/ajaxsearch/",
        dataType: "json",
        success: function(data) {
            $("#Searcher").prop("disabled",false);
            if (data.message==''){
                $('#ajaxresults22 tbody').empty();
                var linkresult='';

                for(i=0; i<data.compound.length; i++){
                    linkresult=linkresult+'<tr><td> <a target="_blank" href=/dynadb/compound/id/'+data.compound[i][0]+'> Compound #'+data.compound[i][0] +': '+data.compound[i][1]+'<br><img src="'+data.compound[i][3]+'"  height="170" width="170"/></a></td><td>  <button class="compound" value="ligand" type="button" name='+data.compound[i][0]+'%'+data.compound[i][1].replace(' ','!')+' ><span class="glyphicon glyphicon-plus"></span>Add to search</button><br></td></tr>';
                }
                for(i=0; i<data.protein.length; i++){
                    linkresult=linkresult+'<tr><td>   <a target="_blank" href=/dynadb/protein/id/'+data.protein[i][0]+'> Protein #'+ data.protein[i][0]+' : '+data.protein[i][1]+'</a> </td><td>   <button class="protein" type="button" value="receptor" name='+data.protein[i][0]+'%'+data.protein[i][1].replace(' ','!')+' ><span class="glyphicon glyphicon-plus"></span> Add to search</button><br></td></tr>';
                }
                for(i=0; i<data.molecule.length; i++){
                    linkresult=linkresult+'<tr><td>  <a target="_blank" href=/dynadb/molecule/id/'+data.molecule[i][0]+'> Molecule #'+data.molecule[i][0]+': '+data.molecule[i][3]+'<br><img src="'+data.molecule[i][2]+'"  height="170" width="170"/></a> </td><td>  <button class="molecule" type="button" value="ligand" name='+data.molecule[i][0]+'%'+data.molecule[i][3].replace(' ','!')+' ><span class="glyphicon glyphicon-plus"></span>Add to search</button><br></td></tr>';
                }
                $('#ajaxresults22').DataTable().destroy()
                $('#ajaxresults22 tbody').append(linkresult);

                if ( $.fn.dataTable.isDataTable( '#ajaxresults22' ) ) {
                    table = $('#ajaxresults22').DataTable();
                }
                else {
                    table = $('#ajaxresults22').DataTable( {
                        "sPaginationType" : "full_numbers",
                        "lengthMenu": [[5, 25, 50, -1], [5, 25, 50, "All"]],
                        "oLanguage": {
                            "oPaginate": {
                                "sPrevious": "<",
                                "sNext": ">",
                                "sFirst": "<<",
                                "sLast": ">>",
                             }
                        }
                    } );
                }           
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


$(document).on('keypress', function (event) {
    if (event.keyCode == 13) {
       event.preventDefault();
       if ( $('#protein22').is(":focus") ){
           $('#Searcher').click(); //add .delay(200)?
       }else{
           $('#tablesearch').click();
       }
    }
});
