
$(document).ready(function(event){
    var fasta = document.getElementById("fasta-files").innerText;
    console.log('listenint');

    var m = msa({
	    el: document.getElementById("msa"),
        seqs: msa.io.fasta.parse(fasta)
    });
    m.render();
});
