///// HTML templates and depending functions
function obtain_mutations(id){
  //Obtain the mutations present in the current alignment
  unisequence = $("#unisequence"+id).val()
  container = $("#alignment"+id)
  alignment = container.attr('alig_fa')
  $("#mutations_error"+id).hide();
  $("#nomuts"+id).hide();
  subdata = {    
    'sequence': unisequence,
    'alignment' : alignment,
  }
  $.ajax({
      url: '../../protein/get_mutations/',
      method : 'POST',
      data: subdata,
      data_type: 'json',
      success: function(data){
        //Remove anyprevious mutations
        $(".mutentry"+id).remove()
        // Append newly found mutations to form
        muts=data['mutations']
        for (i in muts){
          mut = muts[i];
          add_mut_entry(id, mut['resid'], mut['from'], mut['to'])
        }
        //IF no mutations, display alert
        if (muts.length == 0){
          $("#nomuts"+id).show();
        }
        //Update mutatoins number
        update_mutnumber(id);
      },
      error: function(){
        $("#mutations_error"+id).show();
      },
      complete: function(){
      },
      timeout: 600000          
  });
}


function align_sequences(id) {
  //Align the two submitted sequences througth request, and place alignment into corresponding field
  //Extract current segment info
  data_post = {
      'unisequence' : $('#unisequence'+id).val(),
      'submission_id' : $('#submission_id').val(),
      'segnums' : ''
    };
  segnums = []
  redthings = []
  $(".segentry"+id).each(function(){
    segnum = $(this).data('segnum')
    chain_in = $('#'+segnum+"chain"+id)
    seg_in = $('#'+segnum+"segid"+id)
    from_in = $('#'+segnum+"from_resid"+id)
    to_in = $('#'+segnum+"to_resid"+id)
    data_post['chain'+segnum]= chain_in.val()
    data_post['segid'+segnum]= $('#'+segnum+"segid"+id).val()
    data_post['from'+segnum]= $('#'+segnum+"from_resid"+id).val()
    data_post['to'+segnum]= $('#'+segnum+"to_resid"+id).val()
    segnums.push(segnum) 
    redthings.push(chain_in,seg_in,from_in,to_in)
  })

  //Hide error stuff
  errordiv = $("#alignment_error"+id);
  for (var i = 0; i < redthings.length; i++) {
      redthings[i].removeClass('shadow_error')
  }
  $("#unisequence"+id).removeClass('shadow_error')
  errordiv.hide();


  data_post['segnums'] = segnums.join(',')

  $.ajax({
    type: 'POST',
    url: '../../get_alignment/',
    data: data_post,
    dataType: 'json',
    success: function(data) {
      alig = $("#alignment"+id)
      console.log(alig)
      alig.html(data['alig_phy'])
      alig.attr('alig_fa', data['alig_fa'])
      obtain_mutations(id)
    },
    error: function(response){

      // Display custom error message if no reference sequence or no from-pdb sequence were avalible for alignment 
      error_msg = response.responseText
      if (error_msg.includes('Protein sequence with')){
        error_msg = response.responseText
        for (var i = 0; i < redthings.length; i++) {
            console.log(redthings[i])
            redthings[i].addClass('shadow_error')
        }
      }
      else if (error_msg.includes('No reference sequence')){
        error_msg = response.responseText
        $("#unisequence"+id).addClass('shadow_error')
      }
      else { //Predefined message
        error_msg = "<p>An unexpected error ocurred while aligning the specified segments on the Uniprot sequence. Please revise the segment info.</p>"
      }
      errordiv.html(error_msg)
      errordiv.show()
    }
  })
}

class prot_entry { 
	constructor(id, segid="", chain="", uniprot="", checkIsoform="", isoform="1", name="", aliases="", species_code="", species_name="", checkNoGPCR="", unisequence="", notuniprot=false) {
		this.protTemplate = `	
    <div id="prot_entry${id}" data-id=${id} class='col-md-12 panel panel-primary panel_input prot_entry'>
      <div class='row prot_title'>
        <div class="col-md-11">
          <h3 id="entry_title${id}" class='leftText panel-heading'>${id}. Protein entry of chain ${chain}</h3>
        </div>
        <div class="col-md-1">
          <h3 id="remove_prot${id}" class="align_right  remove_prot" data-id=${id} ><span class="info_icon glyphicon glyphicon-trash" ></h3>
        </div>
      </div> 
      <br>
      <div class='row initial-text'>
        <div class='col-md-7'>
          <p>Please, introduce the <b>UniProtKb</b> of this protein segment and press 'retrieve' to obtain its avalible information: </p>
        </div>
        <div class="col-md-5 align_right">
          <form id="retreiveform${id}" class="retreieveform" data-id="${id}" action='/dynadb/prot_info' class='col-md-5 align_right'>
            <input id='uniprot${id}' maxlength='10' name='uniprot' value="${uniprot}" type='text' placeholder="">
            <input type='submit' id='retrieve_uniprot${id}' data-protcode='${id}' value='Retrieve'>
          </form>
          <div class="align_right isoform_inputs">
            <input id="notuniprot${id}" type="checkbox" name="isoform${id}" form="mainform" value="${notuniprot}">
            <label for="isIsoform${id}">
              <a title="Mark this checkbox if this protein does not exists in Uniprot">Not in UniProt</a> 
            </label>            
          </div>
          <div class="isoform_inputs">
            <input type="checkbox" name="isIsoform${id}" ${checkIsoform} id="isIsoform${id}">
            <label for="isIsoform${id}">
              <a title="Isoform number of this Uniprot sequence, if any">Isoform:</a> 
            </label>
            <input id="isoform${id}" type="number" class="readonly_text" readonly name="isoform${id}" form="mainform" required value="${isoform}">
          </div>
          <div id="error_uniprot${id}" class="error_loading alert alert-danger">
          </div>
          <div id="loading_uniprot${id}" class="error_loading">
            <p>Retrieving information...<img id="loading_icon" src="/static/view/images/loading-gear.gif" height="18px"><p>
          </div>
        </div>
      </div>
      <div>
        <input id='manual_mod${id}' class="manual_mod" type='checkbox' data-id="${id}" name='manual_mod${id}'> 
        <label for='manual_mod${id}'>Edit </label>
      </div>

      <hr>

      <div class='prot_data col-md-12'>

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
            <p>
              <span class="info_icon glyphicon glyphicon-info-sign" data-toggle="tooltip" title="" data-original-title="Uniprot ID of this protein."></span>
              UniprotKbac:
            </p>
          </div>
          <div class='col-md-6'>
            <input id='prot_uniprot${id}' form="mainform" required maxlength='10' readonly class='readonly_text input_step input_step${id}' name='prot_uniprot${id}' value="${uniprot}" type='text'>
          </div>
          <br>
        </div>      


        <div class='row input_row'>
          <div class='col-md-3 label_div'>
            <p>Name:</p>
          </div>
          <div class='col-md-6'>
            <input id='name${id}' form="mainform" required maxlength='60' readonly class='readonly_text input_step input_step${id}' name='name${id}' value="${name}" type='text'>
          </div>
          <br>
        </div>      

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
            <p>Other names:</p>
          </div>
          <div class='col-md-6'>
            <input id='aliases${id}' form="mainform" readonly class='readonly_text input_step input_step${id}' name='aliases${id}' value="${aliases}" type='text'>
          </div>
        </div>      

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
            <p>
              <span class="info_icon glyphicon glyphicon-info-sign" data-toggle="tooltip" title="" data-original-title="Uniprot taxon node of the species this protein belongs to."></span>
              UniProt organism id:
            </p>
          </div>
          <div class='col-md-3'>
            <input id='species_code${id}' form="mainform" required maxlength='60' readonly class='readonly_text input_step input_step${id}' name='species_code${id}' value="${species_code}" type='text'>
          </div>
          <div class='col-md-3'>
            <i id="species_name${id}_label" >${species_name}</i>
            <input id='species_name${id}' form="mainform" class='readonly_text input_step input_step${id}' value=${species_name} name='species_name${id}' value="${species_name}" type='hidden'>
          </div>
        </div>      

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
            <p>
              <span class="info_icon glyphicon glyphicon-info-sign" data-toggle="tooltip" title="" data-original-title="Sequence assigned to this UniProtKb in the uniprot database."></span>
              Sequence:
            </p>
          </div>
          <div class='col-md-6'>
            <textarea id='unisequence${id}' cols="40" rows="2" form="mainform" readonly class='readonly_text input_step input_step${id}' name='unisequence${id}'>${unisequence}</textarea>
          </div>
        </div>      

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
            <p>
              <span class="info_icon glyphicon glyphicon-info-sign" data-toggle="tooltip" title="" data-original-title="Is this protein not a GPCR?"></span>            
              Not a GPCR:
            </p>
          </div>
          <div class='col-md-1'>
            <input type="checkbox" id='notaGPCR${id}' ${checkNoGPCR} form="mainform" class='readonly_text input_step input_step${id}' name='notaGPCR${id}' >
          </div>
        </div>

        <hr>

        <div id="segment_section">

          <h3  class="orangeTit">Segments</h3>
          <p class="initial-text">Please, introduce the coordinates that correspond to this <b>UniprotKb</b> in your simulated system (uploaded in step1). 
          Should this protein be a chimera, create new protein entries for the other UniProtKbs present in this protein chain.</p>
          <div class='row initial-text'>
            <div class="col-md-12 segcontainer" id="segcontainer${id}">
              <div id="seg_index" class="row labelrow">
                <label for='pdbid${id}' class="col-md-2 col-md-offset-2">
                  <a title='ID of the PDB structure from which this fragment was obtained'>PDB id</a>
                </label>
                <label for='source{id}' class="col-md-2">
                  <a title='Experimental method used to obtain the 3D structure of this protein segment'>Source type</a>
                </label>
                <label for='chain${id}' class="col-md-1">
                  <a title='Chain Id of this protein segment'>ChainID</a>
                </label>
                <label for='segid${id}' class="col-md-1">
                  <a title='Segment Id of this protein segment'>SegmentID</a>
                </label>
                <label for='from_resid${id}' class="col-md-1">
                  <a title="ID of this segment's first residue">From resid</a>
                </label>
                <label for='to_resid${id}' class="col-md-1">
                  <a title="ID of this segment's last residue">To resid</a>
                </label>
                <label for='bound_previous${id}' class="col-md-1">
                  <a title="Is this segment covalently bound to the previous one?">Bond</a>
                </label>
              </div>
            </div>
            <input type="hidden" name="num_segs${id}" id="num_segs${id}" value="0" form="mainform">
            <div id="segentries${id}">
            </div
          </div>  
        </div>

        <br>

        <h3 class="orangeTit segDivv">Mutations</h3>
        <p class="instructions">The following mutations were detected in your system by aligning it to the uploaded UniProt sequence:</p>
        </div>
        <div class="align_div col-md-7">
          <p>Alignment: </p>
          <pre id="alignment${id}" class="input_step" alig_fa=""></pre>
          <button id="align_button${id}" onclick="align_sequences(${id})" class="btn btn-primary">Align segments to uniprot sequence</button>
          <button id="mut_button${id}" onclick="obtain_mutations(${id})" class="btn btn-primary">Get mutations from alignment</button>
          <div id="alignment_error${id}" class="col-md-12 alert alert-danger alignment_error">
            <p>An unexpected error ocurred while aligning the specified segments on the Uniprot sequence. Please revise the segment info.</p>
          </div>
          <div id="mutations_error${id}" class="col-md-12 alert alert-danger mutations_error hidden_sections">
            <p>An unexpected error ocurred while obtaining the mutations. Please revise your alignment</p>
          </div>
        </div>

        <div class=" col-md-5 mutcontainer" id="mutcontainer${id}">
          <div id="mut_index" class="row labelrow">
            <label class="col-md-3 col-md-offset-1">
              <a title='ID of the mutated residue'>Residue ID</a>
            </label>
            <label class="col-md-3">
              <a title="One-letter code of the aminoacid type in the original (uniprot's) protein sequence">From</a>
            </label>
            <label class="col-md-3">
              <a title="One-letter code of the aminoacid type in the uploaded structure's protein sequence">To</a>
            </label>
          </div>
          <input type="hidden" name="num_muts${id}" id="num_muts${id}" value="" form="mainform">
          <div id="nomuts${id}" class="col-md-12 alert alert-info nomuts hidden_sections">
            <p>No mutations found</p>
          </div>
          <div id="mutentries${id}">
          </div>

      </div>

    </div>
`;	}
}	

function add_prot_entry(){
  //Add a whole new protein entry into the form
  var id = $(".prot_entry").last().data('id') +1;
  myprot = new prot_entry(
   String(id),
   "number"+id
   );
  $(myprot.protTemplate).insertBefore($("#add_new_prot"));
  prot_listeners(id)//entry listeners
  update_entrynumber()

  // Add segs and mut entries
  add_seg_entry(id)

  // Add 'addsegment' and 'addmutations' buttons
  add_segmut_buttons(id)
}


class add_prot_btn { 
  constructor() {
    this.protTemplate = `
      <button onclick="add_prot_entry()" id="add_new_prot" class="panel btn btn-outline-primary col-md-12">
        <h2>
          <span class=" glyphicon glyphicon-plus" data-toggle="tooltip" title="" data-original-title="Add a new molecule entry to fill"> 
        </h2>  
      </button>
    `;
  }
} 

class seg_entry { 
  constructor(id="", seg="",pdbid="",chain="",segid="", resid_from="", resid_to="", bond="")  {
    this.Template = `
      <div class="row  segentry${id}" data-segnum="${seg}" id="${seg}segentry${id}">
        <div class="col-md-1 col-md-offset-1 segnum_div label_div">
          <p>${seg}. </p>
          <input form="mainform" type="hidden" name="${seg}seg${id}" id="${seg}seg${id}" class="input_coord" value="${seg}">
        </div>
        <div class="col-md-2 ">
          <input form="mainform" required data-mylabel="PDBid for segment ${seg} in entry ${id}" type="text" maxlength="6" value="${pdbid}" name="${seg}pdbid${id}" id="${seg}pdbid${id}" class="input_coord">
        </div>
        <div class="col-md-2 ">
          <select form="mainform" required name="${seg}sourcetype${id}" id="${seg}sourcetype${id}" class="input_coord">
            <option value="0"> X-ray</option>
            <option value="1"> NMR</option>
            <option value="2"> Ab-initio</option>
            <option value="3"> Homology</option>
            <option value="4"> Threading</option>
            <option value="5"> MD</option>
            <option value="7"> Electron microscopy</option>
            <option value="6"> Other Computational  Methods</option>
          </select>
        </div>
        <div class="col-md-1">
          <input form="mainform" data-mylabel="Chain id for segment ${seg} in entry ${id}" required type="text" maxlength="1" value="${chain}" name="${seg}chain${id}" id="${seg}chain${id}" class="input_coord">
        </div>
        <div class="col-md-1">
          <input form="mainform" data-mylabel="Segment id for segment ${seg} in entry ${id}" required type="text" maxlength="4" value="${segid}" name="${seg}segid${id}" id="${seg}segid${id}" class="input_coord">
        </div>
        <div class="col-md-1">
          <input form="mainform" data-mylabel="Initial residue of segment ${seg} in entry ${id}" required type="number" value="${resid_from}" name="${seg}from_resid${id}" id="${seg}from_resid${id}" class="input_coord">
        </div>
        <div class="col-md-1">
          <input form="mainform" data-mylabel="End residue of segment ${seg} in entry ${id}" required type="number" value="${resid_to}" name="${seg}to_resid${id}" id="${seg}to_resid${id}" class="input_coord">
        </div>
        <div class="col-md-1">
          <input form="mainform" type="checkbox" ${bond} name="${seg}bound_previous${id}" id="${seg}bound_previous${id}" class="input_coord">
        </div>
        <div class="col-md-1">
          <h3 id="${seg}remove_seg${id}" data-id="${id}" class="remove_seg"><span class="info_icon glyphicon glyphicon-trash"></span></h3>
        </div>

      </div>
    `;
  }
}

function update_segnumber(id){
  //Update the input tag storing the info about the number of molecule entries in the form
  var id, id_list = [], jointed_ids;
  $(".segentry"+id).each(function(){
    segnum = $(this).data('segnum')
    id_list.push(segnum)
  });
  jointed_ids = String(id_list.join(','))
  $("#num_segs"+id).val(jointed_ids)
}

function add_seg_entry(id, seg="",pdbid="",chain="",segid="", resid_from="", resid_to="", bond="", sourcetype=""){
  
  //Get current last number of segment id
  segnum_ar = $("#num_segs"+id).val().split(',').map(Number)
  max_seg = Math.max(...segnum_ar)
  new_seg = String(max_seg+1)
  //Add an empty segment entry into the specified protein entry
  var myseg = new seg_entry(id, new_seg, pdbid, chain, segid, resid_from, resid_to, bond)
  $("#segentries"+id).append(myseg.Template)
  //Listener for trash button
  $('#'+new_seg+'remove_seg'+id).click(function(){
    $(this).parent().parent().remove();
    update_segnumber(id)
  })
  //Set source type in selector
  if (sourcetype) {
    $('#'+new_seg+'segentry'+id+' select').val(sourcetype)
  }
  update_segnumber(id)
}

class add_seg_btn { 
  constructor(id="") {
    this.Template = `
      <br>
      <div class="row labelrow">
        <button onclick="add_seg_entry(${id})" id="addsegs${id}" class="col-md-offset-1 col-md-10 addsegs btn btn-outline-primary">
          <span class=" glyphicon glyphicon-plus" data-toggle="tooltip" title="" data-original-title="Add a new segment entry"> 
        </button>
      </div>

    `;
  }
}

//Sé mo laoch mo Ghile Mear
//'Sé mo Chaesar, Ghile Mear,
//Suan ná séan ní bhfuaireas féin
//Ó chuaigh i gcéin mo Ghile Mear.

class mut_entry { 
  constructor(id="", mut="", resid="", from="", to="") {
    this.Template = `
      <div class="row labelrow mutentry${id}" data-mutnum="${mut}" id="${mut}mutentry${id}">
        <div class="col-md-1">
          <p>${mut}. </p>
          <input form="mainform" type="hidden" name="${mut}seg${id}" id="${mut}mut${id}" class="input_coord" value="${mut}">
        </div>      
        <div class="col-md-3">
          <input id='${mut}resid${id}' required form="mainform" data-mylabel="Residue id of mutation ${mut} in entry ${id}" class='readonly_text input_step input_step${id}' value="${resid}" name='${mut}resid${id}' type='number'>
        </div>
        <div class="col-md-3 ">
          <input id='${mut}from${id}' required form="mainform" data-mylabel="Original residue name for mutation ${mut} in entry ${id}" maxlength='1' class='readonly_text input_step input_step${id}' value="${from}" name='${mut}from${id}' type='text'>
        </div>
        <div class="col-md-3 ">
          <input id='${mut}to${id}' required form="mainform" data-mylabel="Mutated residue name for mutation ${mut} in entry ${id}" maxlength='1' class='readonly_text input_step input_step${id}' value="${to}" name='${mut}to${id}' type='text'>
        </div>
        <div class="col-md-2">
          <h3 id="${mut}remove_mut${id}" data-id="${id}" class="remove_mut"><span class="info_icon glyphicon glyphicon-trash"></span></h3>
        </div>
      </div>    
    `;
  }
}

function update_mutnumber(id){
  //Update the input tag storing the info about the number of molecule entries in the form
  var id, id_list = [], jointed_ids;
  $(".mutentry"+id).each(function(){
    mutnum = $(this).data('mutnum')
    id_list.push(mutnum)
  });
  jointed_ids = String(id_list.join(','))
  $("#num_muts"+id).val(jointed_ids)
}

function add_mut_entry(id, resid="", from="", to=""){
  //Get current last number of segment id
  mutnum_ar = $("#num_muts"+id).val().split(',').map(Number)
  if (mutnum_ar){
    max_mut = Math.max(...mutnum_ar)
    new_mut = String(max_mut+1)  //Add an empty segment entry into the specified protein entry
  } else {
    new_mut = '0'
  }
  var mymut = new mut_entry(id, new_mut, resid, from, to)
  $("#mutentries"+id).append(mymut.Template)
  //Listener for trash button
  $('#'+new_mut+'remove_mut'+id).click(function(){
    $(this).parent().parent().remove();
    update_mutnumber(id);
  })
  update_mutnumber(id);
}

class add_mut_btn { 
  constructor(id="") {
    this.Template = `
    <br>
    <div class="row labelrow">
      <button onclick="add_mut_entry(${id})" id="addmuts${id}" class="col-md-offset-2 col-md-7 addmuts btn btn-outline-primary">
        <span class=" glyphicon glyphicon-plus" data-toggle="tooltip" title="" data-original-title="Add a new mutation entry"> 
      </button>
    </div>    
    `;
  }
}

//// Actual functions

function add_segmut_buttons(id){
  // Add 'addsegment' button into template
  myaddseg = new add_seg_btn(id=id)
  $(myaddseg.Template).insertAfter($("#segentries"+id))

  // Add 'addmutatoins' button into template
  myaddmut = new add_mut_btn(id=id)
  $(myaddmut.Template).insertAfter($("#mutentries"+id))
}

function update_entrynumber(){
  //Update the input tag storing the info about the number of molecule entries in the form
  var id, id_list = [], jointed_ids;
  $(".prot_entry").each(function(){
    id = $(this).data('id')
    id_list.push(id)
  });
  jointed_ids = id_list.join(',')
  $("#num_entries").val(jointed_ids)
}

function remove_prot(id) {
  // Remove molecule on click of small trash bin
  $("#remove_prot"+id).click(function(){
    var resname = $(this).data('resname')
    var confirmation = confirm("Are you sure you want to delete "+resname+" protein entry?");
    if (confirmation) {
      $("#prot_entry"+id).remove();
      update_entrynumber()
    }
  });

}

function isIsoform_checkbox(id) {
  // Edit information manually checkbox
  $("#isIsoform"+id).change(function() {
    var isenabled = $(this).is(":checked")
    $("#isoform"+id).attr('readonly',!isenabled)
    $("#isoform"+id).toggleClass('readonly_text')
  });
}

function edit_checkbox(id) {
  // Edit information manually checkbox
  $("#manual_mod"+id).change(function() {
    var isenabled = $(this).is(":checked")
    $(".input_step"+id).attr('readonly',!isenabled)
    $(".input_step"+id).toggleClass('readonly_text')
  });
}

function silence_field(ID, isenabled) {
  $(ID).prop('disabled', isenabled)
  $(ID).prop('required', !isenabled)
  $(ID).val('')    
}

function notuniprot_checkbox(id) {
  // Protein not-in-uniprot checkbox
  checkbox = $("#notuniprot"+id) 
  checkbox.change(function() {
    var isenabled = $(this).is(":checked")
    //enable forcefully manual modification of fields
    $("#manual_mod"+id).prop("checked",isenabled)
    $("#manual_mod"+id).prop("disabled",isenabled)
    $(".input_step"+id).attr('readonly',!isenabled)
    isenabled ? $(".input_step"+id).removeClass('readonly_text') : $(".input_step"+id).addClass('readonly_text') 
    //Disable everything related to uniprot
    $("#retrieve_uniprot"+id).prop('disabled',isenabled)
    silence_field("#uniprot"+id, isenabled)
    silence_field("#prot_uniprot"+id, isenabled)
    silence_field("#unisequence"+id, isenabled)
    silence_field("#align_button"+id, isenabled)
    silence_field("#mut_button"+id, isenabled)
  });
}

function prot_listeners(id){

  //Remove entry on click of trash bin
  remove_prot(id)

  //Allow modifications on click of checkbox
  edit_checkbox(id)

  //Allow modifications of isoform on click of checkbox
  isIsoform_checkbox(id)

  //Disable uniprot-related functions and enable manual edit on click of "notuniprot" checkbox
  notuniprot_checkbox(id)

  //Informative tooltips
  $('[data-toggle="tooltip"]').tooltip();

  //When the "retreive" button of the uniprotkb searcher is clicked, activate this function to retrieve information from the database and 
  // put in the molecule HTML entry fields
  $(".retreieveform").submit(function(e) {

    e.preventDefault(); // avoid to execute the actual submit of the form.
    var form = $(this);
    var id = form.data('id')
    var url = form.attr('action');
    var errordiv = $("#error_uniprot"+id) 
    var loadingdiv = $("#loading_uniprot"+id)
    var uniprotkbac = $('#uniprot'+id).val()
    var input_data = {
      'uniprotkbac' : uniprotkbac,
      'isoform' : $('#isoform'+id).val(),
      'submission_id' : $('#submission_id').val(),
    }
    errordiv.hide()
    loadingdiv.show()
    $.ajax({
      url: url,
      data: input_data,
      // On success, replace prot entry's values by the ones obtained in the retrieved data
      success: function(data){
        prot_data = JSON.parse(data)
        names_array = [];
        if (prot_data['Protein names']){
          names = prot_data['Protein names'].replace(/ \[.*\]$/,"") //Remove "Cleaved into following chains" section if there is any
          names_array = names.split(" (")
          names_array = names_array.map(function(item,index){return item.replace(/\)$/,"")})
        }
        //From the names provided by uniprot, take first one as the official
        main_name = names_array.shift()
        synonims = names_array.join(';')
        $("#name"+id).val(main_name)
        $("#aliases"+id).val(synonims)
        $("#species_code"+id).val(prot_data['Organism (ID)'])
        $("#species_name"+id+"_label").html(prot_data['Organism'])
        $("#unisequence"+id).val(prot_data['Sequence'])
        $("#prot_uniprot"+id).val(uniprotkbac)
        //We assume that the only receptors here are GPCRs
        not_gpcr =  !(prot_data['Protein families'].includes('receptor')) && !(prot_data['Protein families'].includes('Receptor'))
        $("#notaGPCR"+id).prop('checked', not_gpcr)
      },
      //Migth something go wrong, show an error message bellow the retreive button
      error: function(){
        var thisinchikey = $("#inchikey"+id).val()
        errordiv.html("<p>Error: something failed upon retrieving information for inchikey "+thisinchikey+"</p>")
        errordiv.show()
      },
      //Hide loading div when it is done
      complete: function(){
        loadingdiv.hide()
      }
    }).then(function(){
      //Re-obtain alignment and mutations
      align_sequences(id)
    });
  });
      
}

function create_prot_entries(data, container) {
  // Renders a prot template with the information passed in "data" and appends inside the "container" HTML element 
  var data_prot, myprot, myseg, segcontainer;
  for (i in data) {
    data_prot=data[i]
    myprot = new prot_entry(
      String(i),
      data_prot['segid'],
      data_prot['segments'].length ? data_prot['segments'][0]['chain'] : 'X',
      data_prot['uniprot'],
      data_prot['isIsoform'] ? 'checked' : '',
      data_prot['isoform'],
      data_prot['name'],
      data_prot['aliases'],
      data_prot['species_code'],
      data_prot['species_name'],
      data_prot['noGPCR'] ? 'checked' : '',
      data_prot['unisequence'],
      data_prot['notuniprot']
    )
    container.append(myprot.protTemplate)
    
    // Add Segment entries (if any)
    segcontainer = container.find("#segentries"+i)
    for (j in data_prot['segments']) {
      seg = data_prot['segments'][j]
      add_seg_entry(i, 
        j,
        seg['pdbid'],
        seg['chain'],
        seg['segid'],
        seg['resid_from'], 
        seg['resid_to'], 
        seg['bond'] ? 'checked' : '',
        seg['source_type'],
      )
    }

    // Add Mutation entries
    mutcontainer = container.find("#mutentries"+i)
    for (h in data_prot['mutations']) {
      mut = data_prot['mutations'][h]
      add_mut_entry(i, mut['resid'], mut['from'], mut['to'])
    }

    // Add 'addsegment' and 'addmutations' button
    add_segmut_buttons(i)

    //Listeners of events related to small molecules
    prot_listeners(i)
  }

  //Update number of entries in the form
  update_entrynumber()

  //Add html to append a new molecule entry
  newmol = new add_prot_btn()
  container.append(newmol.protTemplate)

  //Align sequences and get mutations
  //align_sequences(i)
}
