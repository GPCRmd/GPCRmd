function createAllErrors(formname,loadiv) {
    /*
    Function to avaluate if all the required fields have been properly fullfilled before submitting
    */
    var form = $("#"+formname),errorList = $( "ul.errorMessages");
    errorList.parent().hide()

    errorList.empty();
    errorcounter = 0;

    // Find all invalid and empty fields within the form.
    var wrongfields= ($('[form="'+formname+'"][required]').filter(function() { return this.value === ''; })).add($("[form='"+formname+"'][required]:invalid"));
    wrongfields.each( function( index, node ) {

        // Find the field's corresponding label
        var label = $( "label[for=" + node.id + "] "),
            // Opera incorrectly does not fill the validationMessage property.
            message = node.validationMessage || 'Invalid value.';

        labeltext = label.html() ? label.html() : $("#"+node.id).data('mylabel');
        errorList.append( "<li><span>" + labeltext + "</span>: " + message + "</li>" );
        errorcounter++
    });

    if (errorcounter){
        errorList.parent().show()
        $("#"+loadiv).hide()
        $("input[type=submit][form="+formname+"]").show()
    }
    else {
        $("#"+loadiv).show()
    }
    return !Boolean(errorcounter)
};