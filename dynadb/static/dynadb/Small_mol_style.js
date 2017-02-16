
$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };


    $(document).find("[id|=molform]").each(function(){
    var numform=Number($(this).attr('id').split("-")[1]);
    if (numform =3){
        $(this).find("[id|=molform][id$='3'] 'a'").each(function(){
          $(this).css("color","#337ab7");
        });
    }
    });
    });

