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

        }
    );
    $('#table_id').css("display","table");
} );