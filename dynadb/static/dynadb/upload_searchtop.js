function dostuff(event) {
    event.preventDefault();
    $("#pdbchecker1").prop("disabled",true);
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
                searchtop();
            }else{
                alert(data.message);
                $("#pdbchecker1").prop("disabled",false);
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            $("#pdbchecker1").prop("disabled",false);
        }
    });
    return false;
}

$("#pdbchecker1").click(function() {
    $("form").unbind('submit').submit(dostuff);
});
