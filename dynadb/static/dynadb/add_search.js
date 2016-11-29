$('#hidden').hide();
$('#hiddenmodel').hide();
var counter=0;

$(document).on('click', '.protein, .molecule, .compound', function(){
    console.log($('#result_type').find(":selected").text());
    if (counter%2==0){
        var text = $(this).attr("name");
        var nameandid=text.split('%');
        var id=nameandid[0];
        console.log('what we recieve',nameandid);
        var truename=nameandid[1].replace('!','-');
        console.log(truename);
        text=id;
        var myclass= $(this).attr("class");
        var ligrec= $(this).attr("value");
        $('#myTable').find('thead').html('<tr><th>Boolean</th><th>Type</th><th>ID</th> <th></th> <th>Name</th> <th></th> </tr>');
        if (myclass=='protein'){
            $('#myTable').find('tbody').append('<tr title='+truename+'><td><select class="tableselect"><option value="and">AND</option></select></td><td>'+myclass+'</td><td>'+text+'</td><td><input id="ligandreceptor" type="checkbox" name="ligrec" value="some"> Is '+ligrec+' </td><td>'+truename+'</td><td><button id="deleterow" class="btn btn-danger btn-sm"> <span class="glyphicon glyphicon-trash"></span> </button></td></tr>');
        }else{
            if($('#result_type').find(":selected").text()=='Complex Structure' ||$('#result_type').find(":selected").text()=='Dynamics'){
                $('#myTable').find('tbody').append('<tr title='+truename+'><td><select class="tableselect"><option value="and">AND</option></select></td><td>'+myclass+'</td><td>'+text+'</td><td><select class="ligselect"><option value="orto">Orthosteric Ligand</option><option value="alo">Allosteric Ligand</option><option value="other">Other</option></select> </td><td>'+truename+'</td><td><button id="deleterow" class="btn btn-danger btn-sm"> <span class="glyphicon glyphicon-trash"></span> </button></td></tr>');
            }else{
                $('#myTable').find('tbody').append('<tr title='+truename+'><td><select class="tableselect"><option value="and">AND</option></select></td><td>'+myclass+'</td><td>'+text+'</td><td><select class="ligselect"><option value="orto">Orthosteric Ligand</option><option value="alo">Allosteric Ligand</option></select> </td><td>'+truename+'</td><td><button id="deleterow" class="btn btn-danger btn-sm"> <span class="glyphicon glyphicon-trash"></span> </button></td></tr>');
            }

        }

        $('#myTable').find('.tableselect:first').empty().append('<option selected="selected" value=" "> </option>');

    }else{
        var text = $(this).attr("name");
        var nameandid=text.split('%');
        var id=nameandid[0];
        var truename=nameandid[1].replace('!','-');
        text=id;
        var myclass= $(this).attr("class");
        var ligrec= $(this).attr("value");
        $('#myTable').find('thead').html('<tr><th>Boolean</th><th>  </th><th>Type</th><th>ID</th> <th></th> <th></th> <th>Name</th> </tr>');
        if (myclass=='protein'){
            $('#myTable').find('tbody').append('<tr title='+truename+'><td><select class="tableselect">   <option value="AND">AND</option>   <option value="OR">OR</option>   <option value="NOT">NOT</option>  </select>  </td><td>   <select class="paren"> <option  value="(">(</option> <option selected="selected" value=""> </option></select></td>      <td>'+myclass+'</td><td>'+text+'</td><td><input id="ligandreceptor" type="checkbox" name="ligrec" value="some"> Is '+ligrec+' </td><td><select class="paren"><option value=")">)</option><option selected="selected" value=""></option></select></td><td>'+truename+'</td><td><button id="deleterow" class="btn btn-danger btn-sm" >  <span class="glyphicon glyphicon-trash"></span> </button></td></tr>');
        }else{
            if($('#result_type').find(":selected").text()=='Complex Structure' ||$('#result_type').find(":selected").text()=='Dynamics'){
                $('#myTable').find('tbody').append('<tr title='+truename+'><td><select class="tableselect">   <option value="AND">AND</option>   <option value="OR">OR</option>   <option value="NOT">NOT</option>  </select>  </td><td>   <select class="paren"> <option  value="(">(</option> <option selected="selected" value=""> </option></select></td>    <td>'+myclass+'</td><td>'+text+'</td><td><select class="ligselect"><option value="orto">Orthosteric Ligand</option><option value="alo">Allosteric Ligand</option><option value="other">Other</option></option><option value="all">All</option></select></td><td><select class="paren"><option value=")">)</option><option selected="selected" value=""></option></select></td><td>'+truename+'</td><td><button id="deleterow" class="btn btn-danger btn-sm" >  <span class="glyphicon glyphicon-trash" ></span> </button></td></tr>');
            }else{
                $('#myTable').find('tbody').append('<tr title='+truename+'><td><select class="tableselect">   <option value="AND">AND</option>   <option value="OR">OR</option>   <option value="NOT">NOT</option>  </select>  </td><td>   <select class="paren"> <option  value="(">(</option> <option selected="selected" value=""> </option></select></td>      <td>'+myclass+'</td><td>'+text+'</td><td><select class="ligselect"><option value="orto">Orthosteric Ligand</option><option value="alo">Allosteric Ligand</option></select></td><td><select class="paren"><option value=")">)</option><option selected="selected" value=""></option></select></td><td>'+truename+'</td><td><button id="deleterow" class="btn btn-danger btn-sm">  <span class="glyphicon glyphicon-trash"></span> </button></td></tr>');

            }
        }
        $('#myTable').find('.tableselect:first').empty().append('<option selected="selected" value=" "> </option>');
    }
});



$('#gotoadvsearch').on('click', function(){
    $('#myTable tbody tr').remove();

    counter+=1;
    if (counter%2==0){
        $('#gotoadvsearch').html('Go to Advanced Search');

    }else{
        $('#gotoadvsearch').html('Go to Simple Search');
    }
});




$('#result_type').on('change', function() {
    var opdef=$('<option></option>').val("orto").text("Orthoesteric ligand");
    var opdef2=$('<option></option>').val("alo").text("Allosteric ligand");

    if(this.value=='dynamics') {
        $('#hidden').show();
        $('#hiddenmodel').hide();
        var option = $('<option></option>').val("other").text("Other");
        var option2 = $('<option></option>').val("all").text("All");
        $('.ligselect').empty().append(opdef); 
        $('.ligselect').append(opdef2);
        $('.ligselect').append(option); 
        if ($('#gotoadvsearch').html().length!=21){ 
            $('.ligselect').append(option2);
        }

    } else if (this.value=='model') {
        $('#hiddenmodel').show();
        $('#hidden').hide();
        var option = $('<option></option>').val("other").text("Other");
        var option2 = $('<option></option>').val("all").text("All");
        $('.ligselect').empty().append(opdef); 
        $('.ligselect').append(opdef2);
        $('.ligselect').append(option);
        if ($('#gotoadvsearch').html().length!=21){ 
            $('.ligselect').append(option2);
        }
    } else {
        $('#hidden').hide();
        $('#hiddenmodel').hide();
        $('.ligselect').empty().append(opdef); 
        $('.ligselect').append(opdef2);
    } 
});


