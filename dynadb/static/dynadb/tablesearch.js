$("#tablesearch").click(function() {
    var exactboo=$('#exactmatch').prop('checked');
    var bigarray=[];
    var openpar=[];
    var closingpar=[]
    var flag=0; //means no errors
    $("#tablesearch").prop("disabled",true);
    if ($('#gotoadvsearch').html().length==19){
        var typeofsearch='advanced';
        $("#myTable tr").each(function () {
            var postarray=[];
            var counter=0;
            $('td', this).each(function () {
                if (counter==0){
                    var drop=$(this).find(":selected").text();
                    postarray.push(drop);

                }else if (counter==1) {
                    var drop=$(this).find(":selected").text();
                    postarray.push(drop);
                    openpar.push(drop);

                }else{
                    if (counter==4){
                        if (postarray[2]=='protein') {
                            var isligrec=$(this).find('[type=checkbox]').prop('checked');
                            postarray.push(isligrec);
                        }else{
                            var drop=$(this).find(":selected").val();
                            postarray.push(drop);  
                        }
                    }else if (counter==5) {
                        var drop=$(this).find(":selected").text();
                        postarray.push(drop);
                        closingpar.push(drop);
                    } else {
                        var value = $(this).text(); //var value = $(this).text();
                        postarray.push(value);
                    }
                }
                counter=counter+1;
            })
            bigarray.push(postarray);
        })

    }else{
        var typeofsearch='simple';
        $("#myTable tr").each(function () {
            var postarray=[];
            var counter=0;
            $('td', this).each(function () {
                if (counter==0){
                    var drop=$(this).find(":selected").text();
                    postarray.push(drop);
                } else {
                    if (counter==3){
                        if(postarray[1]=='protein'){
                            var isligrec=$(this).find('[type=checkbox]').prop('checked');
                            postarray.push(isligrec);    
                        }else{
                            var drop=$(this).find(":selected").val();
                            postarray.push(drop); 
                        }

                    } else {
                        var value = $(this).text(); //var value = $(this).text();
                        postarray.push(value);
                    }
                }
                counter=counter+1;
            })
            bigarray.push(postarray);
        })
    } //else ends

    for (i=0;i<openpar.length;i++){
        if (openpar[i]=='(' && openpar[i+1]=='('){
            flag=2;
            flagsms='nested parenthesis is not allowed.';
        }
    }

    for (i=0;i<closingpar.length;i++){
        if (closingpar[i]==')' && closingpar[i+1]==')'){
            flag=2;
            flagsms='nested parenthesis is not allowed.';
        }
    }
    status='off';
    for (i=0;i<closingpar.length;i++){
        if ( closingpar[i]==')' && openpar[i]=='(' ) {
            flag=3;
            flagsms='inline parenthesis is not allowed.';
        }
        if (openpar[i]=='(') {
            if (status=='on'){
                flag=4;
                flagsms='Mismatching parenthesis!';
            }else{
                status='on';
            }

        }
        if (closingpar[i]==')'){
            if (status=='off'){
                flag=4;
                flagsms='Mismatching parenthesis!';
            }else{
                status='off';
            }
        }

    }

    if (status=='on'){
        flag=4;
        flagsms='Mismatching parenthesis!';
    }

    //console.log(bigarray);
    var restype=$('#result_type').val();
    var ff=$('#fftype').val();
    var tstep=$('#tstep').val();
    var sof=$('#soft').val();
    var mem=$('#memtype').val();
    var method=$('#method').val();
    var sol=$('#soltype').val();
    if (restype=='model'){
        var is_apoform=$('#apoform').prop('checked');
    }
    if (restype=='dynamics'){
        var is_apoform=$('#apoform_dyn').prop('checked');
    }

    console.log(bigarray.length,restype);

    ///////////////////////////////////////////EMPTY SEARCH //////////////////////////////////////////////////////////

    if(bigarray.length==1 && (restype=='model' || restype=='dynamics')){ //empty
        $.ajax({
            type: "POST",
            data: {'restype':restype,'ff':ff,'tstep':tstep,'sol':sol,'mem':mem,'method':method,'sof':sof,'is_apo':is_apoform},
            url: "/dynadb/empty_search/",
            dataType: "json",
            success: function(data) {
                $("#tablesearch").prop("disabled",false);
                if (data.message==''){
                    $('#ajaxresults22 tbody').empty();
                    var tablestr='';
                    //Results are models
                    if (data.model.length>0 && restype=='model'){
                        var rl=data.model
                        linkr='';
                        for(i=0; i<rl.length; i++){
                            if (rl[i].length>2){
                                tablestr=tablestr+"<tr><td>"+ "<a href=/dynadb/model/id/"+rl[i][0]+"> Complex Structure ID:"+rl[i][0] +"</a> </td><td> Complex Structure with receptor: "+rl[i][1]+", and ligand: "+rl[i][2]+" </td></tr>";
                            }else{
                                tablestr=tablestr+"<tr><td>"+ "<a href=/dynadb/model/id/"+rl[i][0]+"> Apoform Complex Structure ID:"+rl[i][0]+"</a> </td><td> With protein: "+rl[i][1]+" </td></tr>";
                            }

                        }
                        

                    }//endif

                    //Results are dynamics
                    if (data.dynlist.length>0 && restype=='dynamics'){
                        var dl=data.dynlist
                        linkd='';
                        for(i=0; i<dl.length; i++){
                            tablestr=tablestr+"<tr><td>"+ "<a href=/dynadb/dynamics/id/"+dl[i][0]+"> Dynamics ID:"+dl[i][0]+" </a> </td><td> Dynamics with receptor: "+dl[i][1]+ ",and ligand:"+ dl[i][2]+"</td></tr>";
                        }

                    } //endif

                $('#ajaxresults22 tbody').append(tablestr);
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
                $("#tablesearch").prop("disabled",false);
                alert("Something unexpected happen.");
            }
        }); //end of ajax call

    }




    if (bigarray.length>1 || restype=='complex'){

        ///////////////////////////////////////////SIMPLE SEARCH //////////////////////////////////////////////////////////
        if ($('#gotoadvsearch').html().length==21){ //simple search selected
            if ( (is_apoform==true && bigarray.length>2) || (is_apoform==true && bigarray[1][1]!='protein' ) ){
                flag=1;
            }

            if (bigarray.length>1 && flag==0){ //minimun length is 1 because of the table header
                $.ajax({
                    type: "POST",
                    data: {  "bigarray[]": bigarray, 'exactmatch':exactboo,'restype':restype,'ff':ff,'tstep':tstep,'sol':sol,'mem':mem,'method':method,'sof':sof,'is_apo':is_apoform,'typeofsearch':typeofsearch},
                    url: "/dynadb/complex_search/",
                    dataType: "json",
                    success: function(data) {
                        $("#tablesearch").prop("disabled",false);
                        if (data.message==''){
                            $('#ajaxresults22 tbody').empty();
                            var tablestr='';
                            //Results are complexes
                            if (data.result.length>0 && restype=='complex'){
                                var cl=data.result;
                                listc='';
                                for(i=0; i<cl.length; i++){
                                    tablestr=tablestr+"<tr><td> <a href=/dynadb/complex/id/"+cl[i][0]+"> Complex with ID "+cl[i][0]+"</a> </td><td>  Composed by <b>receptor</b>: "+cl[i][1]+", and <b>ligand</b> "+ cl[i][2]+". </td></tr>";
                                }
                            }//endif

                            //Results are models
                            if (data.model.length>0 && restype=='model'){
                                var rl=data.model
                                linkr='';
                                for(i=0; i<rl.length; i++){
                                    if (is_apoform==false){
                                        tablestr=tablestr+"<tr><td>"+ "<a href=/dynadb/model/id/"+rl[i][0]+"> Complex Structure ID:"+rl[i][0] +"</a></td><td> Model with receptor: "+rl[i][1]+", and ligand: "+rl[i][2]+" </td></tr>";
                                    }else{
                                        tablestr=tablestr+"<tr><td>"+ "<a href=/dynadb/model/id/"+rl[i][0]+"> Apoform Complex Structure ID:"+rl[i][0]+"</a></td><td> With protein: "+rl[i][1]+" </td></tr>";
                                    }

                                }

                            }//endif

                            //Results are dynamics
                            if (data.dynlist.length>0 && restype=='dynamics'){
                                var dl=data.dynlist
                                linkd='';
                                for(i=0; i<dl.length; i++){
                                    tablestr=tablestr+"<tr><td>"+ "<a href=/dynadb/dynamics/id/"+dl[i][0]+"> Dynamics ID:"+dl[i][0]+" </a></td><td> Dynamics with receptor: "+dl[i][1]+ ",and ligand:"+ dl[i][2]+"</td></tr>";
                                }

                            } //endif


                        $('#ajaxresults22 tbody').append(tablestr);
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
                        $("#tablesearch").prop("disabled",false);
                        alert("Something unexpected happen.");
                    }
                });

            }else {
                $("#tablesearch").prop("disabled",false);
                if (flag==1){
                    alert('Apoforms are composed by a single protein. Try again.'); 
                }else{
                    alert('You have to add proteins, molecules or compounds from the left to search for complexes.');
                }
            }


        ///////////////////////////////////////////ADV SEARCH //////////////////////////////////////////////////////////
        }else{
            if (is_apoform==true) { //only allow proteins and OR'S
                for (i=1;i<bigarray.length;i++){
                    if ( (bigarray[i][0]!='OR' && (bigarray[i][0]!=' ' && bigarray[i][0]!='') ) || bigarray[i][2]!='protein'){
                        flagsms='Apoform search only allows OR search with protein type';
                        flag=5;
                    }
                }
                $("#tablesearch").prop("disabled",false);
            }
            if (flag==0){
                $.ajax({
                    type: "POST",
                    data: {  "bigarray[]": bigarray, 'exactmatch':exactboo,'restype':restype,'ff':ff,'tstep':tstep,'sol':sol,'mem':mem,'method':method,'sof':sof,'is_apo':is_apoform,'typeofsearch':typeofsearch},
                    url: "/dynadb/advanced_search/",
                    dataType: "json",
                    success: function(data) {
                        $("#tablesearch").prop("disabled",false);
                        if (data.message==''){
                            $('#ajaxresults22 tbody').empty();
                            var tablestr='';
                            //Results are complexes
                            if (data.result.length>0 && restype=='complex'){
                                var cl=data.result;
                                listc='';
                                for(i=0; i<cl.length; i++){
                                    tablestr="<tr><td> <a href=/dynadb/complex/id/"+cl[i][0]+"> Complex with ID "+cl[i][0]+"</a> </td><td>  Composed by receptor: "+cl[i][1]+", and ligand "+ cl[i][2]+". </td><tr>";
                                }
                            }//endif

                            //Results are models
                            if (data.model.length>0 && restype=='model'){
                                var rl=data.model
                                linkr='';
                                for(i=0; i<rl.length; i++){
                                    if (is_apoform==false){
                                        tablestr=tablestr+"<tr><td>"+ "<a href=/dynadb/model/id/"+rl[i][0]+"> Complex Structure ID:"+rl[i][0] +"</a> </td><td> Complex Structure with receptor: "+rl[i][1]+", and ligand: "+rl[i][2]+" </td></tr>";
                                    }else{
                                        tablestr=tablestr+"<tr><td>"+ "<a href=/dynadb/model/id/"+rl[i][0]+"> Apoform Complex Structure ID:"+rl[i][0]+"</a> </td><td> With protein: "+rl[i][1]+" </td></tr>";
                                    }

                                }

                            }//endif


                            if (data.dynlist.length>0 && restype=='dynamics'){
                                var dl=data.dynlist;
                                linkd='';
                                for(i=0; i<dl.length; i++){
                                     tablestr=tablestr+"<tr><td>"+ "<a href=/dynadb/dynamics/id/"+dl[i][0]+"> Dynamics ID:"+dl[i][0]+" </a></td><td> Dynamics with receptor: "+dl[i][1]+ ",and ligand:"+ dl[i][2]+"</td></tr>";
                                }

                            } //endif


                        $('#ajaxresults22 tbody').append(tablestr);
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
                            $("#tablesearch").prop("disabled",false);
                        }
                    },

                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        $("#tablesearch").prop("disabled",false);
                        alert("Something unexpected happen.");
                    }
                });
            }else{//if flag 0
                alert(flagsms);
                $("#tablesearch").prop("disabled",false);
            }
        }//end of the "advanced search" else.

    }//bigarray.lentgh >1
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
$(document).on('click', '#deleterow', function(e){
  e.preventDefault();
  $(this).closest('tr').remove();
  $('#myTable').find('.tableselect:first').empty().append('<option selected="selected" value=" ">'); //</option><option value="not">NOT</option>
  //$('#myTable').find('.tableselect:first').val('or');
  //$('#myTable').find('.tableselect:first').prop('disabled', 'disabled');
});

