$('#help').hide();
var counter=0;
$('#helpbutton').on('click', function(){
    counter=counter+1;
    if (counter%2==1){
        $('#help').show();
        $('#helpbutton').text('Hide Help');
    }else{
        $('#help').hide();
        $('#helpbutton').text('Show Help');
    }
});
