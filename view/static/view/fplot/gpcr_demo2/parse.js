
function parse(graph){
  var nodeMap = {};

  function addToMap(name, data) {
    var node = nodeMap[name], i;
    if (!node) {
      node = nodeMap[name] = data || {name: name, children: []};
      if (name.length) {
        node.parent = addToMap(name.substring(0, i = name.lastIndexOf(".")));
        node.parent.children.push(node);
        node.key = name.substring(i + 1);
      }
    }
    return node;
  };
  graph.nodeMap = nodeMap;
  //Build parents of nodes and add all tree-vertices to nodeMap
  if( !("nodes" in graph) ) graph.nodes = []; 
  graph.nodes
    .forEach(function(n){
      addToMap(n.name, n);
    });

  //Ensure that graph.nodes and nodeMap contains all node names mentioned in graph.edges
  graph.edges
    .forEach(function(edge){
      if(!(edge.name1 in nodeMap)){
        var newNode = {name:edge.name1};
        graph.nodes.push(newNode);
        addToMap(edge.name1, newNode);
      }
      if(!(edge.name2 in nodeMap)){
        var newNode = {name:edge.name2};
        graph.nodes.push(newNode);
        addToMap(edge.name2, newNode);
      }
    });

  graph.treeRoot = nodeMap[""];

  //Go through graph.edges and convert name1, name2, and frames to target and source object arrays
  graph.frames = [];

  graph.edges
    .forEach(function(edge,i){
      //Set source and target of edge
      edge.source = nodeMap[edge.name1];
      edge.target = nodeMap[edge.name2];
      edge.key = ""+i;

      //Add interaction frames
      edge.frames.forEach(function(f){
        while(graph.frames.length<=f) graph.frames.push([]);

        graph.frames[f].push(edge);
      });
    });

  console.log(graph.edges);

  return graph;
}


// Return a list of imports for the given array of nodes.
genLinks = function(nodes) {
  var map = {},
  imports = [];

  // Compute a map from name to node.
  nodes.filter(function(d){ return d.name!=undefined; }).forEach(function(d) {
    map[d.name.substring(d.name.lastIndexOf(".")+1)] = d;
  });

  // For each import, construct a link from the source to target node.
  nodes.filter(function(d){ return d.name==undefined; }).forEach(function(d) {
    while(imports.length<d.edgeEvo.length) 
      imports.push([]);

    d.edgeEvo.forEach(
        function(w,i){ 
          if(w>0.0) 
            imports[i].push({source: map[d.name1], target: map[d.name2], weight: w}); 
        } 
    );
      
  });

  console.log(imports);
  return imports;
}
