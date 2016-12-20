//MAIN SEARCHER, sends ajax call to auto_query function. Returns: link to result + Add to table button

function ShowResults(data, restype,is_apoform){
    var tablestr='';
    if (restype=='complex' &&  data.result.length>0 ){
        var cl=data.result;
        for(i=0; i<cl.length; i++){
            tablestr=tablestr+"<tr><td><a target='_blank' class='btn btn-info' role='button' href=/dynadb/complex/id/"+cl[i][0]+"> Complex with ID "+cl[i][0]+"</a></td><td> Receptor: <kbd>"+cl[i][1]+"</kbd> Ligand: <kbd>"+ cl[i][2]+"</kbd></td></tr>";
        }
    }//endif

    //Results are models
    if ( restype=='model'  && data.model.length>0){
        var rl=data.model
        for(i=0; i<rl.length; i++){ //rl[i].length>2
            if (rl[i].length>2 && (is_apoform=='com'||is_apoform=='both') ){
                tablestr=tablestr+"<tr><td>"+ "<a target='_blank' class='btn btn-info' role='button' href=/dynadb/model/id/"+rl[i][0]+"> Complex Structure ID:"+rl[i][0] +" </a></td><td> Receptor: <kbd>"+rl[i][1]+"<br></kbd> Ligand: <kbd>"+rl[i][2]+"</kbd></td></tr>";
            }if (rl[i].length==2 && (is_apoform=='apo'||is_apoform=='both')) {
                tablestr=tablestr+"<tr><td>"+ "<a target='_blank' class='btn btn-info' role='button' href=/dynadb/model/id/"+rl[i][0]+"> Apoform Complex Structure ID:"+rl[i][0]+" </a></td><td> Protein: <kbd>"+rl[i][1]+"</kbd></td></tr>";
            }
        }
    }//endif


    if (restype=='dynamics' && data.dynlist.length>0  ){
        var dl=data.dynlist;
        for(i=0; i<dl.length; i++){
            if (dl[i].length>2 && (is_apoform=='com'||is_apoform=='both')){ //dl[i].length>2
                tablestr=tablestr+"<tr><td>"+ "<a target='_blank' class='btn btn-info' role='button' href=/dynadb/dynamics/id/"+dl[i][0]+"> Dynamics ID:"+dl[i][0]+" </a></td><td> Receptor: <kbd>"+dl[i][1]+ "<br></kbd> Ligand:<kbd>"+ dl[i][2]+"</kbd></td></tr>";
            }if (dl[i].length==2 && (is_apoform=='apo'||is_apoform=='both')) {
                tablestr=tablestr+"<tr><td>"+ "<a target='_blank' class='btn btn-info' role='button' href=/dynadb/dynamics/id/"+dl[i][0]+"> Dynamics ID:"+dl[i][0]+" </a></td><td> Receptor:<kbd> "+dl[i][1]+"</kbd></td></tr>";
            }
        }
    } //endif

    return tablestr;

}//end of function definition

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
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

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
$("#Searcher").click(function(e) {
    $('#ajaxresults22').DataTable().clear().draw();
    e.preventDefault(); //not helping, still GET error sometimes...
    var p=$("#protein22").val();
    var return_type=$("#simpletype").find(":selected").val();

    var idsearch=$("#idsearch").prop('checked');

    if (idsearch==true){
        p=parseInt(p);
        if (isNaN(p)) {
            alert('ID search demands a number');
            return false;
        }
    }
    $("#Searcher").prop('disabled', true);
    $.ajax({
        type: "POST",
        data: { cmolecule: p, return_type:return_type, id_search:idsearch},
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
                var linkresult1='';
                var linkresult2='';
                var linkresult3='';

                for(i=0; i<data.compound.length; i++){
                    linkresult=linkresult+'<tr><td> <a target="_blank" class="btn btn-info" role="button" href=/dynadb/compound/id/'+data.compound[i][0]+'> Compound ID: '+data.compound[i][0] +' '+data.compound[i][1]+'</a> <span title="Number of dynamics in which this element is present" class="badge">'+data.compound[i][data.compound[i].length-1]+'</span><br> <br><img src="'+data.compound[i][3]+'"  height="170" width="170"/></td><td align="left"> <button class="compound" value="ligand" type="button" name='+data.compound[i][0]+'%'+data.compound[i][1].replace(' ','!')+' ><span class="glyphicon glyphicon-plus"></span>Add to search</button><br></td></tr>';
                }

                for(i=0; i<data.molecule.length; i++){
                    linkresult=linkresult+'<tr><td>  <a target="_blank" class="btn btn-info" role="button" href=/dynadb/molecule/id/'+data.molecule[i][0]+'> Molecule ID: '+data.molecule[i][0]+' '+data.molecule[i][3]+'</a> <span title="Number of dynamics in which this element is present" class="badge"> '+data.molecule[i][data.molecule[i].length-1]+'</span> <span title="Net Charge" class="badge"> '+data.molecule[i][data.molecule[i].length-2]+'</span><br> <br><img src="'+data.molecule[i][2]+'"  height="170" width="170"/> </td><td  align="left">  <button class="molecule" type="button" value="ligand" name='+data.molecule[i][0]+'%'+data.molecule[i][3].replace(' ','!')+' ><span class="glyphicon glyphicon-plus"></span>Add to search</button><br></td></tr>';
                }

                for(i=0; i<data.protein.length; i++){
                    linkresult=linkresult+'<tr><td>   <a target="_blank" class="btn btn-info" role="button" href=/dynadb/protein/id/'+data.protein[i][0]+'> Protein ID: '+ data.protein[i][0]+'</a> <span title="Number of dynamics in which this element is present" class="badge">'+data.protein[i][data.protein[i].length-1]+'</span> '+data.protein[i][1]+'</td><td  align="left">   <button class="protein" type="button" value="GPCR" name='+data.protein[i][0]+'%'+data.protein[i][1].replace(' ','!')+' ><span class="glyphicon glyphicon-plus"></span> Add to search</button><br></td></tr>';
                }

                for(i=0; i<data.names.length; i++){
                    if (data.names[i][0].length>2){
                        if (data.names[i][1]=='complex'){
                            linkresult1=linkresult1+"<tr><td> <a target='_blank' class='btn btn-info' role='button' href=/dynadb/complex/id/"+data.names[i][0][0]+"> Complex with ID "+data.names[i][0][0]+"</a> </td><td  align='left'> Receptor: <kbd>"+data.names[i][0][1]+"</kbd><br> Ligand: <kbd>"+ data.names[i][0][2]+"</kbd>. </td></tr>";
                        }
                        else if (data.names[i][1]=='model'){
                            linkresult2=linkresult2+"<tr><td>"+ "<a target='_blank' class='btn btn-info' role='button' href=/dynadb/model/id/"+data.names[i][0][0]+"> Complex Structure ID:"+data.names[i][0][0] +"</a> </td><td  align='left'> Receptor: <kbd>"+data.names[i][0][1]+"</kbd><br> Ligand: <kbd>"+data.names[i][0][2]+"</kbd> </td></tr>";
                        }

                        else{ 
                            linkresult3=linkresult3+"<tr><td>"+ "<a target='_blank' class='btn btn-info' role='button' href=/dynadb/dynamics/id/"+data.names[i][0][0]+"> Dynamics ID:"+data.names[i][0][0]+" </a></td><td align='left'> Receptor: <kbd>"+data.names[i][0][1]+ "</kbd><br> Ligand:<kbd>"+ data.names[i][0][2]+"</kbd></td></tr>";
                        }

                    }else{
                        if (data.names[i][1]=='model'){
                            linkresult2=linkresult2+"<tr><td>"+ "<a target='_blank' class='btn btn-info' role='button' href=/dynadb/model/id/"+data.names[i][0][0]+"> Apoform Complex Structure ID:"+data.names[i][0][0]+"</a> </td><td align='left'> Protein: <kbd>"+data.names[i][0][1]+"</kbd> </td></tr>"
                        }else{
                            linkresult3=linkresult3+"<tr><td>"+ "<a target='_blank' class='btn btn-info' role='button' href=/dynadb/dynamics/id/"+data.names[i][0][0]+"> Dynamics ID:"+data.names[i][0][0]+" </a></td><td align='left'> Receptor:<kbd> "+data.names[i][0][1]+"</kbd></td></tr>";
                        }

                    }
                }
                linkresult=linkresult+linkresult1+linkresult2+linkresult3;
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
