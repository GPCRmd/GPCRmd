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
    $.ajax({
        type: "POST",
        data: { "frames[]": [ff,tf,an,cut,mean_per]},
        url:"./", 
        dataType: "json",
        success: function(data) {
            console.log(data);
            hbonds=data.hbonds;
            hbonds_np=data.hbonds_notprotein;
            salty=data.salt_bridges;

	        //now the charges graph
            results_charges=drawBasic(data.charges,'Time','Interaction force');
            data_charges=results_charges[0];
            options_charges=results_charges[1];
            var chart_charges = new google.visualization.LineChart(document.getElementById('charges_chart_div'));
            chart_charges.draw(data_charges, options_charges);

            //draw the sasa graph
            results=drawBasic(data.sasa,'Time (ns)','SASA (nm2)');
            data=results[0];
            options=results[1];
            var chart_charges = new google.visualization.LineChart(document.getElementById('charges_chart_div'));
            chart_charges.draw(data_charges, options_charges);

            var table='<center><table class="table table-condesed" style="width:90%;"><thead><tr><th>Donor<th>Acceptors (Frecuency)<tbody>';
            for (var property in hbonds) {
                if (hbonds.hasOwnProperty(property)) {
                    table=table+'<tr> <td rowspan='+ hbonds[property].length.toString() + '>'+ property+'<td> '+hbonds[property][0][0]+' ('+hbonds[property][0][1]+'%) <button class="showhb" data-atomindexes='+hbonds[property][0][2]+'$%$'+hbonds[property][0][3]+'>Show Hbond</button>' ;
                    for (index = 1; index < hbonds[property].length; ++index) {
                        table=table+'<tr><td>'+hbonds[property][index][0]+' ('+hbonds[property][index][1]+'%) <button class="showhb" data-atomindexes='+hbonds[property][index][2]+'$%$'+hbonds[property][index][3]+'>Show Hbond</button>';
                    }
                }
            }
            table=table+'</table></center>';
            $('#hbonds').html(table);


            var tablenp='<center><table class="table table-condesed" style="width:90%;"><thead><tr><th>Donor<th>Acceptors (Frecuency)<tbody>';
            for (var property in hbonds_np) {
                if (hbonds_np.hasOwnProperty(property)) {
                    tablenp=tablenp+'<tr> <td rowspan='+ hbonds_np[property].length.toString() + '>'+ property+'<td> '+hbonds_np[property][0][0]+' ('+hbonds_np[property][0][1]+'%) <button class="showhb" data-atomindexes='+hbonds_np[property][0][2]+'$%$'+hbonds_np[property][0][3]+'>Show Hbond</button>';
                    for (index = 1; index < hbonds_np[property].length; ++index) {
                        tablenp=tablenp+'<tr><td>'+hbonds_np[property][index][0]+' ('+hbonds_np[property][index][1]+'%) <button class="showhb" data-atomindexes='+hbonds_np[property][index][2]+'$%$'+hbonds_np[property][index][3]+'>Show Hbond</button>';
                    }
                }
            }
            tablenp=tablenp+'</table></center>';
            $('#hbondsnp').html(tablenp);


            var salt='<center><table class="table table-condesed" style="width:90%;"><thead><tr><th>Residue1<th>Residue2 (Frecuency%)<tbody>';
            for (var property in salty) {
                if (salty.hasOwnProperty(property)) {
                    salt=salt+'<tr> <td rowspan='+ salty[property].length.toString() + '>'+ property+'<td> '+salty[property][0][0]+' ('+salty[property][0][1]+'%) <button class="showhb" data-atomindexes='+salty[property][0][2]+'$%$'+salty[property][0][3]+'>Show Salt Bridge</button>';
                    for (index = 1; index < salty[property].length; ++index) {
                        salt=salt+'<tr><td>'+salty[property][index][0]+' ('+salty[property][index][1]+'%) <button class="showhb" data-atomindexes='+salty[property][index][2]+'$%$'+salty[property][index][3]+'>Show Salt Bridge</button>';
                    }
                }
            }
            salt=salt+'</table></center>';
            $('#saltbridges').html(salt);

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

$(document).ready(function() {
    $(document).on('click', '.showhb', function(){
        atomshb=$(this).data('atomindexes').split('$%$');
        atomshb=[[Number(atomshb[0]),Number(atomshb[1])]];
        console.log(atomshb);
    });
});

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
