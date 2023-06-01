$(document).ready( function () {
    $('#table_id').DataTable(
        {
         "order": [],
        //"scrollY": 100,
        //"scrollX": true,
          "stripeClasses": [],
           "columnDefs": [ 
                        { "orderable": false, "searchable": false, "targets": 0 

                        },   //Don't give option to sort or search by column 0
                        { 
                          "className": 'dt-body-nowrap',
                          "targets": [1,5,6,9]
                        },                        
                        ],
          dom:"<'myfilter'f><'mylength'l>rtip"

        }
    );
    $('#table_id').css("display","table");

} );


