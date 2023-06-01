$(document).ready( function () {
    var pre_search=$("#table_id").data("pre_search");
    var pre_search_deco=decodeURIComponent(pre_search.replace(/\+/g, " "));
    var pre_search_text="";
    if (pre_search_deco){
      pre_search_text=pre_search_deco;
    }
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
          dom:"<'myfilter'f><'mylength'l>rtip",
          "search": {
            "search": pre_search_text
            }

        }
    );
    $('#table_id').css("display","table");

} );


