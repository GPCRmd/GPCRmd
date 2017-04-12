$('.ortoligand').click(function(){
  let myid=this.id;
  let element = $('#container-01');
  let config = { backgroundColor: 'white' };
  let viewer = $3Dmol.createViewer( element, config );
  let pdbUri = '/dynadb/molecule/id/'+myid+'/sdf';
  jQuery.ajax( pdbUri, { 
    success: function(data) {
      let v = viewer;
      v.addAsOneMolecule( data, "sdf" );                       //load data
      v.zoomTo();                                      //set camera
      v.render();                                      //render scene 
      v.zoom(1.2, 1000);                               //slight zoom 
    },
    error: function(hdr, status, err) {
      alert( "Unable to generate 3D view of this element.");
    },
  });
});
