function upload(event) {
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
            sendpar();
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            $("#pdbchecker2").prop("disabled",false);
        }
    });
    return false;
}

$(function() {
    $('form').submit(upload);
});
