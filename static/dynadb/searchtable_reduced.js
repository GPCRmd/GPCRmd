$(document).ready( function () {

    $('[data-toggle="tooltip"]').tooltip(); 
    $('#table_id').DataTable({
        pageLength : 5,
        lengthMenu: [0, 5, 10, 20],
        // "order": [],
        //"scrollY": 100,
        //"scrollX": true,
        //    columnDefs: [ 
        //                 { "orderable": false, "searchable": false, "targets": 0 },   //Don't give option to sort or search by column 0
        //                 ],
        dom:"rtip", //
          
        }
    );
    $('#loading', window.parent.document).css("display","none");
    $('#table_id').css("display","table");
    window.parent.parent.$('#parentbody').css('overflow', 'hidden');
    
    $(".links a").click(function(){
        $("body").css("cursor","progress");
        $('*', window.parent.document).css("cursor","progress");
    }) ;


} );


