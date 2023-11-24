$(document).ready(function(){
    // Close default toolkit
    document.getElementById("analysis_fplot_pan").click();

    // Open the Pockets section: 
    document.getElementById("analysis_pockets_pan").click();

    // Scroll right panel to the pockets toolkit
    setTimeout(function(){
        var topPos = document.getElementById('analysis_pockets_pan').offsetTop;
        document.getElementById('rightPanelID').scrollTop = topPos-10;
    }, 1000);

    // Sort by Mean volume: 
    var xpath = "//th[text()='Mean volume']";
    var matchingElement = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    matchingElement.click();
    matchingElement.click();

    // Get pockets ids & table data
    var pockets_id = $(".str_file").data("pocket_id");
    var table = document.getElementById("analysis_pockets_table");

    // Select the pockets
    setTimeout(function(){
        var trs = table.getElementsByTagName("tbody")[0].getElementsByTagName("tr");
        for (var i = 0; i < trs.length; i++) {
            if (pockets_id.includes(trs[i]._DT_RowIndex)) {
                trs[i].childNodes[0].click();
            } 
        }
    }, 1000);
    // Click on plot
    setTimeout(function(){
        document.getElementById("pocket_plot_button").click();
    }, 1500);
});