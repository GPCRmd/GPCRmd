google.charts.load('current', {packages: ['corechart', 'line']});
google.charts.setOnLoadCallback(drawBasic);

function drawBasic(rows,xlabel,ylabel) {

      var data = new google.visualization.DataTable();
      data.addColumn('number', xlabel);
      data.addColumn('number', ylabel);

      data.addRows(rows);
      var options = {
        hAxis: {
          title: xlabel
        },
        vAxis: {
          title: ylabel
        }
      };
      
      return [data,options];

    }


$('#doanalysis').click(function() {
    var ff=$('#from_frame').val();
    var tf=$('#to_frame').val();
    var an=$('#atom_name').val();
    var cut=$('#cutoff').val();
    var mean_per=$("input[name=saltymethod]:checked").val();
    console.log(cut,mean_per);
    $.ajax({
        type: "POST",
        data: { "frames[]": [ff,tf,an,cut,mean_per]},
        url:"./", 
        dataType: "json",
        success: function(data) {
            console.log(data);
            hbonds=data.hbonds;
            salty=data.salt_bridges;

	        //now the charges graph
            results_charges=drawBasic(data.charges,'Time','Interaction force');
            data_charges=results_charges[0];
            options_charges=results_charges[1];
            var chart_charges = new google.visualization.LineChart(document.getElementById('charges_chart_div'));
            chart_charges.draw(data_charges, options_charges);

            //draw the sasa graph
            results=drawBasic(data.sasa,'Time','SASA');
            data=results[0];
            options=results[1];
            var table='<center><table class="table table-condesed" style="width:40%;"><thead><tr><th>Donor<th>Acceptors (Frecuency)<tbody>';
            for (var property in hbonds) {
                if (hbonds.hasOwnProperty(property)) {
                    //table=table+'<tr> <td rowspan='+ hbonds[property].length.toString() + '>'+ property+'<td>'+hbonds[property][0];
                    table=table+'<tr> <td rowspan='+ hbonds[property].length.toString() + '>'+ property+'<td> '+hbonds[property][0][0]+' ('+hbonds[property][0][1]+'%)' ;
                    for (index = 1; index < hbonds[property].length; ++index) {
                        //table=table+'<tr><td>'+hbonds[property][index];
                        table=table+'<tr><td>'+hbonds[property][index][0]+' ('+hbonds[property][index][1]+'%)';
                    }
                }
            }
            table=table+'</table></center>';
            $('#hbonds').html(table);
            saltable='<center><table class="table table-condesed" style="width:40%;"><thead><tr><th>Residue 1<th> Residue 2<tbody>';
            for (bridge in salty) {
                saltable=saltable+'<tr><td>'+salty[bridge].split('--')[0]+'</td><td>'+salty[bridge].split('--')[1]+'</td></tr>';           
            }
            saltable=saltable+'</table></center>';
            $('#saltbridges').html(saltable);
            var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
            chart.draw(data, options);


        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            if (XMLHttpRequest.readyState == 4) {
                var responsetext = XMLHttpRequest.responseText;

                alert(textStatus.substr(0,1).toUpperCase()+textStatus.substr(1)+":\nStatus: " + XMLHttpRequest.textStatus+". "+errorThrown+".\n"+responsetext);
            }
            else if (XMLHttpRequest.readyState == 0) {
                alert("Connection error. Please, try later and check that your file is not larger than 50 MB.");
            }
            else {
                alert("Unknown error");
            }
        },
    });

  }
)

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
}); 
