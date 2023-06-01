//code to hide or show the bootstrap carousel code 
$( document ).ready(function() {
    $("#showall").click(function(){
        $('#carouselhide').hide();
        $('#hide3d').hide();
        $('#hideall').show();
        $(this).addClass("active");
        $(this).siblings().removeClass("active");

    });

    $("#2d").click(function(){
       $('#hideall').hide();
       $('#hide3d').hide();
       $('#carouselhide').show();
       $(this).addClass("active");
       $(this).siblings().removeClass("active");
    });

    $("#3d").click(function(){
       $('#carouselhide').hide();
       $('#hideall').hide();
       $('#hide3d').show();
       $(this).addClass("active");
       $(this).siblings().removeClass("active");
    });
});
