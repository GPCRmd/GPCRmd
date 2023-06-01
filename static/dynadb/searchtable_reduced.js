$(document).ready( function () {

    $('[data-toggle="tooltip"]').tooltip(); 
    $('#table_id').DataTable(
        {
         "order": [],
        //"scrollY": 100,
        //"scrollX": true,
           "columnDefs": [ 
                        { "orderable": false, "searchable": false, "targets": 0 },   //Don't give option to sort or search by column 0
                        ],
          dom:"<'myfilter'f><'mylength'l>rtip",
            pageLength : 5,
          
        }
    );
    $('#loading', window.parent.document).css("display","none");
    $('#table_id').css("display","table");

    
    $(".links a").click(function(){
        $("body").css("cursor","progress");
        $('*', window.parent.document).css("cursor","progress");
    }) ;


} );


