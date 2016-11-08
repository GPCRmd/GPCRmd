$('#hidden').hide();
$('#hiddenmodel').hide();

$(document).on('click', '.protein, .molecule, .compound', function(){
    var text = $(this).attr("name");
    var myclass= $(this).attr("class");
    var ligrec= $(this).attr("value");
    $('#myTable').find('tbody').append('<tr><td><select class="tableselect"><option value="and">AND</option></select></td><td>'+myclass+'</td><td>'+text+'</td><td><input id="ligandreceptor" type="checkbox" name="ligrec" value="some"> Is '+ligrec+' </td><td><button id="deleterow" >   Delete </button></td></tr>');

    $('#myTable').find('.tableselect:first').empty().append('<option selected="selected" value=""> </option>');

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
