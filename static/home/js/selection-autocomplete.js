$.widget( "custom.catcomplete", $.ui.autocomplete, {
    _create: function() {
      this._super();
      this.widget().menu( "option", "items", "> :not(.ui-autocomplete-category)" );
    },
    _renderMenu: function( ul, items ) {
      var that = this,
        currentCategory = "";
      $.each( items, function( index, item ) {
        var li;
        if ( item.category != currentCategory ) {
          ul.append( "<li class='ui-autocomplete-category'>" + item.category + "</li>" );
          currentCategory = item.category;
        }
        li = that._renderItemData( ul, item );
        if ( item.category ) {
          li.attr( "aria-label", item.category + " : " + item.label );
        }
      });
    }
  });

$(function() {
    $("#selection-autocomplete").catcomplete({
        source: "/protein/autocomplete?type_of_selection=" + type_of_selection,
        minLength: 2,
        autoFocus: true,
        delay: 500,
        create: function(event, ui) { this.focus();return false; },
        focus: function(event, ui) { return false; },
        select: function(event, ui) {
            $( '#selection-autocomplete' ).val('');
            
            // redirect if select a target/family to browse
            if (type_of_selection == 'browse') {
                AddToSelection('targets', ui.item['type'], ui.item['id']);
                toggleButtonClass('selection-button'); // loading effect on button
                setTimeout(function(){window.location = '/' + ui.item['type'] + '/' + ui.item['slug'];}, 200);
            
            } else if (type_of_selection == 'gsinterface') {
                //custom for gsinterface
                AddToSelection('targets', ui.item['type'], ui.item['id']);
                toggleButtonClass('selection-button'); // loading effect on button
                setTimeout(function(){window.location = '/interaction/gsinterface/' + ui.item['slug'];}, 200);
            
            } else {
                // add to selection
                AddToSelection(type_of_selection, ui.item['type'], ui.item['id']);                
                // redirect the user if only one target can be selected
                if (type_of_selection == 'reference' && redirect_on_select == 'True') {
                    toggleButtonClass('selection-button'); // loading effect on button
                    setTimeout(function(){window.location = redirect_url;}, 200);
                }
            }

            return false;
        }
    }).data("custom-catcomplete")._renderItem = function (ul, item) {
        return $("<li></li>")
        .data("item.autocomplete", item)
        .append("<a>" + item.label + "</a>")
        .appendTo(ul);
    };
});