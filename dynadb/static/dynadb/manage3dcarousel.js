function show3dmol(counter){
  let molids=$('#moleculesids').html().split('%$!');
  let molnames=$('#moleculesnames').html().split('%$!');
  let myid=molids[counter];
  let myname=molnames[counter];
  let element = $('#container-02');
  let config = {backgroundColor:'white'};
  let viewer = $3Dmol.createViewer( element, config );
  let pdbUri = '/dynadb/molecule/id/'+myid+'/sdf';
  $('#namediv').html(myname);
  jQuery.ajax(pdbUri, { 
    success: function(data) {
      let v = viewer;
      v.addAsOneMolecule( data, "sdf" );                       //load data
      v.zoomTo();                                      //set camera
      v.render();                                      //render scene 
      v.zoom(1.2, 1000);                               //slight zoom 
    },
    error: function(hdr, status, err) {
      alert( "No 3D for that molecule. Sorry!");
    },
  });
};

$( document ).ready(function() {
  var counter=0;
  var molids=$('#moleculesids').html().split('%$!');
  
  show3dmol(counter);
  $('#movel').click(function(){
    counter=counter-1;
    if (counter<0){
      counter=counter + molids.length;
    }
    show3dmol(counter);
  });

  $('#mover').click(function(){
    counter=counter+1;
    if (counter==molids.length){
      counter=counter- molids.length;
    }
    show3dmol(counter);
  });
});
