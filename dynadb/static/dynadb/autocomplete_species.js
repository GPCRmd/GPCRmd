$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };
    $.widget( "ui.species_autocomplete", {
      _create: function() {
        var self = $(this);
        var page = "../get_specieslist/"
        var input1 = this.element,
          id = input1.attr("id")+"_autocomplete",
          name = input1.attr("name")+"_autocomplete";
        var input2 = $("#"+id);
        if (!input2.exists()) {
          var input2 = $( "<input />" )
          .attr("id",id)
          .attr("name",name)
          .attr("maxlength",200)
          .attr("placeholder","Homo Sapiens (HUMAN)")
          .attr("type","text")
          .val( "" )
          .css('width','300px')
          .prop("readonly",true)
          .insertAfter(input1);
          
          $(input2).set_readonly_color();
          
          
//           .addClass("ui-widget ui-widget-content ui-corner-left");
        }
        input2.autocomplete({
          delay: 3,
          minLength: 2,
          source: function(request, response) {
            var matcher = new RegExp( $.ui.autocomplete.escapeRegex(request.term), "i" );
            $.post(page,
            {
                term : request.term
            },
            function(data){
              jsonObj = [];
              $.each(data, function(i, item) {
                
                var text = item.screen_name;

                newitem = {
                  label: text.replace(
                    new RegExp("("+$.ui.autocomplete.escapeRegex(request.term)+")", "gi"),
                    "<strong>$1</strong>"),
                  value: text,
                  id: item.id
                };
                jsonObj.push(newitem);
              }); 
              response(jsonObj);
            }, 'json')

            .fail(function(xhr) {
              alert("Error "+ "\nStatus: " + xhr.status+"\n"+xhr.responseText);

            })


          },
          select: function( event, ui ) {
            input1.val(ui.item.id);
            self._trigger( "selected", event, {
              id: ui.item.id,
              name: ui.item.value
            });
          },
          change: function(event, ui) {
            
            if ( !ui.item ) {
              var text = $(this).val();
              var element = $(this);
              var matcher = new RegExp( "^" + $.ui.autocomplete.escapeRegex( text ) + "$", "i" );
              $.post(page,
            {
                term : text
            },
            function(data){
              var valid = false;
              
              if (data.length == 1 && data[0].screen_name.match( matcher )) {
                element.val(data[0].screen_name)
                input1.val(data[0].id);
                valid = true;
                return false;
              }
              if ( !valid ) {
                // remove invalid value, as it didn't match anything
                element.val( "" );
                input1.val( "" );
                return false;
              }
            
            }, 'json')

            .fail(function(xhr) {
              // remove invalid value in case of a connection issue
              element.val( "" );
              input1.val( "" );
              alert("Error "+ "\nStatus: " + xhr.status+"\n"+xhr.responseText);

            })

            }
          }
        });
          
          

       
        input2.autocomplete("instance")._renderItem = function( ul, item ) {
          return $( "<li></li>" )
            .data( "item.autocomplete", item )
            .append( "<a>" + item.label + "</a>" )
            .appendTo( ul );
        };
        

      }
    });
    

 
    $("[id='id_id_species'],[id|=id_form][id$='-id_species']").species_autocomplete();

});


