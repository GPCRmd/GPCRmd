$(document).on('click', '.protein, .molecule, .compound', function(){
    var text = $(this).attr("name");
    var myclass= $(this).attr("class");
    console.log(text,myclass);
    $('#myTable').find('tbody').append('<tr><td><select class="tableselect" ><option value="or">OR</option><option value="and">AND</option><option value="not">NOT</option></select></td><td>'+myclass+'</td><td>'+text+'</td><td><button id="deleterow" >Delete</button></td></tr>');
});
