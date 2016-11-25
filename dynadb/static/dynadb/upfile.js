function upload(event) {
    //fired when validate is clicked, performs a PDB checking.
    $("#pdbchecker2").prop("disabled",true);
    event.preventDefault();
    var data = new FormData($('#myform').get(0));
    $.ajax({
        url: "/dynadb/upload_pdb/",
        type: $(this).attr('method'),
        data: data,
        cache: false,
        processData: false,
        contentType: false,
        success: function(data) {
            if (data.message==''){
                sendpar();
            }else{
                alert(data.message);
                $("#pdbchecker2").prop("disabled",false);
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            $("#pdbchecker2").prop("disabled",false);
        }
    });
    return false;
}


$('#pdbchecker2').click(function(){
    $('form').unbind('submit').submit(upload);
}); 

