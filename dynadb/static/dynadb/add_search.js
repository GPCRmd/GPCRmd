$('#hidden').show();
$('#hiddenmodel').hide();
$('#hiddenbar').hide();
var counter=0;

$(document).on({
    mouseenter: function () {
        $("#lightup").css("background-color", "#5cb85c"); //#609dd2

    },
    mouseleave: function () {
        $("#lightup").css("background-color", "#d9edf7");
    }
}, ".protein, .molecule, .compound"); //pass the element as an argument to .on


$(document).on('click', '.protein, .molecule, .compound', function(){
    //when a "add to search" button is clicked that element is added to the right panel. Depending on the selection of advanced or simple search options, the element information is displayed differently (with or without parenthesis) 
    $('[data-toggle="tooltip"]').tooltip();
    if (counter%2==0){
        var text = $(this).attr("name");
        var nameandid=text.split('%');
        var id=nameandid[0];
        var truename=nameandid[1].replace('!','-');
        console.log(truename);
        text=id;
        var myclass= $(this).attr("class");
        var ligrec= $(this).attr("value");
        $('#myTable').find('thead').html('<tr><th>Boolean</th><th>Type</th><th>ID</th> <th></th> <th>Name</th> <th></th> </tr>');
        if (myclass=='protein'){
            $('#myTable').find('tbody').append('<tr data-toggle="tooltip" title='+truename+'><td><select class="tableselect"><option value="and">AND</option></select></td><td>'+myclass+'</td><td>'+text+'</td><td><input id="ligandreceptor" type="checkbox" name="ligrec" value="some" checked> Is '+ligrec+' </td><td>'+truename+'</td><td><button id="deleterow" class="btn btn-danger btn-sm"> <span class="glyphicon glyphicon-trash"></span> </button></td></tr>');
        }else{
            if($('#result_type').find(":selected").text()=='Complex Structure' ||$('#result_type').find(":selected").text()=='Dynamics'){
                $('#myTable').find('tbody').append('<tr data-toggle="tooltip" title='+truename+'><td><select class="tableselect"><option value="and">AND</option></select></td><td>'+myclass+'</td><td>'+text+'</td><td><select class="ligselect"><option value="orto">Orthosteric Ligand</option><option value="alo">Allosteric Ligand</option><option value="other">Other</option><option value="all" selected="selected">All</option></select> </td><td>'+truename+'</td><td><button id="deleterow" class="btn btn-danger btn-sm"> <span class="glyphicon glyphicon-trash"></span> </button></td></tr>');
            }else{
                $('#myTable').find('tbody').append('<tr data-toggle="tooltip" title='+truename+'><td><select class="tableselect"><option value="and">AND</option></select></td><td>'+myclass+'</td><td>'+text+'</td><td><select class="ligselect"><option value="orto">Orthosteric Ligand</option><option value="alo">Allosteric Ligand</option><option value="all" selected="selected">All</option></select> </td><td>'+truename+'</td><td><button id="deleterow" class="btn btn-danger btn-sm"> <span class="glyphicon glyphicon-trash"></span> </button></td></tr>');
            }

        }

        $('#myTable').find('.tableselect:first').empty().append('<option selected="selected" value=" "> </option>');

    }else{ //ADVANCED SEARCH SELECTED
        var text = $(this).attr("name");
        var nameandid=text.split('%');
        var id=nameandid[0];
        var truename=nameandid[1].replace('!','-');
        text=id;
        var myclass= $(this).attr("class");
        var ligrec= $(this).attr("value");
        $('#myTable').find('thead').html('<tr><th>Boolean</th><th>  </th><th>Type</th><th>ID</th> <th></th> <th></th> <th>Name</th> </tr>');
        if (myclass=='protein'){
            $('#myTable').find('tbody').append('<tr data-toggle="tooltip" title='+truename+'><td><select class="tableselect">   <option value="AND">AND</option>   <option value="OR">OR</option>   <option value="NOT">NOT</option>  </select>  </td><td>   <select class="paren"> <option  value="(">(</option> <option selected="selected" value=""> </option></select></td>      <td>'+myclass+'</td><td>'+text+'</td><td><input id="ligandreceptor" type="checkbox" name="ligrec" value="some" checked> Is '+ligrec+' </td><td><select class="paren"><option value=")">)</option><option selected="selected" value=""></option></select></td><td>'+truename+'</td><td><button id="deleterow" class="btn btn-danger btn-sm" >  <span class="glyphicon glyphicon-trash"></span> </button></td></tr>');
        }else{
            if($('#result_type').find(":selected").text()=='Complex Structure' ||$('#result_type').find(":selected").text()=='Dynamics'){
                $('#myTable').find('tbody').append('<tr data-toggle="tooltip" title='+truename+'><td><select class="tableselect">   <option value="AND">AND</option>   <option value="OR">OR</option>   <option value="NOT">NOT</option>  </select>  </td><td>   <select class="paren"> <option  value="(">(</option> <option selected="selected" value=""> </option></select></td>    <td>'+myclass+'</td><td>'+text+'</td><td><select class="ligselect"><option value="orto">Orthosteric Ligand</option><option value="alo">Allosteric Ligand</option><option value="other">Other</option></option><option value="all" selected="selected">All</option></select></td><td><select class="paren"><option value=")">)</option><option selected="selected" value=""></option></select></td><td>'+truename+'</td><td><button id="deleterow" class="btn btn-danger btn-sm" >  <span class="glyphicon glyphicon-trash" ></span> </button></td></tr>');
            }else{
                $('#myTable').find('tbody').append('<tr data-toggle="tooltip" title='+truename+'><td><select class="tableselect">   <option value="AND">AND</option>   <option value="OR">OR</option>   <option value="NOT">NOT</option>  </select>  </td><td>   <select class="paren"> <option  value="(">(</option> <option selected="selected" value=""> </option></select></td>      <td>'+myclass+'</td><td>'+text+'</td><td><select class="ligselect"><option value="orto">Orthosteric Ligand</option><option value="alo">Allosteric Ligand</option><option value="all" selected="selected">All</option></select></td><td><select class="paren"><option value=")">)</option><option selected="selected" value=""></option></select></td><td>'+truename+'</td><td><button id="deleterow" class="btn btn-danger btn-sm">  <span class="glyphicon glyphicon-trash"></span> </button></td></tr>');

            }
        }
        $('#myTable').find('.tableselect:first').empty().append('<option selected="selected" value=" "> </option>');
    }
});





$('#gotoadvsearch').on('click', function(){
    //steps to perform when changing between adv and simpmle search.
    counter+=1;
    bigarray=tabledata(counter);
    $('#myTable tbody tr').remove();
    if (counter%2==0){
        if (bigarray.length > 1){
            recycletable(counter,bigarray);
        }
        $('#gotoadvsearch').html('Go to Advanced Search'); //from adv to simple
        $('#crazycolor').css("background-color", "transparent");

    }else{
        if (bigarray.length > 1){
            recycletable(counter,bigarray);
        }
        $('#gotoadvsearch').html('Go to Simple Search'); //from simple to adv
        $('#crazycolor').css("background-color", "#e6e6ff");
    }
});


$('#result_type').on('change', function() {
    //When changing between adv and simple search, this function changes the available options to the user
    var opdef=$('<option></option>').val("orto").text("Orthosteric ligand");
    var opdef2=$('<option></option>').val("alo").text("Allosteric ligand");

    if(this.value=='dynamics') {
        $('#hidden').show();
        $('#hiddenmodel').hide();
        var option = $('<option></option>').val("other").text("Other");
        var option2 = $('<option></option>').val("all").text("All");
        $('.ligselect').empty().append(opdef); 
        $('.ligselect').append(opdef2);
        $('.ligselect').append(option); 
        $('.ligselect').append(option2);

    } else if (this.value=='model') {
        $('#hiddenmodel').show();
        $('#hidden').hide();
        var option = $('<option></option>').val("other").text("Other");
        var option2 = $('<option></option>').val("all").text("All");
        $('.ligselect').empty().append(opdef); 
        $('.ligselect').append(opdef2);
        $('.ligselect').append(option);
        $('.ligselect').append(option2);
    } else {
        $('#hidden').hide();
        $('#hiddenmodel').hide();
        var option2 = $('<option></option>').val("all").text("All");
        $('.ligselect').empty().append(opdef); 
        $('.ligselect').append(opdef2);
        $('.ligselect').append(option2);
    } 
});

function tabledata(countertt){
    //gets the data from the right panel and returns it as an array of arrays.
    var bigarray=[];
    var openpar=[];
    var closingpar=[]
    var flag=0; //means no errors
    if (countertt%2==0){
        var typeofsearch='advanced';
        $("#myTable tr").each(function () {
            var postarray=[];
            var counter=0;
            $('td', this).each(function () {
                if (counter==0){
                    var drop=$(this).find(":selected").text();
                    postarray.push(drop);

                }else if (counter==1) {
                    var drop=$(this).find(":selected").text();
                    postarray.push(drop);
                    openpar.push(drop);

                }else{
                    if (counter==4){
                        if (postarray[2]=='protein') {
                            var isligrec=$(this).find('[type=checkbox]').prop('checked');
                            postarray.push(isligrec);
                        }else{
                            var drop=$(this).find(":selected").val();
                            postarray.push(drop);  
                        }
                    }else if (counter==5) {
                        var drop=$(this).find(":selected").text();
                        postarray.push(drop);
                        closingpar.push(drop);
                    } else {
                        var value = $(this).text(); //var value = $(this).text();
                        postarray.push(value);
                    }
                }
                counter=counter+1;
            })
            bigarray.push(postarray);
        })

    }else{
        //pick simple search information
        var typeofsearch='simple';
        $("#myTable tr").each(function () {
            var postarray=[];
            var counter=0;
            $('td', this).each(function () {
                if (counter==0){
                    var drop=$(this).find(":selected").text();
                    console.log('and or ',drop);
                    postarray.push(drop);
                } else {
                    if (counter==3){
                        if(postarray[1]=='protein'){
                            var isligrec=$(this).find('[type=checkbox]').prop('checked');
                            postarray.push(isligrec); 
                            console.log('isrece?',isligrec);   
                        }else{
                            var drop=$(this).find(":selected").val();
                            postarray.push(drop); 
                            console.log('lig type',drop);
                        }

                    } else {
                        var value = $(this).text(); //var value = $(this).text();
                        console.log(counter,value);
                        postarray.push(value);
                    }
                }
                counter=counter+1;
            })
            bigarray.push(postarray);
        })
    } //else ends
    return bigarray;
}
function recycletable(counterRT,bigarray){
    //allows the user to change between advanced and simple search and save the elements previously added to the right panel.
    $('#myTable').find('thead').html('<tr><th>Boolean</th><th>Type</th><th>ID</th> <th></th> <th>Name</th> <th></th> </tr>');
    if (counterRT%2==0){
        for (i=1;i<bigarray.length;i++){
            if (bigarray[i][2]=='protein'){
                $('#myTable').find('tbody').append('<tr data-toggle="tooltip" title='+bigarray[i][6]+'><td><select class="tableselect"><option value="and">AND</option></select></td><td>'+bigarray[i][2]+'</td><td>'+bigarray[i][3]+'</td><td><input id="ligandreceptor" type="checkbox" name="ligrec" value="blah"> Is GPCR </td><td>'+bigarray[i][6]+'</td><td><button id="deleterow" class="btn btn-danger btn-sm"> <span class="glyphicon glyphicon-trash"></span> </button></td></tr>');
            }else{
                if($('#result_type').find(":selected").text()=='Complex Structure' ||$('#result_type').find(":selected").text()=='Dynamics'){
                    $('#myTable').find('tbody').append('<tr data-toggle="tooltip" title='+bigarray[i][6]+'><td><select class="tableselect"><option value="and">AND</option></select></td><td>'+bigarray[i][2]+'</td><td>'+bigarray[i][3]+'</td><td><select class="ligselect"><option value="orto">Orthosteric Ligand</option><option value="alo">Allosteric Ligand</option><option value="other">Other</option><option value="all">All</option></select> </td><td>'+bigarray[i][6]+'</td><td><button id="deleterow" class="btn btn-danger btn-sm"> <span class="glyphicon glyphicon-trash"></span> </button></td></tr>');
                }else{
                    $('#myTable').find('tbody').append('<tr data-toggle="tooltip" title='+bigarray[i][6]+'><td><select class="tableselect"><option value="and">AND</option></select></td><td>'+bigarray[i][2]+'</td><td>'+bigarray[i][3]+'</td><td><select class="ligselect"><option value="orto">Orthosteric Ligand</option><option value="alo">Allosteric Ligand</option><option value="all">All</option></select> </td><td>'+bigarray[i][6]+'</td><td><button id="deleterow" class="btn btn-danger btn-sm"> <span class="glyphicon glyphicon-trash"></span> </button></td></tr>');
                }

            }
        } //endfor

        $('#myTable').find('.tableselect:first').empty().append('<option selected="selected" value=" "> </option>');

    }else{
        $('#myTable').find('thead').html('<tr><th>Boolean</th><th>  </th><th>Type</th><th>ID</th> <th></th> <th></th> <th>Name</th> </tr>');
        for (i=1;i<bigarray.length;i++){
            if (bigarray[i][1]=='protein'){
                $('#myTable').find('tbody').append('<tr data-toggle="tooltip" title='+bigarray[i][4]+'><td><select class="tableselect">   <option value="AND">AND</option>   <option value="OR">OR</option>   <option value="NOT">NOT</option>  </select>  </td><td>   <select class="paren"> <option  value="(">(</option> <option selected="selected" value=""> </option></select></td>      <td>'+bigarray[i][1]+'</td><td>'+bigarray[i][2]+'</td><td><input id="ligandreceptor" type="checkbox" name="ligrec" value="some"> Is GPCR </td><td><select class="paren"><option value=")">)</option><option selected="selected" value=""></option></select></td><td>'+bigarray[i][4]+'</td><td><button id="deleterow" class="btn btn-danger btn-sm" >  <span class="glyphicon glyphicon-trash"></span> </button></td></tr>');
            }else{
                if($('#result_type').find(":selected").text()=='Complex Structure' ||$('#result_type').find(":selected").text()=='Dynamics'){
                    $('#myTable').find('tbody').append('<tr data-toggle="tooltip" title='+bigarray[i][4]+'><td><select class="tableselect">   <option value="AND">AND</option>   <option value="OR">OR</option>   <option value="NOT">NOT</option>  </select>  </td><td>   <select class="paren"> <option  value="(">(</option> <option selected="selected" value=""> </option></select></td>    <td>'+bigarray[i][1]+'</td><td>'+bigarray[i][2]+'</td><td><select class="ligselect"><option value="orto">Orthosteric Ligand</option><option value="alo">Allosteric Ligand</option><option value="other">Other</option></option><option value="all">All</option></select></td><td><select class="paren"><option value=")">)</option><option selected="selected" value=""></option></select></td><td>'+bigarray[i][4]+'</td><td><button id="deleterow" class="btn btn-danger btn-sm" >  <span class="glyphicon glyphicon-trash" ></span> </button></td></tr>');
                }else{
                    $('#myTable').find('tbody').append('<tr data-toggle="tooltip" title='+bigarray[i][4]+'><td><select class="tableselect">   <option value="AND">AND</option>   <option value="OR">OR</option>   <option value="NOT">NOT</option>  </select>  </td><td>   <select class="paren"> <option  value="(">(</option> <option selected="selected" value=""> </option></select></td>      <td>'+bigarray[i][1]+'</td><td>'+bigarray[i][2]+'</td><td><select class="ligselect"><option value="orto">Orthosteric Ligand</option><option value="alo">Allosteric Ligand</option><option value="all">All</option></select></td><td><select class="paren"><option value=")">)</option><option selected="selected" value=""></option></select></td><td>'+bigarray[i][4]+'</td><td><button id="deleterow" class="btn btn-danger btn-sm">  <span class="glyphicon glyphicon-trash"></span> </button></td></tr>');

                }
            }
        }
        $('#myTable').find('.tableselect:first').empty().append('<option selected="selected" value=" "> </option>');    
    }
}

