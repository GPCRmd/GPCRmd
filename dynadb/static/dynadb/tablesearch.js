$("#tablesearch").click(function() {
    var exactboo=$('#exactmatch').prop('checked');
    var bigarray=[];
    var openpar=[];
    var closingpar=[]
    var flag=0; //means no errors
    $("#tablesearch").prop("disabled",true);

    if ($('#gotoadvsearch').html().length==13){
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
    console.log(bigarray);
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



    if ($('#gotoadvsearch').html().length!=13){ //simple search selected
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
                        $('#ajaxresults').html('No results.');
                        //Results are complexes
                        if (data.result.length>0 && restype=='complex'){

                            $('#ajaxresults').html('Complex Results:');
                            $('#ajaxresults').append("<ul id='complexes'></ul>");
                            var cl=data.result;
                            listc='';
                            for(i=0; i<cl.length; i++){
                                $("#complexes").append("<li> <a href=/dynadb/complex/id/"+cl[i][0]+"> Complex with ID "+cl[i][0]+"</a>  Composed by receptor: "+cl[i][1]+", and ligand "+ cl[i][2]+". </li>");
                            }
                        }//endif

                        //Results are models
                        if (data.model.length>0 && restype=='model'){
                            $('#ajaxresults').html('Models Results');
                            $('#ajaxresults').append("<ul id='modres'></ul>");
                            var rl=data.model
                            linkr='';
                            for(i=0; i<rl.length; i++){
                                if (is_apoform==false){
                                    $("#modres").append("<li>"+ "<a href=/dynadb/model/id/"+rl[i][0]+"> Model ID:"+rl[i][0] +"</a> Model with receptor: "+rl[i][1]+", and ligand: "+rl[i][2]+" </li>");
                                }else{
                                    $("#modres").append("<li>"+ "<a href=/dynadb/model/id/"+rl[i][0]+"> Apoform model ID:"+rl[i][0]+"</a> With protein: "+rl[i][1]+" </li>");
                                }

                            }

                        }//endif


                        if (data.dynlist.length>0 && restype=='dynamics'){
                            $("#ajaxresults").html('Dynamics Results');
                            $("#ajaxresults").append("<ul id='dynres'></ul>");
                            var dl=data.dynlist.split(',');
                            linkd='';
                            for(i=0; i<dl.length; i++){
                                $("#dynres").append("<li>"+ "<a href=/dynadb/dynamics/id/"+dl[i]+">"+dl[i]+" </a>" +"</li>");
                            }

                        } //endif

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
            $("#tablesearch").prop("disabled",true);
            if (flag==1){
                alert('Apoforms are composed by a single protein. Try again.'); 
            }else{
                alert('You have to add a protein, a compound or a molecule to the table at the right.');
            }
        }



    }else{
        if (is_apoform==true) { //only allow proteins and OR'S
            for (i=1;i<bigarray.length;i++){
                if ( (bigarray[i][0]!='OR' && (bigarray[i][0]!=' ' && bigarray[i][0]!='') ) || bigarray[i][2]!='protein'){
                    flagsms='Apoform search only allows OR search with protein type';
                    flag=5;
                }
            }
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
                        $('#ajaxresults').html('No results.');
                        //Results are complexes
                        if (data.result.length>0 && restype=='complex'){

                            $('#ajaxresults').html('Complex Results:');
                            $('#ajaxresults').append("<ul id='complexes'></ul>");
                            var cl=data.result;
                            listc='';
                            for(i=0; i<cl.length; i++){
                                $("#complexes").append("<li> <a href=/dynadb/complex/id/"+cl[i][0]+"> Complex with ID "+cl[i][0]+"</a>  Composed by receptor: "+cl[i][1]+", and ligand "+ cl[i][2]+". </li>");
                            }
                        }//endif

                        //Results are models
                        if (data.model.length>0 && restype=='model'){
                            $('#ajaxresults').html('Models Results');
                            $('#ajaxresults').append("<ul id='modres'></ul>");
                            var rl=data.model
                            linkr='';
                            for(i=0; i<rl.length; i++){
                                if (is_apoform==false){
                                    $("#modres").append("<li>"+ "<a href=/dynadb/model/id/"+rl[i][0]+"> Model ID:"+rl[i][0] +"</a> Model with receptor: "+rl[i][1]+", and ligand: "+rl[i][2]+" </li>");
                                }else{
                                    $("#modres").append("<li>"+ "<a href=/dynadb/model/id/"+rl[i][0]+"> Apoform model ID:"+rl[i][0]+"</a> With protein: "+rl[i][1]+" </li>");
                                }

                            }

                        }//endif


                        if (data.dynlist.length>0 && restype=='dynamics'){
                            $("#ajaxresults").html('Dynamics Results');
                            $("#ajaxresults").append("<ul id='dynres'></ul>");
                            var dl=data.dynlist.split(',');
                            linkd='';
                            for(i=0; i<dl.length; i++){
                                $("#dynres").append("<li>"+ "<a href=/dynadb/dynamics/id/"+dl[i]+">"+dl[i]+" </a>" +"</li>");
                            }

                        } //endif

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

