$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };
    $(document).on('click',"[id='id_upload_button'],[id|=id_form][id$='-upload_button']",function(){
        var mainform = $("#small_molecule");
        var protform = $(this).parents("[id|=protform]");
        var molval = protform.find("[id='id_molsdf'],[id|=id_form][id$='-molsdf']").val();
        $(mainform).ajaxSubmit({
            url: "../generate_inchi/",
            type: 'POST',
            dataType:'json',
            success: function(data) {
                alert("do some stuff");
            },
            error: function(xhr,status,msg){
                alert(status.substr(0,1).toUpperCase()+status.substr(1)+":\nStatus: " + xhr.status+". "+msg+".\n"+xhr.responseText);
            }
        });
    });
        
});