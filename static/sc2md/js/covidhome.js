$(document).ready(function(){

    function linkMouseOut(d){
      d3.selectAll("path")
        .attr("stroke-width", "1px");
      $("body").css("cursor","auto");
    }



})
