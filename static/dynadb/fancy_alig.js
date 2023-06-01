//main function to call the MSA plugin to show the aligment in colors.
$(document).ready(function(event){
    var yourDiv=document.getElementById("msa");
    var fasta = document.getElementById("fasta-files").innerText;
    var seqs = msa.io.fasta.parse(fasta);
    opts = {};
    opts.seqs = seqs;
    var d = msa(opts);
    yourDiv.appendChild(d.el);
    var fun = {}
    // the init function is only called once
    fun.init = function(){
      // you have here access to the conservation or the sequence object
      this.cons = this.opt.conservation();
    }
    fun.run = function(letter,opts){
      return this.cons[opts.pos] == 1 ? "blue" : "red" //return this.cons[opts.pos] == 1 ? "#fff" : "red"
    };

    d.g.colorscheme.addDynScheme("dyn", fun);
    d.g.colorscheme.set("scheme", "dyn");
    d.render();

});
