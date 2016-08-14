$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };
    $.widget( "ui.combobox", {
      _create: function() {
        var self = this;
        var select = this.element.hide(),
          selected = select.children( ":selected" ),
          value = selected.val() ? selected.text() : "",
          id = select.attr("id")+"_autocomplete",
          name = select.attr("name")+"_autocomplete";
        var input = $("#"+id)
        if (!input.exists()) {
        var input = $( "<input />" )
          .attr("id",id)
          .attr("name",name)
          .val( value )
          .css('height','25px')
          .css('width','250px')
          .css('vertical-align','middle')
          .insertAfter( select )
          .addClass("ui-widget ui-widget-content ui-corner-left");
        }
        input.autocomplete({
          delay: 0,
          minLength: 0,
          source: function(request, response) {
            var matcher = new RegExp( $.ui.autocomplete.escapeRegex(request.term), "i" );
            response( select.children("option" ).map(function() {
              var text = $( this ).text();
              if ( this.value && ( !request.term || matcher.test(text) ) )
                return {
                  label: text.replace(
                    new RegExp(
                      "(?![^&;]+;)(?!<[^<>]*)(" +
                      $.ui.autocomplete.escapeRegex(request.term) +
                      ")(?![^<>]*>)(?![^&;]+;)", "gi"),
                    "<strong>$1</strong>"),
                  value: text,
                  option: this
                };
            }) );
          },
          select: function( event, ui ) {
            ui.item.option.selected = true;
            self._trigger( "selected", event, {
              item: ui.item.option
            });
          },
          change: function(event, ui) {
            if ( !ui.item ) {
              var matcher = new RegExp( "^" + $.ui.autocomplete.escapeRegex( $(this).val() ) + "$", "i" ),
              valid = false;
              select.children( "option" ).each(function() {
                if ( this.value.match( matcher ) ) {
                  this.selected = valid = true;
                  return false;
                }
              });
//               if ( !valid ) {
//                 // remove invalid value, as it didn't match anything
//                 $( this ).val( "" );
//                 select.val( "" );
//                 return false;
//               }
            }
          }
        });
          
          

       
        input.autocomplete("instance")._renderItem = function( ul, item ) {
          return $( "<li></li>" )
            .data( "item.autocomplete", item )
            .append( "<a>" + item.label + "</a>" )
            .appendTo( ul );
        };
        
        var id2 = id +'_btn',
        name2 = name+'_btn';
        var button = $("#"+id2)
        if (!button.exists()) {
          var button = $( "<button> </button>" )
          .attr('id',id2)
          .attr('name',name2)
          .attr( "tabIndex", -1 )
          .attr( "title", "Show All Items" )
          .attr( "type", "button" )
          .insertAfter(input)
          .removeClass( "ui-corner-all" )
          .addClass( "ui-corner-right ui-button-icon" )
          .css('height','25px')
          .css('vertical-align','middle');
        };
        button.uibutton({
            icons: {
              primary: "ui-icon-triangle-1-s"
            },
            text: false
        });
        button.click(function() {
          // close if already visible
          if (input.autocomplete("widget").is(":visible")) {
            input.autocomplete("close");
            return;
          }
          // pass empty string as value to search for, displaying all results
          input.autocomplete("search", "");
          input.focus();
        });
        

      }
    });
    

 
    $("[id='id_id_species'],[id|=id_form][id$='-id_species']").combobox();

});


