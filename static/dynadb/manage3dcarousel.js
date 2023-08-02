function show3dmol(counter){
  let molids=$('#moleculesids').html().split('%$!');
  let molnames=$('#moleculesnames').html().split('%$!');
  let molnumbers=$('#moleculesnumber').html().split('%$!');
  let myid=molids[counter];
  let myname=molnames[counter];
  let mymolnumber=molnumbers[counter]
  if (mymolnumber=="()"){
    mymolnumber="";
  }
  let element = $('#container-02');
  let config = {backgroundColor:'white'};
  let viewer = $3Dmol.createViewer( element, config );
  let pdbUri = '/dynadb/molecule/id/'+myid+'/sdf';
  $('#namediv').html(myname);
  $('#molnumdcarousel3d').text(mymolnumber);
  $("#linkmol").attr("href","/dynadb/molecule/id/"+myid).text("Molecule ID:"+myid);
  jQuery.ajax(pdbUri, { 
    success: function(data) {
      let v = viewer;
      console.log(data.split('\n').length);
      v.addAsOneMolecule( data, "sdf" );
      
      if (data.split('\n').length<15){
        myname=myname+' (This molecule may not have 3D image, probably because it is a monoatomic ion. Sorry!)'
        $('#namediv').html(myname);
      }
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

  $("#3d").click(function(){
      if (counter==0){
        console.log("Hi")
        show3dmol(counter);
      }
  });


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
