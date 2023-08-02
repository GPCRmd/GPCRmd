class smalmol_entry { 
	constructor(id, blocked="readonly", resname="", inchikey="", sinchikey="", name="", iupac="", chemblid="", cid="", inchi="", sinchi="", smiles="", net_charge="",  other_names="", description="", imagepath="", submission_id="") {
		this.smalmolTemplate = `
  	<div id="smalmol_entry${id}" data-id=${id} class='col-md-12 panel panel-primary panel_input smalmol_entry'>

      <div class='row smalmol_title'>
        <div class="col-md-11">
          <h3 class="leftText panel-heading" id="entry_title${id}">${id}. Small molecule ${resname}</h3>
        </div>
        <div class="col-md-1">
          <h3 id="remove_smalmol${id}" class="align_right  remove_smalmol" data-resname=${resname} data-id=${id} ><span class="info_icon glyphicon glyphicon-trash" ></h3>
        </div>
      </div> 
      <br>
      <div class='row initial-text'>
	      <div class='col-md-7'>
	        <p>
	        Molecule role in the system: 
	       	<span class="info_icon glyphicon glyphicon-info-sign" data-toggle="tooltip" title="" data-original-title="Select the function of this small molecule in the system (solvent, membrane lipid, ligand) and whether or not it was present in the original experimental structure"></span>
	       	</p>
	      </div>
	      <div class="col-md-5 align_right">
		      <select form="mainform" id="smalmol_type${id}" required name="smalmol_type${id}">
            <option disabled selected value> -- select an option -- </option>
  		    	<option value="0"> Orthosteric ligand</option>
  			    <option value="1"> Allosteric ligand</option>
  			    <option value="2"> Experimental ions</option>
  			    <option value="3"> Experimental lipids</option>
  			    <option value="4"> Experimental waters</option>
  			    <option value="5"> Other co-crystalized item</option>
    				<option value="6"> Bulk waters</option>
    				<option value="7"> Bulk lipids</option>
    				<option value="8"> Bulk ions</option>
    				<option value="9"> Other bulk component</option>
			    </select>
		    </div>
	    </div>	

	    <br>
      <div class='row initial-text'>
        <div class='col-md-7'>
          <p>Please, introduce the <b>InChIKey</b> of this molecule and press 'retrieve' to obtain its avalible information: </p>
        </div>
        <div class="col-md-5 align_right">
          <form id="retreiveform${id}" class="retreieveform" data-id="${id}" action='/dynadb/smalmol_info' class='col-md-5 align_right'>
            <input id='inchikey${id}' maxlength='27' name='inchikey' required type='text' placeholder="" value="${inchikey}">
            <input id='submission_id${id}' name='submission_id' type='hidden' value="${submission_id}" />
            <input type='submit' id='retrieve_inchikey${id}' data-smalmolcode='${id}' value='Retrieve'>
          </form>
          <div id="error_inchikey${id}" class="error_loading alert alert-danger">
          </div>
          <div id="nopubchem_inchikey${id}" class="error_loading alert alert-warning">
          </div>
          <div id="loading_inchikey${id}" class="error_loading">
            <p>Retrieving information...<img id="loading_icon" src="/static/view/images/loading-gear.gif" height="18px"><p>
          </div>
        </div>
      </div>
      <div>
        <input id='manual_mod${id}' class="manual_mod" type='checkbox' data-id="${id}" name='manual_mod${id}'> 
        <label for='manual_mod${id}'>Edit </label>
      </div>

      <hr>
      <div class='smalmol_data col-md-6'>

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
            <p>Name: </p>
          </div>
          <div class='col-md-9'>
            <input id='smalmol_name${id}' ${blocked} form="mainform" required maxlength='60' class='readonly_text input_step input_step${id}' name='smalmol_name${id}' type='text' value="${name}">
          </div>
          <br>
        </div>      

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
              <p> Residue name: </p>
          </div>
          <div class='col-md-9'>
            <input id='smalmol_resname${id}' form="mainform" required maxlength='60' class=' input_step input_step${id}' name='smalmol_resname${id}' type='text' value="${resname}">
          </div>
          <br>
        </div>      

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
              <p> IUPAC name: </p>
          </div>
          <div class='col-md-9'>
            <input id='smalmol_iupac${id}' ${blocked} form="mainform" required maxlength='500' class='readonly_text input_step input_step${id}' name='smalmol_iupac${id}' type='text' value="${iupac}">
          </div>
          <br>
        </div>      

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
              <p> ChemblId: </p>
          </div>
          <div class='col-md-9'>
            <input id='smalmol_chemblid${id}' ${blocked} form="mainform" class='readonly_text input_step input_step${id}' name='smalmol_chemblid${id}' type='number' value="${chemblid}">
          </div>
          <br>
        </div>      

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
              <p> Pubchem CID: </p>
          </div>
          <div class='col-md-9'>
            <input id='smalmol_cid${id}' ${blocked} form="mainform" class='readonly_text input_step input_step${id}' name='smalmol_cid${id}' type='number' placeholder="" value="${cid}">
          </div>
          <br>
        </div>      

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
              <p> InChI: </p>
          </div>
          <div class='col-md-9'>
            <input id='smalmol_inchi${id}' ${blocked} form="mainform" required maxlength='500' placeholder="e.g: 1S/H2O/h1H2" class='readonly_text input_step input_step${id}' name='smalmol_inchi${id}' type='text' placeholder="" value="${inchi}">
          </div>
          <br>
        </div>      

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
              <p>
                <span class="info_icon glyphicon glyphicon-info-sign" data-toggle="tooltip" title="" data-original-title="InChi of the standard form of this molecule (should be the same as InChi, except if the submited molecule is an isomer)"></span>
                Standard InCh: 
              </p>
          </div>
          <div class='col-md-9'>
            <input id='smalmol_sinchi${id}' ${blocked} form="mainform" required maxlength='500' placeholder="e.g: 1S/H2O/h1H2" class='readonly_text input_step input_step${id}' name='smalmol_sinchi${id}' type='text'  value="${sinchi}">
          </div>
          <br>
        </div>      

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
              <p> InChIKey: </p>
          </div>
          <div class='col-md-9'>
            <input id='smalmol_inchikey${id}' ${blocked} form="mainform" required maxlength='27' class='readonly_text input_step input_step${id}' name='smalmol_inchikey${id}' type='text' placeholder="e.g: XLYOFNOQVPJJNP-UHFFFAOYSA-N" value="${inchikey}">
          </div>
          <br>
        </div>      

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
              <p>
                <span class="info_icon glyphicon glyphicon-info-sign" data-toggle="tooltip" title="" data-original-title="InChiKey of the standard form of this molecule (should be the same as InChiKey, except if the submited molecule is an isomer)"></span>
                Standard InChIKey: 
              </p>
          </div>
          <div class='col-md-9'>
            <input id='smalmol_sinchikey${id}' ${blocked} form="mainform" required maxlength='27' class='readonly_text input_step input_step${id}' name='smalmol_sinchikey${id}' type='text' placeholder="e.g: XLYOFNOQVPJJNP-UHFFFAOYSA-N" value="${sinchikey}">
          </div>
          <br>
        </div>      

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
              <p> Open SMILES: </p>
          </div>
          <div class='col-md-9'>
            <textarea id='smalmol_smiles${id}' ${blocked} form="mainform" required maxlength='500' class='readonly_text input_step input_step${id}' name='smalmol_smiles${id}' placeholder="smiles code" >${smiles}</textarea>
          </div>
          <br>
        </div>              

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
              <p> Net charge: </p>
          </div>
          <div class='col-md-9'>
            <input id='smalmol_netcharge${id}' ${blocked} form="mainform" required maxlength='2' class='readonly_text input_step input_step${id}' name='smalmol_netcharge${id}' type='number' placeholder="${net_charge}" value="${net_charge}">
          </div>
          <br>
        </div>              

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
              <p> Other names (comma-separated): </p>
          </div>
          <div class='col-md-9'>
            <textarea id='smalmol_synonyms${id}' ${blocked} form="mainform" maxlength='200' class='readonly_text input_step input_step${id}' name='smalmol_synonyms${id}'>${other_names}</textarea>
          </div>
          <br>
        </div>              

        <div class='row input_row'>
          <div class='col-md-3 label_div'>
              <p> Description: </p>
          </div>
          <div class='col-md-9'>
            <textarea id='smalmol_description${id}' ${blocked} form="mainform" maxlength='80' class='readonly_text input_step input_step${id}' name='smalmol_description${id}'>${description}</textarea>
          </div>
          <br>
        </div>              
      </div>
      <div id="imagediv${id}" class='col-md-6 imagediv'>
        <img id="mol_image${id}" class="mol_image" src="${imagepath}" height="100%" alt="Image not avalible yet for this molecule">
        <input type='hidden' name="image_path${id}" id="image_path${id}" form="mainform" value=${imagepath} >
      </div>
    </div>
`;	}
}	

class add_smalmol { 
  constructor() {
    this.smalmolTemplate = `
    <button id="addmol_button" class="btn btn-outline-primary col-md-12 panel">
      <h1><span class=" glyphicon glyphicon-plus" data-toggle="tooltip" title="" data-original-title="Add a new molecule entry to fill"></h1>
    </button> 
    `;
  }
} 

class add_SDF {
  constructor(id, visible, title, required="") {
    this.Template = `
      <div class="row alert alert-warning" style="display: ${visible}">
        <p><b>InChIKey not found in GPCRmd's database!</b> In order to create a new entry, please upload an SDF file of your molecule</p>
      </div
      <div class="row">
        <div class="col-md-4 label_div">
            <p>Molecule SDF file:</p>
        </div>
        <div class="col-md-8">
          <input type="file"  name="sdfmol${id}"  class="validate[required,custom[onlyLetter],length[0,100]] ${required} feedback-input" form="mainform" placeholder="" accept=".sdf" id="sdfmol${id}" />
        </div>
      </div>
    `;
  }
}

function update_entrynumber(){
  //Update the input tag storing the info about the number of molecule entries in the form
  var id, id_list = [], jointed_ids;
  $(".smalmol_entry").each(function(){
    id = $(this).data('id')
    id_list.push(id)
  });
  jointed_ids = id_list.join(',')
  $("#num_entries").val(jointed_ids)
}

function submitSDF(id, inGPCRmd, creation_submission) {
  //Add input template to submit SDF file if required, and replace it by the image of smalmol
  var instructions, newSDF_form;
  if ((!inGPCRmd) && !($('#sdfmol'+id).length)){
    instructions = "Since this molecule was not found in GPCRmd, a SDF file is required to create a new entry for it";
    newSDF_form = new add_SDF(id, "block", instructions,'required');
    $("#imagediv"+id).append(newSDF_form.Template)
  }
  else if (creation_submission){
    instructions = "Submit a new SDF file if you wish to replace the existing one in GPCRmd"
    newSDF_form = new add_SDF(id,"block", instructions);
    $("#imagediv"+id).append(newSDF_form.Template)
  }
}

function remove_molecule(id) {
  // Remove molecule on click of small trash bin
  $("#remove_smalmol"+id).click(function(){
    var resname = $(this).data('resname')
    var confirmation = confirm("Are you sure you want to delete "+resname+" molecule entry?");
    if (confirmation) {
      $("#smalmol_entry"+id).remove();
      update_entrynumber()
    }
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

function smalmol_listeners(){

  //Informative tooltips
  $('[data-toggle="tooltip"]').tooltip();

  //When the "retreive" button of the inchikey searcher is clicked, activate this function to retrieve information from the database and 
  // put in the molecule HTML entry fields
  $(".retreieveform").submit(function(e) {

    e.preventDefault(); // avoid to execute the actual submit of the form.
    var form = $(this);
    var id = form.data('id')
    var url = form.attr('action');
    var manual_mod = $("#manual_mod"+id)
    var errordiv = $("#error_inchikey"+id) 
    var loadingdiv = $("#loading_inchikey"+id)
    var nopub = $("#nopubchem_inchikey"+id)
    manual_mod.attr("disabled",false)
    errordiv.hide()
    loadingdiv.show()
    nopub.hide()
    $.ajax({
      url: url,
      data: form.serialize(),
      success: function(data){

        // On success, replace smalmol entry's values by the ones obtained in the retrieved data
        smalmol_data = JSON.parse(data)
        $('#smalmol_inchikey'+id).val(smalmol_data['inchikey'])
        $('#smalmol_sinchikey'+id).val(smalmol_data['sinchikey'])
        $('#smalmol_name'+id).val(smalmol_data['name'])
        $('#smalmol_iupac'+id).val(smalmol_data['iupac'])
        $('#smalmol_chemblid'+id).val(smalmol_data['chemblid'])
        $('#smalmol_cid'+id).val(smalmol_data['cid'])
        $('#smalmol_inchi'+id).val(smalmol_data['inchi'])
        $('#smalmol_sinchi'+id).val(smalmol_data['sinchi'])
        $('#smalmol_smiles'+id).val(smalmol_data['smiles'])
        $('#smalmol_netcharge'+id).val(smalmol_data['net_charge'])
        $('#smalmol_synonyms'+id).val(smalmol_data['other_names'])
        $('#smalmol_description'+id).val(smalmol_data['description']) 
        $('#mol_image'+id).attr('src',smalmol_data['imagepath'])
  
        //Add SDF file input entry if required
        submitSDF(String(id), smalmol_data['inGPCRmd'], smalmol_data['creation_submission'])

        // Change name of the entry to name of the molecule
        $("#entry_title"+id).html(id+'. Small molecule '+smalmol_data['name'])

        // If no molecule is not found in the database, ask user to introudce its data manually
        if (!smalmol_data['cid']){
          nopub.html("<p><b>Molecule not found in pubchem:</b> please manually introduce the data for this molecule entry.</p>")
          nopub.show()
          if (!manual_mod.prop('checked')){
            manual_mod.trigger('click')
          }
          manual_mod.attr("disabled",true)
        }

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
    });
  });
      
}


function smalmol_entries(data, container) {
  // Renders a smalmol template with the information passed in "data" and appends inside the "container" HTML element 
  var mols = Object.keys(data)
  var resname, data_smalmol, mymol, newmol;
  for (let i = 0; i < mols.length; i++) {
    mol_num = mols[i];
    data_smalmol = data[mol_num];
    mymol = new smalmol_entry(
      mol_num,
      data_smalmol['blocked'],
      data_smalmol['resname'],
      data_smalmol['inchikey'],
      data_smalmol['sinchikey'],
      data_smalmol['name'],
      data_smalmol['iupac'],
      data_smalmol['chemblid'],
      data_smalmol['cid'],
      data_smalmol['inchi'],
      data_smalmol['sinchi'],
      data_smalmol['smiles'],
      data_smalmol['net_charge'],
      data_smalmol['other_names'],
      data_smalmol['description'],
      data_smalmol['imagepath'],
      data_smalmol['submission_id']
    )
    container.append(mymol.smalmolTemplate)
    
    //Set default option for molecule-type selector, if any was passed
    if (data_smalmol['mol_type']!==''){
      $("#smalmol_type"+mol_num+" option[value='"+data_smalmol['mol_type']+"']").selected()
    }

    //If the molecule was not found in the GPCRmd database, ask the submitter for a SDF file
    if (!data_smalmol['inGPCRmd']){
      submitSDF(mol_num, data_smalmol['inGPCRmd'], data_smalmol['creation_submission'])
    }

    //Add listeners 
    remove_molecule(mol_num)
    edit_checkbox(mol_num)
  }

  //Update the number of molecule entries in the form
  update_entrynumber()

  //Add html to append a new molecule entry
  newmol = new add_smalmol()
  container.append(newmol.smalmolTemplate)
  //Listener to add new molecule entry on click of "add molecule" button
  $("#addmol_button").click(function(){
    var new_id = $(".smalmol_entry").last().data('id') +1;
    mymol = new smalmol_entry(
     String(new_id),
     "readonly",
     );
    $(mymol.smalmolTemplate).insertBefore($("#addmol_button"));
    smalmol_listeners()//entry listeners
    update_entrynumber()
    remove_molecule(new_id)
    edit_checkbox(new_id)
  });

  //Listeners of events related to small molecules
  smalmol_listeners()
}
