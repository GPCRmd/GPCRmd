$(document).ready( function () {

    $('#tb_submission thead tr')
        .clone(true)
        .addClass('filters')
        .appendTo('#tb_submission thead');

    var table = $('#tb_submission').DataTable(
        {
            "order": [],
            autoWidth: false,
            orderCellsTop: true,
            //"scrollY": 100,
            //"scrollX": true,
            "columnDefs": [ 
                { width: '50px', target: 1 },
                { width: '50px', target: 2 },
                { width: '50px', target: 3 },
                { searchable: false, width: '50px', target: 4 },   //Don't give option to sort or search by column 0
                { searchable: false, width: '50px', target: 5 },
                { searchable: false, width: '50px', target: 6 },
                { orderable: false, width: '50px', searchable: false, target: 0 },   //Don't give option to sort or search by column 0
            ],
            // dom:"<'myfilter'f><'mylength'l>rtip",
            // dom: 'B<"mylength"l>rtip',
            // buttons: [
            //     'copy', 'csv', 'excel', 'pdf', 'print'
            // ],
            initComplete: function () {
                var api = this.api();
                // For each column
                api
                    .columns()
                    .eq(0)
                    .each(function (colIdx) {
                        if (!(colIdx==0 || colIdx==4 || colIdx==5 || colIdx==6)) {
                            // Set the header cell to contain the input element
                            var cell = $('.filters th').eq(
                                $(api.column(colIdx).header()).index()
                            );
                            var title = $(cell).text();
                            if ($(api.column(colIdx).header()).index() >= 0) {
                                $(cell).html('<input style="width:90px" type="text" placeholder="' + title + '"/>');
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
    
    }
);


