//function to autocomplete the user input
$('#protein22').autocomplete({ 
    source: function (request, response) { 
        $.getJSON("/dynadb/autocomplete/?q=" + request.term, function (data) { 
            goodata={};
            for (i = 0; i < data['results'].length; i++) {
                key=i.toString();
                goodata[key]= data['results'][i];
            }
            response(goodata);
        }); 
    } 
});
