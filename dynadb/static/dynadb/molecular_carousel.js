//code to hide or show the bootstrap carousel code 
var counter=0;
$('#hideall').hide();
$("#showall").click(function(){
    counter+=1;
    if (counter%2==0){
        $('#hideall').hide();
        $('#carouselhide').show();
        $('#showall').text('Show all');
    }else{
        $('#carouselhide').hide();
        $('#hideall').show();
        $('#showall').text('Show carousel');
    }
})
