$(document).ready(function() {
    
    // create session ID, submit query and get url to retrieve the query results
    $("#open_chembl").submit();
    $("#iframe1").load(function() {
        $("#chembl_results_url").submit();
    });
    
});


