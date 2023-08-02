$(document).ready( function () {

    $('[data-toggle="tooltip"]').tooltip(); 
    $('#table_id').DataTable(
        {
         "order": [],
        //"scrollY": 100,
        //"scrollX": true,
           "columnDefs": [ 
                        { "orderable": false, "searchable": false, "targets": 0 },   //Don't give option to sort or search by column 0
                        {"targets": 9,"visible": false},//Hide columns, only show if clicked
                        {"targets": 10,"visible": false},
                        {"targets": 11,"visible": false},
                        {"targets": 12,"visible": false},
                        {"targets": 13,"visible": false},
                        {"targets": 14,"visible": false},
                        {"targets": 15,"visible": false},
                        {"targets": 16,"visible": false},
                        {"targets": 17,"visible": false},
                        ],
          dom:"<'myfilter'f><'mylength'l>rtip",
          
        }
    );
    $('#loading', window.parent.document).css("display","none");
    $('#table_id').css("display","table");

    //toggle visbility of columns
    $('a.toggle-vis').on('click', function (e) {
        var table = $('#table_id').DataTable();
        e.preventDefault();
        // Get the column API object
        var column = table.column($(this).attr('data-column'));
        // Toggle the visibility
        column.visible(!column.visible());
    });
    
    $(".links a").click(function(){
        $("body").css("cursor","progress");
        $('*', window.parent.document).css("cursor","progress");
    }) ;


    // If '#...' in URL (searched from homepage) write the input in the searchbar
    // var path_list = window.location.href.split("/");
    // var path_list = document.referrer.split("/");
    var path_list = window.top.location.href.toString().split("/");
    if (path_list[5].indexOf('#') > -1)
    {
        var inputElement = path_list[5].replace('#','')
        // if spaces in url
        if (inputElement.indexOf('%20') > -1){
            inputElement=inputElement.replaceAll('%20',' ')
        }
        $('#table_id').DataTable().search(inputElement).draw();
    }
       
} );


