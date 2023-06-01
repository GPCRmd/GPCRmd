function sortFunction(a, b) {
    if (a[0] === b[0]) {
        return 0;
    }
    else {
        return (a[0] < b[0]) ? -1 : 1;
    }
}

function ShowResults(data, restype,is_apoform){
    data.model=data.model.sort(sortFunction);
    data.dynlist=data.dynlist.sort(sortFunction);
    data.result=data.result.sort(sortFunction);


    var tablestr='';
    if (restype=='complex' &&  data.result.length>0 ){
        var cl=data.result;
        for(i=0; i<cl.length; i++){
            tablestr=tablestr+"<tr><td><a class='btn btn-info' target='_blank' role='button' href=/dynadb/complex/id/"+cl[i][0]+"> Complex with ID "+cl[i][0]+"</a> </td><td>  Receptor: <kbd>"+cl[i][1]+"</kbd> Ligand: <kbd>"+ cl[i][2]+"</kbd>. </td></tr>";
        }
    }//endif

    //Results are models
    if ( restype=='model'  && data.model.length>0){
        var rl=data.model
        for(i=0; i<rl.length; i++){ //rl[i].length>2
            if (rl[i].length>2 && (is_apoform=='com'||is_apoform=='both') ){
                tablestr=tablestr+"<tr><td>"+ "<a class='btn btn-info' target='_blank' role='button' href=/dynadb/model/id/"+rl[i][0]+"> Complex Structure ID:"+rl[i][0] +"</a> </td><td> Receptor: <kbd>"+rl[i][1]+"</kbd><br> Ligand:      <kbd>"+rl[i][2]+"</kbd> </td></tr>";
            }if (rl[i].length==2 && (is_apoform=='apo'||is_apoform=='both')) {
                tablestr=tablestr+"<tr><td>"+ "<a class='btn btn-info' target='_blank' role='button' href=/dynadb/model/id/"+rl[i][0]+"> Apoform Complex Structure ID:"+rl[i][0]+"</a> </td><td> Protein: <kbd>"+rl[i][1]+"</kbd> </td></tr>";
            }
        }
    }//endif


    if (restype=='dynamics' && data.dynlist.length>0  ){
        var dl=data.dynlist;
        for(i=0; i<dl.length; i++){
            if (dl[i].length>2 && (is_apoform=='com'||is_apoform=='both')){ //dl[i].length>2
                tablestr=tablestr+"<tr><td>"+ "<a class='btn btn-info' target='_blank' role='button' href=/view/"+dl[i][0]+"> Dynamics ID:"+dl[i][0]+" </a></td><td> Receptor: <kbd>"+dl[i][1]+ "</kbd><br> Ligand:     <kbd>"+ dl[i][2]+"</kbd></td></tr>";
            }if (dl[i].length==2 && (is_apoform=='apo'||is_apoform=='both')) {
                tablestr=tablestr+"<tr><td>"+ "<a class='btn btn-info' target='_blank' role='button' href=/view/"+dl[i][0]+"> Dynamics ID:"+dl[i][0]+" </a></td><td> Receptor:<kbd> "+dl[i][1]+"</kbd></td></tr>";
            }
        }
    } //endif

    return tablestr;

}//end of function definition
function CreateTable(){
    if ( $.fn.dataTable.isDataTable( '#ajaxresults22' ) ) {
        table = $('#ajaxresults22').DataTable();
    }
    else {
        table = $('#ajaxresults22').DataTable( {
            "sPaginationType" : "full_numbers",
            "lengthMenu": [[10, 20, 50, -1], [10, 20, 50, "All"]],
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



function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}


$("#tablesearch").click(function() {
    $('#badge_legend').hide();
    $('#ajaxresults22').DataTable().clear().draw();
    var exactboo=$('#exactmatch').prop('checked');
    var bigarray=[];
    var openpar=[];
    var closingpar=[]
    var flag=0; //means no errors
    $("#tablesearch").prop("disabled",true);
    $('#hiddenbar').show();
    $('#hiddenbarin').width("10%");

    //pick information of advanced search, parenthesis
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
        //pick simple search information
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
    $('#hiddenbarin').width("60%");
    //check that parenthesis are correct
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
    $('#hiddenbarin').width("80%");
    var restype=$('#result_type').val();
    var ff=$('#fftype').val();
    var tstep=$('#tstep').val();
    var gle=$('#gle').val();
    console.log(gle);
    if (! isNumber(tstep) && tstep.length>0){
        alert('Time step has to be a number');
        $("#tablesearch").prop("disabled",false);
        $('#hiddenbar').hide();
        $('#hiddenbarin').width("10%");
        return false;
    }
    var sof=$('#soft').val();
    var mem=$('#memtype').val();
    var method=$('#method').val();
    var sol=$('#soltype').val();
    if (restype=='model'){
        var is_apoform=$('input[name=radiosearch]:checked', '#hiddenmodel').val();
    }
    if (restype=='dynamics'){
        var is_apoform=$('input[name=radiosearch1]:checked', '#hidden').val();
    }
    $('#hiddenbarin').width("90%");
    ///////////////////////////////////////////EMPTY SEARCH //////////////////////////////////////////////////////////
    //search to perform when no elements were added to the right panel
    if(bigarray.length==1 && (restype=='model' || restype=='dynamics') ){ //empty
        if (exactboo==true){
            alert('Exact match does not work if the query is empty.');
            $("#tablesearch").prop("disabled",false);
            $('#hiddenbar').hide();
            $('#hiddenbarin').width("10%");
            return false;

        }
        $.ajax({
            type: "POST",
            data: {'restype':restype,'ff':ff,'tstep':tstep,'sol':sol,'mem':mem,'method':method,'sof':sof,'is_apo':is_apoform, 'gle':gle},
            headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            },
            url: "/dynadb/empty_search/",
            dataType: "json",
            success: function(data) {
                $('#hiddenbarin').width("100%");
                $("#tablesearch").prop("disabled",false);
                $('#hiddenbar').hide();
                $('#hiddenbarin').width("10%");
                if (data.message==''){
                    $('#ajaxresults22 tbody').empty();
                    tablestr=ShowResults(data, restype,is_apoform);
                    $('#ajaxresults22').DataTable().destroy()
                    $('#ajaxresults22 tbody').append(tablestr);
                    CreateTable();

                }else{
                    alert(data.message);
                }
            },

            error: function(XMLHttpRequest, textStatus, errorThrown) {
                $("#tablesearch").prop("disabled",false);
                $('#hiddenbar').hide();
                $('#hiddenbarin').width("10%");
                alert("Something unexpected happen.");
            }
        }); //end of ajax call

    }

    if (bigarray.length==1 && restype=='complex'){
        alert('Complex search does not work if there is not any protein or molecule.');
        $("#tablesearch").prop("disabled",false);
        $('#hiddenbar').hide();
        $('#hiddenbarin').width("10%");
        return false;
    }

    if (bigarray.length>1 || restype=='complex'){

        ///////////////////////////////////////////SIMPLE SEARCH //////////////////////////////////////////////////////////
        if ($('#gotoadvsearch').html().length==21){
            if ( (is_apoform==true && bigarray.length>2) || (is_apoform==true && bigarray[1][1]!='protein' ) ){
                flag=1;
            }
            if (bigarray.length>1 && flag==0){ //minimun length is 1 because of the table header

                console.log('before',bigarray);
                for (i=1;i<bigarray.length;i++){
                    bigarray[i].splice(1, 0, " ");
                    bigarray[i].splice(5, 0, "");        
                }

                console.log('after',bigarray);
                $.ajax({
                    type: "POST",
                    data: {  "bigarray[]": bigarray, 'exactmatch':exactboo,'restype':restype,'ff':ff,'tstep':tstep,'sol':sol,'mem':mem,'method':method,'sof':sof,'is_apo':is_apoform,'typeofsearch':typeofsearch, 'gle':gle},
                    headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    },
                    url: "/dynadb/advanced_search/",//"/dynadb/complex_search/",
                    dataType: "json",
                    success: function(data) {
                        $("#tablesearch").prop("disabled",false);
                        $('#hiddenbar').hide();
                        $('#hiddenbarin').width("10%");
                        if (data.message==''){
                            $('#ajaxresults22 tbody').empty(); //this new
                            tablestr=ShowResults(data,restype,is_apoform);
                            $('#ajaxresults22').DataTable().destroy() //this new
                            $('#ajaxresults22 tbody').append(tablestr);
                            CreateTable();

                        }else{
                            alert(data.message);
                        }
                    },

                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        $("#tablesearch").prop("disabled",false);
                        $('#hiddenbar').hide();
                        $('#hiddenbarin').width("10%");
                        alert("Something unexpected happen.");
                    }
                });

            }else {
                $("#tablesearch").prop("disabled",false);
                $('#hiddenbar').hide();
                $('#hiddenbarin').width("10%");
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
                $('#hiddenbar').hide();$('#hiddenbarin').width("10%");
            }
            console.log('adv',bigarray);
            if (flag==0){
                $.ajax({
                    type: "POST",
                    data: {  "bigarray[]": bigarray, 'exactmatch':exactboo,'restype':restype,'ff':ff,'tstep':tstep,'sol':sol,'mem':mem,'method':method,'sof':sof,'is_apo':is_apoform,'typeofsearch':typeofsearch, 'gle':gle},
                    headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    },
                    url: "/dynadb/advanced_search/",
                    dataType: "json",
                    success: function(data) {
                        $("#tablesearch").prop("disabled",false);
                        $('#hiddenbar').hide();$('#hiddenbarin').width("10%");
                        if (data.message==''){
                            $('#ajaxresults22 tbody').empty(); //this new
                            tablestr=ShowResults(data,restype,is_apoform);
                            $('#ajaxresults22').DataTable().destroy() //this new
                            $('#ajaxresults22 tbody').append(tablestr);
                            CreateTable();
                        }else{
                            alert(data.message);
                            $("#tablesearch").prop("disabled",false);
                            $('#hiddenbar').hide();$('#hiddenbarin').width("10%");
                        }
                    },

                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        $("#tablesearch").prop("disabled",false);
                        $('#hiddenbar').hide();$('#hiddenbarin').width("10%");
                        alert("Something unexpected happen.");
                    }
                });
            }else{//if flag 0
                alert(flagsms);
                $("#tablesearch").prop("disabled",false);
                $('#hiddenbar').hide();$('#hiddenbarin').width("10%");
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
});
