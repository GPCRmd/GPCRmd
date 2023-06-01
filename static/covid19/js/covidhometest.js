$(document).ready(function(){
var width = 2000;  
var height = 2000;  
var cluster = d3.layout.tree()        
    .size([height, width-200]);  
var diagonal = d3.svg.diagonal()        
    .projection (function(d) { return [d.y, d.x];});  
var svg = d3.select("body").append("svg")        
    .attr("width",width)        
    .attr("height",height)        
    .append("g")        
    .attr("transform","translate(100,0)");  

var root=$("#chart").data("tree_data")

var nodes = cluster.nodes(root);        
var links = cluster.links(nodes);        
var link = svg.selectAll(".link")              
   .data(links)              
   .enter().append("path")              
   .attr("class","link")              
   .attr("d", diagonal);         

console.log(nodes)
var node = svg.selectAll(".node")              
   .data(nodes.filter(function(d){ return d.name; }))
   .enter().append("g")              
   .attr("class","node")              
   .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });        
node.append("circle")              
   .attr("r", 4.5);        
node.append("text")              
   .attr("dx", function(d) { return d.children ? -8 : 8; })
   .attr("dy", 3)              
   .style("text-anchor", function(d) { return d.children ? "end" : "start"; })
   .style("font", "10px sans-serif")             
   .text( function(d){ return d.accession;});  


})
