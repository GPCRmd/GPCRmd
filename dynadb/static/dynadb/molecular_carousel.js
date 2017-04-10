//code to hide or show the bootstrap carousel code 
$( document ).ready(function() {
    $("#showall").click(function(){
        $('#carouselhide').hide();
        $('#hide3d').hide();
        $('#hideall').show();
    });

    $("#2d").click(function(){
       $('#hideall').hide();
       $('#hide3d').hide();
       $('#carouselhide').show();

    });

    $("#3d").click(function(){
       $('#carouselhide').hide();
       $('#hideall').hide();
       $('#hide3d').show();
    });
});
