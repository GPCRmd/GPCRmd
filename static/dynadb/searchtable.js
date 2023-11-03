$(document).ready( function () {

    $('[data-toggle="tooltip"]').tooltip(); 
    $('#table_id thead tr')
        .clone(true)
        .addClass('filters')
        .appendTo('#table_id thead');

    var table = $('#table_id').DataTable(
        {
            "order": [],
            orderCellsTop: true,
            //"scrollY": 100,
            //"scrollX": true,
            "columnDefs": [ 
                { "orderable": false, "searchable": false, "targets": 0 },   //Don't give option to sort or search by column 0
                // {"targets": 2,"visible": false},
                // {"targets": 4,"visible": false},
                // {"targets": 8,"visible": false},
                // // {"targets": 9,"visible": false},//Hide columns, only show if clicked
                // {"targets": 10,"visible": false},
                // {"targets": 11,"visible": false},
                // {"targets": 12,"visible": false},
                // {"targets": 13,"visible": false},
                // {"targets": 14,"visible": false},
                // {"targets": 15,"visible": false},
                // {"targets": 16,"visible": false},
                // {"targets": 17,"visible": false},
                { "orderable": false, "searchable": false, "targets": 18 },   //Don't give option to sort or search by column 0

            ],
            // dom:"<'myfilter'f><'mylength'l>rtip",
            dom: 'B<"mylength"l>rtip',
            buttons: [
                'copy', 'csv', 'excel', 'pdf', 'print'
            ],
            initComplete: function () {
                var api = this.api();
                // For each column
                api
                    .columns()
                    .eq(0)
                    .each(function (colIdx) {
                        if (!(colIdx==0 || colIdx==18)) {
                            // Set the header cell to contain the input element
                            var cell = $('.filters th').eq(
                                $(api.column(colIdx).header()).index()
                            );
                            var title = $(cell).text();
                            if ($(api.column(colIdx).header()).index() >= 0) {
                                $(cell).html('<input type="text" placeholder="' + title + '"/>');
                            }                            // On every keypress in this input
                            $(
                                'input',
                                $('.filters th').eq($(api.column(colIdx).header()).index())
                            )
                                .off('keyup change')
                                .on('change', function (e) {
                                    // Get the search value
                                    $(this).attr('title', $(this).val());
                                    var regexr = '({search})'; //$(this).parents('th').find('select').val();
        
                                    var cursorPosition = this.selectionStart;
                                    // Search the column for that value
                                    api
                                        .column(colIdx)
                                        .search(
                                            this.value != ''
                                                ? regexr.replace('{search}', '(((' + this.value + ')))')
                                                : '',
                                            this.value != '',
                                            this.value == ''
                                        )
                                        .draw();
                                })
                                .on('keyup', function (e) {
                                    e.stopPropagation();
        
                                    $(this).trigger('change');
                                    $(this)
                                        .focus()[0]
                                        .setSelectionRange(cursorPosition, cursorPosition);
                                });
                        };
                    });
                    
            },
        }
    );
    $('#loading', window.parent.document).css("display","none");
    $('#table_id').css("display","table");
    
    // Hide columns: 
    var l_hide = [2,4,8,10,11,12,13,14,15,16,17];
    var table = $('#table_id').DataTable();
    for (l in l_hide){
        var column = table.column(l_hide[l]);
        column.visible(!column.visible());
    }
    //toggle visbility of columns
    $('a.toggle-vis').on('click', function (e) {
        var table = $('#table_id').DataTable();
        e.preventDefault();
        this.classList.toggle("active"); 
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


