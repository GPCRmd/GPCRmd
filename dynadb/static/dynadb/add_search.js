$('#hidden').hide();
$('#hiddenmodel').hide();
var counter=0;

$(document).on('click', '.protein, .molecule, .compound', function(){
    if (counter%2==0){
        var text = $(this).attr("name");
        var myclass= $(this).attr("class");
        var ligrec= $(this).attr("value");
        $('#myTable').find('thead').html('<tr><th>Boolean</th><th>Type</th><th>ID</th><th></th></tr>');
        $('#myTable').find('tbody').append('<tr><td><select class="tableselect"><option value="and">AND</option></select></td><td>'+myclass+'</td><td>'+text+'</td><td><input id="ligandreceptor" type="checkbox" name="ligrec" value="some"> Is '+ligrec+' </td><td><button id="deleterow" > Delete </button></td></tr>');

        $('#myTable').find('.tableselect:first').empty().append('<option selected="selected" value=" "> </option>');

    }else{
        var text = $(this).attr("name");
        var myclass= $(this).attr("class");
        var ligrec= $(this).attr("value");
        $('#myTable').find('thead').html('<tr><th>Boolean</th><th>  </th><th>Type</th><th>ID</th><th></th></tr>');
        $('#myTable').find('tbody').append('<tr><td><select class="tableselect">   <option value="AND">AND</option>   <option value="OR">OR</option>   <option value="NOT">NOT</option>  </select>  </td><td>   <select class="paren"> <option  value="(">(</option> <option selected="selected" value=""> </option></select></td>      <td>'+myclass+'</td><td>'+text+'</td><td><input id="ligandreceptor" type="checkbox" name="ligrec" value="some"> Is '+ligrec+' </td><td><select class="paren"><option value=")">)</option><option selected="selected" value=""></option></select></td><td><button id="deleterow" >  Delete </button></td></tr>');

        $('#myTable').find('.tableselect:first').empty().append('<option selected="selected" value=" "> </option>');
    }

});



$('#gotoadvsearch').on('click', function(){
    $('#myTable tbody tr').remove();

    counter+=1;
    if (counter%2==0){
        $('#gotoadvsearch').html('Advanced Search');

    }else{
        $('#gotoadvsearch').html('Simple Search');
    }
});




$('#result_type').on('change', function() {
    if(this.value=='dynamics') {
        $('#hidden').show();
        $('#hiddenmodel').hide();
    } else if  (this.value=='model') {
        $('#hiddenmodel').show();
        $('#hidden').hide();
    } else {
        $('#hidden').hide();
        $('#hiddenmodel').hide();
    } 
});


