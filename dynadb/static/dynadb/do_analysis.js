google.charts.load('current', {packages: ['corechart', 'line']});
google.charts.setOnLoadCallback(drawBasic);

function drawBasic(rows) {

      var data = new google.visualization.DataTable();
      data.addColumn('number', 'Time');
      data.addColumn('number', 'SAS');

      data.addRows(rows);
      var options = {
        hAxis: {
          title: 'Time'
        },
        vAxis: {
          title: 'SAS'
        }
      };
      
      return [data,options];

    }


$('#doanalysis').click(function() {
    var ff=$('#from_frame').val();
    var tf=$('#to_frame').val();
    var an=$('#atom_name').val();
    $.ajax({
        type: "POST",
        data: { "frames[]": [ff,tf,an]},
        url:"./", 
        dataType: "json",
        success: function(data) {
            console.log(data);
            hbonds=data.hbonds;
            results=drawBasic(data.sasa);
            data=results[0];
            options=results[1];
            $('#hbonds').html(hbonds);
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
    //~ rows=[
        //~ [0, 0],   [1, 10],  [2, 23],  [3, 17],  [4, 18],  [5, 9],
        //~ [6, 11],  [7, 27],  [8, 33],  [9, 40],  [10, 32], [11, 35],
        //~ [12, 30], [13, 40], [14, 42], [15, 47], [16, 44], [17, 48],
        //~ [18, 52], [19, 54], [20, 42], [21, 55], [22, 56], [23, 57],
        //~ [24, 60], [25, 50], [26, 52], [27, 51], [28, 49], [29, 53],
        //~ [30, 55], [31, 60], [32, 61], [33, 59], [34, 62], [35, 65],
        //~ [36, 62], [37, 58], [38, 55], [39, 61], [40, 64], [41, 65],
        //~ [42, 63], [43, 66], [44, 67], [45, 69], [46, 69], [47, 70],
        //~ [48, 72], [49, 68], [50, 66], [51, 65], [52, 67], [53, 70],
        //~ [54, 71], [55, 72], [56, 73], [57, 75], [58, 70], [59, 68],
        //~ [60, 64], [61, 60], [62, 65], [63, 67], [64, 68], [65, 69],
        //~ [66, 70], [67, 72], [68, 75], [69, 80]
      //~ ];

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
