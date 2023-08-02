
$(document).ready(function(){


  var h=$("#header").detach();
  $(h).insertBefore("nav");
  $("body").css("display","block");





//Click tooltip
//$("#chart").on("click","g",function(e){
//    console.log(e.pageX,e.pageY)
//    $("#clickinfo").html("<div style='background-color:#3278B4'>aaaaaaaaaaaaaaaaa</div>")
//    $("#clickinfo").css({"top":e.pageY,"left":e.pageX})
//})




//CREATE PLOT ---------------------------------------------

/*  var data = {
    "children": [{
      "name": "Class A",
      "State": "-",
      "CrystalLigand": "-",
      "OldLigand": "-",
      "CrystalTransducer": "-",
      "Transducer": "-",
      "Simulated": "-",
      "Apo": "-",
      "Complex": "-",
      "Ligand": "-",
      "ClassCol": "-",
      "KlassCol": "A\t\t\t\t",
      "children": [{
        "name": "5-Hydroxytryptamine",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "5-HT1B",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "6G79",
            "State": "Active",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "EP5",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4IAQ",
            "State": "Intermediate",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "85",
            "Complex": "",
            "Ligand": "dihydroergotamine",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5V54",
            "State": "Intermediate",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "(+)-Metitepine",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4IAR",
            "State": "Intermediate",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "87",
            "Complex": "90",
            "Ligand": "ERGOTAMINE",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "5-HT2B",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5TUD",
            "State": "Active",
            "CrystalLigand": "5-hydroxytryptamine",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "ERGOTAMINE",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4IB4",
            "State": "Intermediate",
            "CrystalLigand": "5-hydroxytryptamine",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "92",
            "Complex": "94",
            "Ligand": "ERGOTAMINE",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4NC3",
            "State": "Intermediate",
            "CrystalLigand": "5-hydroxytryptamine",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "ERGOTAMINE",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5TVN",
            "State": "Intermediate",
            "CrystalLigand": "5-hydroxytryptamine",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "Lysergide",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "5-HT2C",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "6BQH",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "ritanserin",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6BQG",
            "State": "Active",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "ERGOTAMINE",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Adenosine",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "A1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5UEN",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "21|165",
            "Complex": "",
            "Ligand": "CHEMBL144360",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6D9H",
            "State": "Active",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "adenosine",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5N2S",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "PSB36",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "A2A",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5G53",
            "State": "Active",
            "CrystalLigand": "NECA",
            "OldLigand": "NECA",
            "CrystalTransducer": "mini-Gs",
            "Transducer": "mini-Gs",
            "Simulated": "Yes",
            "Apo": "47",
            "Complex": "48",
            "Ligand": "NECA",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4UHR",
            "State": "Intermediate",
            "CrystalLigand": "CGS21680",
            "OldLigand": "CGS21680",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "45",
            "Complex": "46",
            "Ligand": "Cgs 21680",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3VG9",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5IU8",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "52",
            "Complex": "",
            "Ligand": "6DZ",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3UZC",
            "State": "Inactive",
            "CrystalLigand": "4-(3-amino-5-phenyl-1,2,4-triazin-6-yl)-2-chlorophenol",
            "OldLigand": "4-(3-amino-5-phenyl-1,2,4-triazin-6-yl)-2-chlorophenol",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "41",
            "Complex": "42",
            "Ligand": "T4E",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5IUB",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "54",
            "Complex": "",
            "Ligand": "6DV",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5K2C",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5N2R",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "8JN",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5OLO",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "TOZADENANT",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5VRA",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4EIY",
            "State": "Inactive",
            "CrystalLigand": "ZM241385",
            "OldLigand": "ZM241385",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "43",
            "Complex": "44",
            "Ligand": "ZM241385 ",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6AQF",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5OLH",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "Vipadenant",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2YDV",
            "State": "Intermediate",
            "CrystalLigand": "NECA",
            "OldLigand": "NECA",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "32",
            "Complex": "33",
            "Ligand": "NECA",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3REY",
            "State": "Inactive",
            "CrystalLigand": "XAC",
            "OldLigand": "XAC",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "35",
            "Complex": "36",
            "Ligand": "Papaxac",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5MZJ",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "theophylline",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5MZP",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "caffeine",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2YDO",
            "State": "Intermediate",
            "CrystalLigand": "ADENOSINE",
            "OldLigand": "ADENOSINE",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "30",
            "Complex": "31",
            "Ligand": "adenosine",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5JTB",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5IUA",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "53",
            "Complex": "",
            "Ligand": "6DX",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3VGA",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3EML",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5K2B",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3UZA",
            "State": "Inactive",
            "CrystalLigand": "6-(2,6-dimethylpyridin-4-yl)-5-phenyl-1,2,4-triazin-3-amine",
            "OldLigand": "6-(2,6-dimethylpyridin-4-yl)-5-phenyl-1,2,4-triazin-3-amine",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "39",
            "Complex": "40",
            "Ligand": "3uza",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6GDG",
            "State": "Active",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "NECA",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5IU4",
            "State": "Inactive",
            "CrystalLigand": "ZM241385",
            "OldLigand": "ZM241385",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "49",
            "Complex": "50",
            "Ligand": "ZM241385 ",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5WF5",
            "State": "Intermediate",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "UKA",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3QAK",
            "State": "Intermediate",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "34",
            "Complex": "",
            "Ligand": "UKA",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5OLV",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "9Y2",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3PWH",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5NLX",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5OM1",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "T4E",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5WF6",
            "State": "Intermediate",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "UKA",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5K2A",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5OLG",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5UVI",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5UIG",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "8D1",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3RFM",
            "State": "Inactive",
            "CrystalLigand": "CAFFEINE",
            "OldLigand": "CAFFEINE",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "37",
            "Complex": "38",
            "Ligand": "caffeine",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5NM2",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4UG2",
            "State": "Intermediate",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "Cgs 21680",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5OLZ",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "T4E",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5NM4",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5OM4",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "T4E",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5K2D",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5IU7",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "51",
            "Complex": "",
            "Ligand": "CHEMBL3937413",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Apelin",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "Apelin",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5VBL",
            "State": "Inactive",
            "CrystalLigand": "apelin-13 apelin receptor early endogenous ligand",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "peptide",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Angiotensin",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "AT1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "4ZUD",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-|-",
            "Simulated": "Yes",
            "Apo": "189",
            "Complex": "190|120|146",
            "Ligand": "Olmesartan|Olmesartan|Olmesartan",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4YAY",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "166",
            "Complex": "",
            "Ligand": "ZD-7155",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "AT2",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5UNG",
            "State": "Active",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "8ES",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5UNF",
            "State": "Active",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "8ES",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5UNH",
            "State": "Active",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "8EM",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Leukotriene",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "BLT1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5X33",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "BIIL-260",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Complement",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "C5a1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5O9H",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "H94WRL71FP",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6C1R",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "3-Cyclohexyl-D-alanine",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6C1Q",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "PMX53,9P2",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Cannabinoid",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "CB1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5XRA",
            "State": "Active",
            "CrystalLigand": "2-arachidonoylglycerol",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "GTPL9612",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5TGZ",
            "State": "Inactive",
            "CrystalLigand": "2-arachidonoylglycerol",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "162",
            "Complex": "",
            "Ligand": "SCHEMBL662960",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5XR8",
            "State": "Active",
            "CrystalLigand": "2-arachidonoylglycerol",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "8D0",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5U09",
            "State": "Inactive",
            "CrystalLigand": "2-arachidonoylglycerol",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "163",
            "Complex": "22|164",
            "Ligand": "Taranabant|Taranabant",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Chemokine",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "CCR2",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5T1A",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "VT5,73R",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "CCR5",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5UIW",
            "State": "Inactive",
            "CrystalLigand": "CCL11 CCL14 CCL16 CCL2 CCL3 CCL4 CCL5 CCL7 CCL8",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4MBS",
            "State": "Inactive",
            "CrystalLigand": "CCL11 CCL14 CCL16 CCL2 CCL3 CCL4 CCL5 CCL7 CCL8",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "118",
            "Complex": "119|67",
            "Ligand": "Maraviroc|Maraviroc",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "CCR9",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5LWE",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "Vercirnon",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "CXCR4",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "3ODU",
            "State": "Inactive",
            "CrystalLigand": "CXCL12α CXCL12β",
            "OldLigand": "CXCL12α CXCL12β",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "101",
            "Complex": "103|102",
            "Ligand": "isothiourea-1t|isothiourea-1t",
            "ClassCol": "isothiourea-1t",
            "KlassCol": "A"
          }, {
            "name": "3OE9",
            "State": "Inactive",
            "CrystalLigand": "CXCL12α CXCL12β",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "isothiourea-1t",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3OE0",
            "State": "Inactive",
            "CrystalLigand": "CXCL12α CXCL12β",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "104",
            "Complex": "",
            "Ligand": "peptide",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3OE8",
            "State": "Inactive",
            "CrystalLigand": "CXCL12α CXCL12β",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "isothiourea-1t",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3OE6",
            "State": "Inactive",
            "CrystalLigand": "CXCL12α CXCL12β",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "isothiourea-1t",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4RWS",
            "State": "Inactive",
            "CrystalLigand": "CXCL12α CXCL12β",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "98",
            "Complex": "89|86",
            "Ligand": "Viral macrophage inflammatory protein 2 (protein)|Viral macrophage inflammatory protein 2 (protein)",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Dopamine",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "D2",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "6CM4",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "risperidone",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "D3",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "3PBL",
            "State": "Inactive",
            "CrystalLigand": "dopamine",
            "OldLigand": "dopamine",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "105",
            "Complex": "106",
            "Ligand": "Eticlopride",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "D4",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5WIV",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "nemonapride",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5WIU",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "nemonapride",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Endothelin",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "ETB",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5X93",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "K-8794",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5GLH",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "158",
            "Complex": "168",
            "Ligand": "endothelin-1 (protein)",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5XPR",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5GLI",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Free fatty acid",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "FFA1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5TZY",
            "State": "Intermediate",
            "CrystalLigand": "long chain carboxylic acids",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "UNII-11612L5SPI, 7OS",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4PHU",
            "State": "Intermediate",
            "CrystalLigand": "long chain carboxylic acids",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "75",
            "Complex": "76",
            "Ligand": "Fasiglifam",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5TZR",
            "State": "Intermediate",
            "CrystalLigand": "long chain carboxylic acids",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "UNII-11612L5SPI",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5KW2",
            "State": "Intermediate",
            "CrystalLigand": "long chain carboxylic acids",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "6XQ",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Histamine",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "H1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "3RZE",
            "State": "Inactive",
            "CrystalLigand": "histamine",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "108",
            "Complex": "109|126",
            "Ligand": "doxepin|doxepin",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Lysophospholipid",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "LPA1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "4Z35",
            "State": "Inactive",
            "CrystalLigand": "LPA",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "184",
            "Complex": "",
            "Ligand": "ON9",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4Z34",
            "State": "Inactive",
            "CrystalLigand": "LPA",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "171",
            "Complex": "183",
            "Ligand": "ONO9780307",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4Z36",
            "State": "Inactive",
            "CrystalLigand": "LPA",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "",
            "Complex": "185",
            "Ligand": "ONO-3080573",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "LPA6",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5XSZ",
            "State": "Active",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Acetylcholine (musc.)",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "M1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5CXV",
            "State": "Inactive",
            "CrystalLigand": "acetylcholine",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "154",
            "Complex": "194",
            "Ligand": "Tiotropium",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "M2",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "4MQT",
            "State": "Active",
            "CrystalLigand": "acetylcholine",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "73|72",
            "Complex": "",
            "Ligand": "iperoxo",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3UON",
            "State": "Inactive",
            "CrystalLigand": "acetylcholine",
            "OldLigand": "acetylcholine",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "111",
            "Complex": "112",
            "Ligand": "(R)-(-)-3-Quinuclidinyl benzilate",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4MQS",
            "State": "Active",
            "CrystalLigand": "acetylcholine",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "68",
            "Complex": "69",
            "Ligand": "iperoxo",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "M3",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "4U15",
            "State": "Inactive",
            "CrystalLigand": "acetylcholine",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "93",
            "Complex": "174",
            "Ligand": "Tiotropium",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4U14",
            "State": "Inactive",
            "CrystalLigand": "acetylcholine",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "Tiotropium",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4DAJ",
            "State": "Inactive",
            "CrystalLigand": "acetylcholine",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "Tiotropium",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4U16",
            "State": "Inactive",
            "CrystalLigand": "acetylcholine",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "175",
            "Complex": "176",
            "Ligand": "Methscopolamine",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "M4",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5DSG",
            "State": "Inactive",
            "CrystalLigand": "acetylcholine",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "157",
            "Complex": "173",
            "Ligand": "Tiotropium",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Neurotensin",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "NTS1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5T04",
            "State": "Active",
            "CrystalLigand": "Neurotensin neurotensin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "TCEP",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4XES",
            "State": "Intermediate",
            "CrystalLigand": "Neurotensin neurotensin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4BUO",
            "State": "Inactive",
            "CrystalLigand": "Neurotensin neurotensin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "glycine",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3ZEV",
            "State": "Inactive",
            "CrystalLigand": "Neurotensin neurotensin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "glycine",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4GRV",
            "State": "Intermediate",
            "CrystalLigand": "Neurotensin neurotensin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "66",
            "Complex": "71",
            "Ligand": "neurotensin (protein)",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4BWB",
            "State": "Inactive",
            "CrystalLigand": "Neurotensin neurotensin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4XEE",
            "State": "Intermediate",
            "CrystalLigand": "Neurotensin neurotensin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "177",
            "Complex": "178",
            "Ligand": "citrate",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4BV0",
            "State": "Inactive",
            "CrystalLigand": "Neurotensin neurotensin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Orexin",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "OX1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "4ZJ8",
            "State": "Inactive",
            "CrystalLigand": "noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "186",
            "Complex": "187",
            "Ligand": "Suvorexant",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4ZJC",
            "State": "Inactive",
            "CrystalLigand": "noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "",
            "Complex": "188",
            "Ligand": "SB-674042",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "OX2",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5WS3",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "EMPA",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5WQC",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "EMPA",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4S0V",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "91",
            "Complex": "172",
            "Ligand": "Suvorexant",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "P2Y",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "P2Y1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "4XNW",
            "State": "Intermediate",
            "CrystalLigand": "ADP",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "180",
            "Complex": "181|182",
            "Ligand": "MRS-2500|MRS-2500",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4XNV",
            "State": "Intermediate",
            "CrystalLigand": "ADP",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "179",
            "Complex": "",
            "Ligand": "BPTU",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "P2Y12",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "4NTJ",
            "State": "Intermediate",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "AZD1283",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4PY0",
            "State": "Intermediate",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "79",
            "Complex": "80",
            "Ligand": "2-Mesatp",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4PXZ",
            "State": "Intermediate",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "77",
            "Complex": "78",
            "Ligand": "2-MeSADP",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Platelet-activating",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "PAF",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5ZKP",
            "State": "Active",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "Foropafant",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5ZKQ",
            "State": "Intermediate",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "9EU",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Proteinase-activated",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "PAR1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "3VW7",
            "State": "Intermediate",
            "CrystalLigand": "thrombin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "128",
            "Complex": "129|130",
            "Ligand": "Vorapaxar|Vorapaxar",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "PAR2",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5NDD",
            "State": "Intermediate",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "8TZ",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5NJ6",
            "State": "Intermediate",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5NDZ",
            "State": "Intermediate",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "8UN",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Opsins",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "Rhodopsin",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "2Z73",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5DYS",
            "State": "Active",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "1GZM",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4ZWJ",
            "State": "Active",
            "CrystalLigand": "",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "1HZX",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "1L9H",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4J4Q",
            "State": "Active",
            "CrystalLigand": "",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3AYM",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2PED",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5TE3",
            "State": "Active",
            "CrystalLigand": "",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6FK7",
            "State": "Active",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "DO5",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6FK6",
            "State": "Active",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "DOK",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4PXF",
            "State": "Active",
            "CrystalLigand": "",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3OAX",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4WW3",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3PQR",
            "State": "Active",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "125",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4BEZ",
            "State": "Active",
            "CrystalLigand": "",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2I35",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2G87",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5W0P",
            "State": "Active",
            "CrystalLigand": "",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4BEY",
            "State": "Active",
            "CrystalLigand": "",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2ZIY",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2HPY",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2J4Y",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6CMO",
            "State": "Active",
            "CrystalLigand": "",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "1F88",
            "State": "Inactive",
            "CrystalLigand": "",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5WKT",
            "State": "Active",
            "CrystalLigand": "",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5DGY",
            "State": "Active",
            "CrystalLigand": "",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6FK8",
            "State": "Active",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "DNZ",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2I37",
            "State": "Inactive",
            "CrystalLigand": "",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4X1H",
            "State": "Active",
            "CrystalLigand": "",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6FKB",
            "State": "Active",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "DLH",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5TE5",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "10,20-Methanoretinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6FKA",
            "State": "Active",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "DN5",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2X72",
            "State": "Active",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6FKD",
            "State": "Active",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "DL2",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3AYN",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4A4M",
            "State": "Active",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3C9M",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3PXO",
            "State": "Active",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3C9L",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6FK9",
            "State": "Active",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "DNK",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2I36",
            "State": "Inactive",
            "CrystalLigand": "",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6FKC",
            "State": "Active",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "DLB",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5EN0",
            "State": "Active",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3DQB",
            "State": "Active",
            "CrystalLigand": "",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "122",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "1U19",
            "State": "Inactive",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "12",
            "Complex": "",
            "Ligand": "retinal",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3CAP",
            "State": "Active",
            "CrystalLigand": "retinal",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Lysophospholipid",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "S1P1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "3V2Y",
            "State": "Inactive",
            "CrystalLigand": "sphingosine 1-phosphate",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "63",
            "Complex": "127",
            "Ligand": "W146",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3V2W",
            "State": "Inactive",
            "CrystalLigand": "sphingosine 1-phosphate",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "W146",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Unclassified",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "US28",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5WB1",
            "State": "Active",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4XT1",
            "State": "Active",
            "CrystalLigand": "CX3CL1",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "170",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4XT3",
            "State": "Active",
            "CrystalLigand": "CX3CL1",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5WB2",
            "State": "Active",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Neuropeptide Y",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "Y1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5ZBH",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "BMS-193885",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5ZBQ",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "9AO",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Adrenoceptors",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "β1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "4AMJ",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-|-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "141|142",
            "Complex": "167",
            "Ligand": "(S)-Carvedilol",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2Y00",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "13|14",
            "Complex": "15|16",
            "Ligand": "(R)-DOBUTAMINE|(R)-DOBUTAMINE",
            "ClassCol": "(R)-DOBUTAMINE",
            "KlassCol": "A"
          }, {
            "name": "2Y04",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "27|28",
            "Complex": "29|55",
            "Ligand": "Levalbuterol|Levalbuterol",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2Y03",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "23|24",
            "Complex": "25|26",
            "Ligand": "LEVISOPRENALINE|LEVISOPRENALINE",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2YCX",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "DB08347",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5F8U",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "DB08347",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2VT4",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "DB08347",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4AMI",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "138|139",
            "Complex": "140",
            "Ligand": "L-Bucindolol",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2YCY",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "DB08347",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2Y02",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "18|17",
            "Complex": "19|20",
            "Ligand": "Carmoterol|Carmoterol",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2YCW",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "56|64",
            "Complex": "57",
            "Ligand": "(-)-carazolol",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4BVN",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "143|144",
            "Complex": "58",
            "Ligand": "DB08347",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3ZPR",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-|-",
            "Simulated": "Yes",
            "Apo": "137|135|136",
            "Complex": "",
            "Ligand": "4-methyl-2-(piperazin-1-yl)quinoline",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2YCZ",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "I32",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2Y01",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "(R)-DOBUTAMINE",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4GPO",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3ZPQ",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "131|132",
            "Complex": "133|134",
            "Ligand": "4-(1-Piperazinyl)-1H-indole|4-(1-Piperazinyl)-1H-indole",
            "ClassCol": "4-(1-Piperazinyl)-1H-indole",
            "KlassCol": "A"
          }, {
            "name": "5A8E",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "147|148",
            "Complex": "150|149",
            "Ligand": "XTK|XTK",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "β2",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "3SN6",
            "State": "Active",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "P0G",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5JQH",
            "State": "Inactive",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "159",
            "Complex": "160",
            "Ligand": "(-)-carazolol",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2RH1",
            "State": "Inactive",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "11",
            "Complex": "",
            "Ligand": "(-)-carazolol",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3PDS",
            "State": "Inactive",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "107",
            "Complex": "",
            "Ligand": "ERC",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3NY8",
            "State": "Inactive",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "88",
            "Complex": "123",
            "Ligand": "JRZ",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5D5A",
            "State": "Inactive",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "(-)-carazolol",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2R4R",
            "State": "Inactive",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "isonorene|carazolol",
            "CrystalTransducer": "-",
            "Transducer": "-|-",
            "Simulated": "Yes",
            "Apo": "",
            "Complex": "9|10",
            "Ligand": "isonorene|carazolol",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4LDE",
            "State": "Active",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "113",
            "Complex": "121",
            "Ligand": "P0G",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3NYA",
            "State": "Inactive",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "100",
            "Complex": "124",
            "Ligand": "(-)-Alprenolol",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4QKX",
            "State": "Active",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "82",
            "Complex": "",
            "Ligand": "35V",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3D4S",
            "State": "Inactive",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "(-)-adrenaline (-)-noradrenaline",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "65",
            "Complex": "83",
            "Ligand": "timolol",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5D6L",
            "State": "Inactive",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "(-)-carazolol",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3P0G",
            "State": "Active",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "P0G",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5D5B",
            "State": "Inactive",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "(-)-carazolol",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5X7D",
            "State": "Inactive",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "(-)-carazolol",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3KJ6",
            "State": "Inactive",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4LDL",
            "State": "Active",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "114",
            "Complex": "115",
            "Ligand": "XQC",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "2R4S",
            "State": "Inactive",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "3NY9",
            "State": "Inactive",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "96",
            "Complex": "99",
            "Ligand": "JSZ",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4GBR",
            "State": "Inactive",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "(-)-carazolol",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4LDO",
            "State": "Active",
            "CrystalLigand": "(-)-adrenaline (-)-noradrenaline",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "116",
            "Complex": "117",
            "Ligand": "epinephrine",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }]
      }, {
        "name": "Opioid",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "A\t\t\t\t",
        "children": [{
          "name": "δ",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "4N6H",
            "State": "Inactive",
            "CrystalLigand": "β-endorphin dynorphin A dynorphin B endomorphin-1 [Leu]enkephalin [Met]enkephalin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-|-|-",
            "Simulated": "Yes",
            "Apo": "",
            "Complex": "4|8|145",
            "Ligand": "Naltrindole|Naltrindole|Naltrindole",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4EJ4",
            "State": "Inactive",
            "CrystalLigand": "β-endorphin dynorphin A dynorphin B endomorphin-1 [Leu]enkephalin [Met]enkephalin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "Naltrindole",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4RWD",
            "State": "Inactive",
            "CrystalLigand": "β-endorphin dynorphin A dynorphin B endomorphin-1 [Leu]enkephalin [Met]enkephalin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "84",
            "Complex": "",
            "Ligand": "peptide",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4RWA",
            "State": "Inactive",
            "CrystalLigand": "β-endorphin dynorphin A dynorphin B endomorphin-1 [Leu]enkephalin [Met]enkephalin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "peptide",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "κ",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "4DJH",
            "State": "Inactive",
            "CrystalLigand": "dynorphin A",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "59",
            "Complex": "60",
            "Ligand": "JDTic",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6B73",
            "State": "Active",
            "CrystalLigand": "dynorphin A",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "CVV",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "μ",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5C1M",
            "State": "Active",
            "CrystalLigand": "β-endorphin dynorphin A dynorphin B endomorphin-1 [Leu]enkephalin [Met]enkephalin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "151",
            "Complex": "169",
            "Ligand": "BU72",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4DKL",
            "State": "Inactive",
            "CrystalLigand": "β-endorphin dynorphin A dynorphin B endomorphin-1 [Leu]enkephalin [Met]enkephalin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "61",
            "Complex": "",
            "Ligand": "BF0",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6DDF",
            "State": "Active",
            "CrystalLigand": "β-endorphin dynorphin A dynorphin B endomorphin-1 [Leu]enkephalin [Met]enkephalin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "DAMGO",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "6DDE",
            "State": "Intermediate",
            "CrystalLigand": "β-endorphin dynorphin A dynorphin B endomorphin-1 [Leu]enkephalin [Met]enkephalin",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "DAMGO",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        }, {
          "name": "NOP",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "A\t\t\t\t",
          "children": [{
            "name": "5DHG",
            "State": "Inactive",
            "CrystalLigand": "nociceptin/orphanin FQ",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "156",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "4EA3",
            "State": "Inactive",
            "CrystalLigand": "nociceptin/orphanin FQ",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "62",
            "Complex": "70",
            "Ligand": "Banyu Compound-24",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }, {
            "name": "5DHH",
            "State": "Inactive",
            "CrystalLigand": "nociceptin/orphanin FQ",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "155",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "A",
            "KlassCol": "A\t\t\t\t"
          }]
        } ]
      }]
    }, {
      "name": "Class B1",
      "State": "-",
      "CrystalLigand": "-",
      "OldLigand": "-",
      "CrystalTransducer": "-",
      "Transducer": "-",
      "Simulated": "-",
      "Apo": "-",
      "Complex": "-",
      "Ligand": "-",
      "ClassCol": "-",
      "KlassCol": "B\t\t\t\t",
      "children": [{
        "name": "Corticotropin",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "B\t\t\t\t",
        "children": [{
          "name": "CRF1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "B\t\t\t\t",
          "children": [{
            "name": "4Z9G",
            "State": "Inactive",
            "CrystalLigand": "corticotrophin-releasing hormone",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "CP-376395",
            "ClassCol": "B",
            "KlassCol": "B\t\t\t\t"
          }, {
            "name": "4K5Y",
            "State": "Inactive",
            "CrystalLigand": "corticotrophin-releasing hormone",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "95",
            "Complex": "97",
            "Ligand": "CP-376395",
            "ClassCol": "B",
            "KlassCol": "B\t\t\t\t"
          }]
        }]
      }, {
        "name": "Calcitonin",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "B\t\t\t\t",
        "children": [{
          "name": "CT",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "B\t\t\t\t",
          "children": [{
            "name": "5UZ7",
            "State": "Active",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "B",
            "KlassCol": "B\t\t\t\t"
          }]
        }]
      }, {
        "name": "Glucagon family",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "B\t\t\t\t",
        "children": [{
          "name": "GLP-1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "B\t\t\t\t",
          "children": [{
            "name": "5NX2",
            "State": "Intermediate",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "peptide",
            "ClassCol": "B",
            "KlassCol": "B\t\t\t\t"
          }, {
            "name": "5VEW",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "97Y",
            "ClassCol": "B",
            "KlassCol": "B\t\t\t\t"
          }, {
            "name": "5VAI",
            "State": "Active",
            "CrystalLigand": "glucagon-like peptide 1",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "B",
            "KlassCol": "B\t\t\t\t"
          }, {
            "name": "6B3J",
            "State": "Active",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "B",
            "KlassCol": "B\t\t\t\t"
          }, {
            "name": "5VEX",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "97V",
            "ClassCol": "B",
            "KlassCol": "B\t\t\t\t"
          }]
        }, {
          "name": "Glucagon",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "B\t\t\t\t",
          "children": [{
            "name": "5XEZ",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "97V",
            "ClassCol": "B",
            "KlassCol": "B\t\t\t\t"
          }, {
            "name": "4L6R",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "110",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "B",
            "KlassCol": "B\t\t\t\t"
          }, {
            "name": "5YQZ",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "B",
            "KlassCol": "B\t\t\t\t"
          }, {
            "name": "5XF1",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "97V",
            "ClassCol": "B",
            "KlassCol": "B\t\t\t\t"
          }, {
            "name": "5EE7",
            "State": "Inactive",
            "CrystalLigand": "-",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "5MV",
            "ClassCol": "B",
            "KlassCol": "B\t\t\t\t"
          }]
        }]
      }]
    }, {
      "name": "Class C",
      "State": "-",
      "CrystalLigand": "-",
      "OldLigand": "-",
      "CrystalTransducer": "-",
      "Transducer": "-",
      "Simulated": "-",
      "Apo": "-",
      "Complex": "-",
      "Ligand": "-",
      "ClassCol": "-",
      "KlassCol": "C\t\t\t\t",
      "children": [{
        "name": "Metabotropic glutamate",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "C\t\t\t\t",
        "children": [{
          "name": "mGlu1",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "C\t\t\t\t",
          "children": [{
            "name": "4OR2",
            "State": "Inactive",
            "CrystalLigand": "L-glutamic acid",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "81",
            "Complex": "",
            "Ligand": "FITM",
            "ClassCol": "C",
            "KlassCol": "C\t\t\t\t"
          }]
        }, {
          "name": "mGlu5",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "C\t\t\t\t",
          "children": [{
            "name": "4OO9",
            "State": "Inactive",
            "CrystalLigand": "L-glutamic acid",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "74",
            "Complex": "",
            "Ligand": "Mavoglurant",
            "ClassCol": "C",
            "KlassCol": "C\t\t\t\t"
          }, {
            "name": "5CGC",
            "State": "Inactive",
            "CrystalLigand": "L-glutamic acid",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "152",
            "Complex": "",
            "Ligand": "51D",
            "ClassCol": "C",
            "KlassCol": "C\t\t\t\t"
          }, {
            "name": "6FFI",
            "State": "Inactive",
            "CrystalLigand": "L-glutamic acid",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "M-MPEP",
            "ClassCol": "C",
            "KlassCol": "C\t\t\t\t"
          }, {
            "name": "6FFH",
            "State": "Inactive",
            "CrystalLigand": "L-glutamic acid",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "Fenobam",
            "ClassCol": "C",
            "KlassCol": "C\t\t\t\t"
          }, {
            "name": "5CGD",
            "State": "Inactive",
            "CrystalLigand": "L-glutamic acid",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "153",
            "Complex": "193",
            "Ligand": "51E",
            "ClassCol": "C",
            "KlassCol": "C\t\t\t\t"
          }]
        }]
      }]
    }, {
      "name": "Class F",
      "State": "-",
      "CrystalLigand": "-",
      "OldLigand": "-",
      "CrystalTransducer": "-",
      "Transducer": "-",
      "Simulated": "-",
      "Apo": "-",
      "Complex": "-",
      "Ligand": "-",
      "ClassCol": "-",
      "KlassCol": "F\t\t\t\t",
      "children": [{
        "name": "Frizzled",
        "State": "-",
        "CrystalLigand": "-",
        "OldLigand": "-",
        "CrystalTransducer": "-",
        "Transducer": "-",
        "Simulated": "-",
        "Apo": "-",
        "Complex": "-",
        "Ligand": "-",
        "ClassCol": "-",
        "KlassCol": "F\t\t\t\t",
        "children": [{
          "name": "SMO",
          "State": "-",
          "CrystalLigand": "-",
          "OldLigand": "-",
          "CrystalTransducer": "-",
          "Transducer": "-",
          "Simulated": "-",
          "Apo": "-",
          "Complex": "-",
          "Ligand": "-",
          "ClassCol": "-",
          "KlassCol": "F\t\t\t\t",
          "children": [{
            "name": "5L7D",
            "State": "Inactive",
            "CrystalLigand": "constitutive",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "161",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "F",
            "KlassCol": "F\t\t\t\t"
          }, {
            "name": "5L7I",
            "State": "Inactive",
            "CrystalLigand": "constitutive",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "Yes",
            "Apo": "191",
            "Complex": "192",
            "Ligand": "Vismodegib",
            "ClassCol": "F",
            "KlassCol": "F\t\t\t\t"
          }, {
            "name": "5V56",
            "State": "Inactive",
            "CrystalLigand": "constitutive",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "GTPL9576",
            "ClassCol": "F",
            "KlassCol": "F\t\t\t\t"
          }, {
            "name": "4JKV",
            "State": "Inactive",
            "CrystalLigand": "constitutive",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "Taladegib",
            "ClassCol": "F",
            "KlassCol": "F\t\t\t\t"
          }, {
            "name": "5V57",
            "State": "Inactive",
            "CrystalLigand": "constitutive",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "GTPL9576",
            "ClassCol": "F",
            "KlassCol": "F\t\t\t\t"
          }, {
            "name": "4QIM",
            "State": "Inactive",
            "CrystalLigand": "constitutive",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "A8T",
            "ClassCol": "F",
            "KlassCol": "F\t\t\t\t"
          }, {
            "name": "4QIN",
            "State": "Inactive",
            "CrystalLigand": "constitutive",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "SG8",
            "ClassCol": "F",
            "KlassCol": "F\t\t\t\t"
          }, {
            "name": "4N4W",
            "State": "Inactive",
            "CrystalLigand": "constitutive",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "SANT-1",
            "ClassCol": "F",
            "KlassCol": "F\t\t\t\t"
          }, {
            "name": "4O9R",
            "State": "Inactive",
            "CrystalLigand": "constitutive",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "CYCLOPAMINE",
            "ClassCol": "F",
            "KlassCol": "F\t\t\t\t"
          }, {
            "name": "6D35",
            "State": "Inactive",
            "CrystalLigand": "constitutive",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "-",
            "ClassCol": "F",
            "KlassCol": "F\t\t\t\t"
          }, {
            "name": "6D32",
            "State": "Inactive",
            "CrystalLigand": "constitutive",
            "OldLigand": "-",
            "CrystalTransducer": "-",
            "Transducer": "-",
            "Simulated": "No",
            "Apo": "",
            "Complex": "",
            "Ligand": "CYCLOPAMINE",
            "ClassCol": "F",
            "KlassCol": "F"
          }]
        }]
      }]
    }]
  }*/

    data=$("#chart").data("chart_data")

   // var screenh=screen.height;
   // var plotheight= screenh-300;

    //var maxwidth=826;
    var width = 1000;
    var height = width
    var radius = (width / 2) - 50
    var width_arc_innerRadius = (width/2) - 40 //(width / 2) - 10;
    var width_arc_outerRadius = (width/2) - 38 //width_arc_innerRadius + 10;
  
    tree = data => d3.tree()
    .size([2 * Math.PI, radius])
    .separation((a, b) => (a.parent == b.parent ? 1 : 2) / a.depth)
    (d3.hierarchy(data))

    const root = tree(data);

    //d3.select("#section_cordplot").style("height", wdiv + "px");

    var mydiv = d3.select("#chart") 
//                .style("width", wdiv + "px")
//                .style("height", wdiv + "px")

    function zoomed() {
        // svg.attr("transform", d3.event.transform);
        // console.log(d3.event.transform);
        // var xy = d3.mouse(this);  
        // var transform = d3.zoomTransform(svg.node());
        // var xy1 = transform.invert(xy);
        // console.log(xy1);
        svg.attr("transform", "translate(" + (d3.event.transform["x"]+width+130) / 2 + "," + (d3.event.transform["y"]+height+130) / 2 + ")scale(" + d3.event.transform["k"] + ")")
      }
    
    var zoom = d3.zoom()
      .scaleExtent([1, 10])
      // .translateExtent([[-1*(width + 130), -1*(height + 130)], [width, height]])
      .extent([[0, 0], [width, height]])
      .on("zoom", zoomed)

    const svg = mydiv.append("svg")
       // .attr("width", "100%")
       // .attr("height", "100%")
      // .on("zoom", zoomed)
      // .call(zoom) 
      .attr("style","display:block;margin:auto;")
      .attr('viewBox','0 0 '+(width + 130)+' '+(width + 130))
      .attr('preserveAspectRatio','xMinYMin')
      .style("font", "10px sans-serif")
      .style("border", "1px solid black")
      .style("border-color","#BF3C1F")
      .append("svg:g")
      .attr("transform", "translate(" + (width+130) / 2 + "," + (width+130) / 2 + ")")
      ;

    mydiv.on("zoom", zoomed);
    mydiv.call(zoom);
    

    var transform = d3.zoomIdentity //<-- create your transform with your initialScale
      .translate(0, 0)
      .scale(1);

    $("#Reset").click(() => {
      mydiv.transition()
        .duration(750)
        .call(zoom.transform, transform)
        // .call(zoom.translateTo, 500, 500)

        // .attr("transform", "translate(" + (width+140) / 2 + "," + (width+140) / 2 + ")")
    });

    const link = svg.append("g")
        .attr("fill", "none")
        .attr("stroke-opacity", 0.4)
        .attr("stroke-width", 1.5)
      .selectAll("path")
      .data(root.links())
      .enter().append("path")
        .attr("d", d3.linkRadial()
            .angle(d => d.x)
            .radius(d => d.y))
      .attr("stroke", d => d.target.data.Simulated == "Yes" ? "black" : d.target.data.Simulated == "No" ? "lightgrey" : "black")
    
    let current_circle = undefined;

    let setstyle_fontweight = function(d,is_sel){
        if (is_sel){
            return "bold"
        } else{
            if (d.depth === 1) {
              return "500"
            } else if (d.depth === 2) {
              return "300"
            } else if (d.depth === 3) {
              return "200"
            } else if (d.depth === 4) {
              return "100"
            }
        }
    }
    let setstyle_font =function(d,is_sel){
        if (is_sel){
          if (d.depth === 1) {
            return "12px sans-serif"
          } else if (d.depth === 2) {
            return "10px sans-serif"
          } else if (d.depth === 3) {
            return "8px sans-serif"
          } else if (d.depth === 4) {
            return "2px monospace"
          }    
      } else {
          if (d.depth === 1) {
            return "10px sans-serif"
          } else if (d.depth === 2) {
            return "8px sans-serif"
          } else if (d.depth === 3) {
            return "6px sans-serif"
          } else if (d.depth === 4) {
            return "2px monospace"
          }
      }
    }

    function limit_text(mystr,mymax){
        if (mystr.length >mymax){
            mystr=mystr.slice(0,mymax-3)+"..."
        }
        return (mystr)
    }

    function get_this_transform(fthis){
        var trans_s=fthis.getAttribute("transform");
        var rotation=Number(trans_s.match(/rotate\(((\w|\.|-)*)\)/)[1]);
        transl_xy= trans_s.match(/translate\(((\w|,|-|\.)*)\)/)[1];
        transl_xy_l=transl_xy.split(",")
        var transl_x=Number(transl_xy_l[0]); //450
        var transl_y=Number(transl_xy_l[1]); //0
        return [rotation,transl_x,transl_y]
    }

  function get_svg_center(){
      var $this = $("svg");
      var offset = $this.offset();
      var width = $this.width();
      var height = $this.height();
      var centerX = offset.left + width / 2;
      var centerY = offset.top + height / 2;
      return [centerX,centerY]
  }


  function calc_rotation(x,y,rotation){
      angle=(rotation*Math.PI)/180;
      var translate_x= x*Math.cos(angle)- y*Math.sin(angle);
      var translate_y= x*Math.sin(angle) + y*Math.cos(angle);
      return [translate_x,translate_y]
  }


    function selectOccupation(d,fthis,actiontype) {
       var doNotDisplay=false;
       if (actiontype=="click"){
        popupID="details-popup";
        popupsel="#details-popup";
        rectID="rect"
        rect_sel="#rect"
        selecitonstyle_class="clickednode";
        selecitonstyle_sel=".clickednode";
        if (d.height>=1){
          doNotDisplay=true;
        }
       } else {
        popupID="details-popup_hov";
        popupsel="#details-popup_hov";
        rectID="rect_hov";
        rect_sel="#rect_hov";
        selecitonstyle_class="hoverednode";
        selecitonstyle_sel=".hoverednode";
       }
      // cleanup previous selected circle
      if(current_circle !== undefined){      
        svg.selectAll(popupsel).remove();
      }
      //Remove hover/clicked class to previously selected
      var previous_sel=svg.selectAll(selecitonstyle_sel);
      previous_sel
          .attr("class",function(){ 
              var classli=this.classList;
              classli.remove(selecitonstyle_class)
              return classli
          });

      //Return to normal the style of previously selected
      previous_sel.selectAll("text")
            .style("font",function(t){
                var nodeclasses= this.parentNode.classList;
                if (nodeclasses.length == 0){
                  return setstyle_font(t,false)
                } else {
                  return setstyle_font(t,true)
                }

            })
            .style("font-weight",function(t){
                var nodeclasses= this.parentNode.classList;
                if (nodeclasses.length == 0){
                  return setstyle_fontweight(t,false)
                } else {
                  return setstyle_fontweight(t,true)
                }
            })

      if ((d.data.name) && (!doNotDisplay)){
            current_circle = d3.select(fthis);

            current_circle
                .attr("class",function(){ 
                    var classli=this.classList;
                    if (! classli.contains(selecitonstyle_class)){
                        classli.add(selecitonstyle_class)
                    }
                    return classli
                })
                .raise();

            current_circle.selectAll("text")
              .style("font",  setstyle_font(d,true))
              .style("font-weight",setstyle_fontweight(d,true))
              .raise();
              // .attr("x",function(t){
              //   var transform = this.getAttribute("transform");
              //   if (t.depth == 4) {
              //     if (transform.includes("rotate")) {
              //         return "-40"
              //       }
              //       else {
              //         return "40"
              //       }
              // }});
            var this_transf=get_this_transform(fthis);
            var rotation =this_transf[0];
            var transl_x =this_transf[1];
            var transl_y =this_transf[2];

            let textblock = svg.selectAll(popupsel)
              .data([d])
              .enter()
              .append("g")
              .attr("id", popupID)
              .attr("class","details")
              .attr("font-size", 14)
              .attr("font-family", "sans-serif")
              .attr("fill", "white")
              .attr("text-anchor", "start")
              .attr("transform", d => `translate(`+transl_x+`, `+transl_y+`)`);
        
            textblock.append("rect")
              .attr("id",rectID)
              .attr("rx", "10")
              .attr("ry", "10")
              .attr("x", "-10")
              .attr("y", "-20")
      
            textblock.append("text")
              .text(d.data.name)
              .attr("font-weight", "bold");
            
              if (!( d.data.State == "-" || d.data.State == undefined )){
                  textblock.append("text")
                    .text("State: " + d.data.State)
                    .attr("y", "24");
              } 
              if (!( d.data.Simulated == "-" || d.data.Simulated == undefined )){
                k=0
                /*
                  textblock.append("text")
                    .text("Deposed ligand: " +limit_text( d.data.CrystalLigand,34))
                    .attr("y", "40")
                        .append("title").text(d.data.CrystalLigand);
                  var k=0;
                  if( (d.data.CrystalTransducer !== "-") && (d.data.CrystalTransducer !== "") ){ 
                    k=1;
                    textblock.append("text")
                      .text("Deposed transducer: " + limit_text(d.data.CrystalTransducer,30))
                      .attr("y",  parseInt(40+16*k))
                        .append("title").text(d.data.CrystalTransducer);
                  }*/
                  var j=0;
                  var base_url = window.location.origin;
                  if( (d.data.Apo !== "-") && (d.data.Apo !== "") && (d.data.Apo !== undefined)  ){ 
                    var ApoNum = d.data.Apo.split("|");
                    if (actiontype=="click"){
                          for (j = 0; j < ApoNum.length; j++) { 
                            textblock.append("a")
                              .attr("xlink:href", ApoNum[j] != "-" ? base_url+"/view/"+ApoNum[j] : null) 
                              .attr("target","_blank")
                              .append("text")
                                .style("cursor", "pointer")
                                .text("Apo simulation: ID " + ApoNum[j])
                                .attr("y",  parseInt(40+16*(j+k)))
                                .attr("fill", ApoNum[j] != "-" ? '#85bae0' : 'grey' )

                          }
                      } else {
                          if (ApoNum){
                              j=1;
                              textblock.append("text")
                                  .text("# Apo simulation settings: " + ApoNum.length)
                                  .attr("y",  parseInt(24+16*(j+k)));
                              }
                      }
                  }
                  if( (d.data.Complex !== "-") && (d.data.Complex !== "") && (d.data.Complex !== undefined) ){ 
                    var i;
                    var ComplexNum = d.data.Complex.split("|");


                    var Ligandname = d.data.Ligand.split("|");
                    var TransducerNum = d.data.Transducer.split("|");

                    if (actiontype=="click"){
                          var Ligandname = d.data.Ligand.split("|");
                          var TransducerNum = d.data.Transducer.split("|");
                          for (i = 0; i < ComplexNum.length; i++) { 
                            textblock.append("a")
                              .attr("xlink:href", ComplexNum[i] != "-" ? base_url+"/view/"+ComplexNum[i] : null) 
                              .attr("target","_blank")
                              .append("text")
                                .style("cursor", "pointer")
                                .text(limit_text("Complex simulation: ID " + ComplexNum[i] + (Ligandname[0] != "-" ||  TransducerNum[0] != "-" ? " (" :"") + (Ligandname[i] != "-" ? "lig: "+Ligandname[i] :"") + (TransducerNum[i] !="-" ? "; transducer: "+TransducerNum[i]+";" :"") + (Ligandname[0] != "-" ||  TransducerNum[0] != "-" ? ")" :""),50))
                                .attr("y",  parseInt(40+16*(i+j+k)))
                                .attr("fill", ComplexNum[i] != "-" ? '#85bae0' : 'grey' )
                                    .append("title").text("Complex simulation: ID " + ComplexNum[i] + (Ligandname[0] != "-" ||  TransducerNum[0] != "-" ? " (" :"") + (Ligandname[i] != "-" ? "lig: "+Ligandname[i] :"") + (TransducerNum[i] !="-" ? "; transducer: "+TransducerNum[i]+";" :"") + (Ligandname[0] != "-" ||  TransducerNum[0] != "-" ? ")" :""));

                          }
                      } else {
                          if (ApoNum){
                              i=1;
                              textblock.append("text")
                                  .text("# Complex simulation settings: " + ApoNum.length)
                                  .attr("y",  parseInt(24+16*(i+j+k)));
                          }
                      }
                  }
                  l=0;
                  if (actiontype!="click"){
                      if(d.data.Simulated == "-"){
                          l=1;
                          textblock.append("text")
                              .text("# Total simulation settings: " + getAllSims(d))
                              .attr("y",  parseInt(40+16*(i+j+k+l)));
                      }
                  }
            }
      
          //Position rect
          var popup_size = document.getElementById(popupID).getBBox();
          var whole_popup_width=popup_size.width + 40;
          var whole_popup_height=popup_size.height + 15;
          svg.select(rect_sel)
              .attr("width",(whole_popup_width) + "px")
              .attr("height",(whole_popup_height) + "px")
      
          //Close btn
          if (actiontype=="click"){
              textblock.append('text')
                  .text('X')
          //        .attr("dominant-baseline","text-before-edge")
                  //.attr("font-family", "sans-serif")
                  .attr("font-size", "10px")
                  .attr("font-weight", "bold")
                  .attr("x", (popup_size.width +10  )+"px")
                  .attr("id", "closePopup")
                  .attr("fill", "#a6a6a6");
          }
      
          //Move popup ---------------------------
            svg_cent=get_svg_center();
            centerX=svg_cent[0];
            centerY=svg_cent[1];

            var pos_fin=calc_rotation(transl_x,transl_y,rotation);
            var translate_x=pos_fin[0];
            var translate_y=pos_fin[1];

          // -- Correciton so that box is always inside of the plot
          var rotaiton_val=Number(current_circle.attr("transform").match(/rotate\((.*)\)/)[1]);//from -90 to 270
          // ---- Height
          var M=-(whole_popup_height);
          rotaiton_val=rotaiton_val+90;//from 0 to 360
          rot_norm=rotaiton_val/360;
          var b=0;
          if (rot_norm <0.5){
            b =rot_norm/0.5;
          } else {
            b=(rot_norm-1)/-0.5
          }
          var extra_space_b=(30*(Math.abs(1-b)))

          // ----Width
          var N=-(whole_popup_width);
          var rotaiton_val2=rotaiton_val-270;
          if (rotaiton_val2<0){
            rotaiton_val2=rotaiton_val2+360
          };
          rot_norm2=rotaiton_val2/360;
          var a=0;
          if (rot_norm2 <0.5){
            a =rot_norm2/0.5;
          } else {
            a=(rot_norm2-1)/-0.5
          }

          if (rot_norm>0.5){
            var added_w=20;
          } else {
            var added_w=N ;
          }

          // --Apply transformation
          var translate_x_fin= (translate_x+added_w );
          var translate_y_fin= (translate_y+(M*b)+extra_space_b);

          textblock
                  .attr("transform", "translate(" + translate_x_fin
                            + "," + translate_y_fin + ")");
             
      }
    }
  
    
    let getAllSims = function(d) {
      var numSims = 0;
      var v;
      for (v = 0; v < d.children.length; v++) {
        if (d.children[v].data.Simulated == "-") {
          var vv;
          for (vv = 0; vv < d.children[v].children.length; vv++) {
            if (d.children[v].children[vv].data.Simulated == "-") {
              var vvv;
              for (vvv = 0; vvv < d.children[v].children[vv].children.length; vvv++) {
                if (d.children[v].children[vv].children[vvv].data.Simulated == "-") {
                  var vvvv;
                  for (vvv = 0; vvv < d.children[v].children[vv].children[vvv].children.length; vvv++) {
                    if ((d.children[v].children[vv].children[vvv].children[vvvv].data.Apo.split("|")[0] !== "-") && (d.children[v].children[vv].children[vvv].children[vvvv].data.Apo.split("|")[0] !== "")) {
                      numSims = numSims + d.children[v].children[vv].children[vvv].children[vvvv].data.Apo.split("|").length
                    }
                    if ((d.children[v].children[vv].children[vvv].children[vvvv].data.Complex.split("|")[0] !== "-") && (d.children[v].children[vv].children[vvv].children[vvvv].data.Complex.split("|")[0] !== "")) {
                      numSims = numSims + d.children[v].children[vv].children[vvv].children[vvvv].data.Complex.split("|").length
                    }
                  }
                } else {
                  if ((d.children[v].children[vv].children[vvv].data.Apo.split("|")[0] !== "-") && (d.children[v].children[vv].children[vvv].data.Apo.split("|")[0] !== "")) {
                    numSims = numSims + d.children[v].children[vv].children[vvv].data.Apo.split("|").length
                  }
                  if ((d.children[v].children[vv].children[vvv].data.Complex.split("|")[0] !== "-") && (d.children[v].children[vv].children[vvv].data.Complex.split("|")[0] !== "")) {
                    numSims = numSims + d.children[v].children[vv].children[vvv].data.Complex.split("|").length
                  }
                }
              }
            } else {
              if ((d.children[v].children[vv].data.Apo.split("|")[0] !== "-") && (d.children[v].children[vv].data.Apo.split("|")[0] !== "")) {
                numSims = numSims + d.children[v].children[vv].data.Apo.split("|").length
              }
              if ((d.children[v].children[vv].data.Complex.split("|")[0] !== "-") && (d.children[v].children[vv].data.Complex.split("|")[0] !== "")) {
                numSims = numSims + d.children[v].children[vv].data.Complex.split("|").length
              }
            }
          }
        } else {
          if ((d.children[v].data.Apo.split("|")[0] !== "-") && (d.children[v].data.Apo.split("|")[0] !== "")) {
            numSims = numSims + d.children[v].data.Apo.split("|").length
          }
          if ((d.children[v].data.Complex.split("|")[0] !== "-") && (d.children[v].data.Complex.split("|")[0] !== "")) {
            numSims = numSims + d.children[v].data.Complex.split("|").length
          }
        }
      }
      return numSims
    }
    
    function wrap() { // To wrap long text
        var self = d3.select(this),
            textLength = self.node().getComputedTextLength(),
            text = self.text();
        while (textLength > (70 - 2 * 1) && text.length > 0) { // (width - 2 * padding)
            text = text.slice(0, -1);
            self.text(text + '...');
            textLength = self.node().getComputedTextLength();
        }
    } 

    var arc = d3.arc()
      .innerRadius(width_arc_innerRadius)
      .outerRadius(width_arc_outerRadius)
      .padAngle(2.5)
      .padRadius(0.6)
      .cornerRadius(10)
  
  
    svg.append('path')
      .style("fill", "#575757 ")
      .style("stroke", "#575757")
      .attr('d', arc({
        startAngle: 0.01,
        endAngle: 5.55
      }))
  
    svg.append('path')
      .style("fill", "#898989") //898989
      .style("stroke", "#898989")
      .attr('d', arc({
        startAngle: 5.57,
        endAngle: 5.89
      }))
  
    svg.append('path')
      .style("fill", "#575757")
      .style("stroke", "#575757") //d5d5d5
      .attr("stroke-width", "1")
      .attr('d', arc({
        startAngle: 5.9,
        endAngle: 6.05
      }))
  
    svg.append('path')
      .style("fill", "#898989") //#4169E1")
      .style("stroke", "#898989") //#4169E1")
      .attr("stroke-width", "1")
      .attr('d', arc({
        startAngle: 6.06,
        endAngle: 6.27
      }))
  
    link.enter().append("path")
      .attr("d", d3.linkRadial()
        .angle(d => d.x)
        .radius(d => d.y))
      .attr("stroke", d => d.target.data.Simulated == "Yes" ? "black" : d.target.data.Simulated == "No" ? "lightgrey" : "black")
      .attr("stroke", d => d.target.data.Simulated == "Yes" ? (d.target.data.KlassCol == "A" ? "#898989" : d.target.data.KlassCol == "B" ? "#575757" : d.target.data.KlassCol == "C" ? "#898989" : d.target.data.KlassCol == "F" ? "#575757" : "black") : d.target.data.Simulated == "No" ? "lightgrey" : (d.target.data.KlassCol == "A" ? "#898989" : d.target.data.KlassCol == "B" ? "#575757" : d.target.data.KlassCol == "C" ? "#898989" : d.target.data.KlassCol == "F" ? "#575757" : "black"))
  

    const node = svg.append("g")
      .attr("stroke-linejoin", "round")
      .attr("stroke-width", 3)
      .selectAll("g")
      .data(root.descendants().reverse())
      .enter().append("g")
      .attr("transform", d => `
              rotate(${d.x * 180 / Math.PI - 90})
              translate(${d.y},0)
            `);
    //return graph;
    let displayAncestors = (d) => {
      svg.property("value", d).dispatch("input");
    }

    node.append("circle")
      .attr("fill", "#575757")
      .attr("r", d => d.data.Simulated == "Yes" ? 2 : d.data.Simulated == "No" ? 1 : 2)
      .attr("class",function(d) {
        if (d.height==0){
          return "clickable"
        } else {
          return ""
        }
      })

    node.append("circle")
      .attr("fill", d => d.data.State == "Active" ? "green" : d.data.State == "Inactive" ? "red" : d.data.State == "Intermediate" ? "orange" : "black")
      .attr("r", 1.5)
      .attr("class",function(d) {
        if (d.height==0){
          return "clickable"
        } else {
          return ""
        }
      })
    node.append("text")
      .attr("fill", d => d.data.Simulated == "Yes" ? "black" : d.data.Simulated == "No" ? "lightgrey" : "black")
      .attr("dy", "0.31em")
      .attr("x", d => d.x < Math.PI === !d.children ? 6 : -6)
      .attr("text-anchor", function(d) {
        return d.x < Math.PI ? "start" : "end";
      })
      .attr("transform", function(d) {
        return d.x < Math.PI ? "translate(15)" : "translate(15) rotate(180)";
      })
      .style("font", function(d) {
        return setstyle_font(d,false)
      })
      .style("font-weight", function(d) {
        return setstyle_fontweight(d,false)
      })
      .text(function(d) { return d.data.name; }).each(wrap)
      .attr("class",function(d) {
        if (d.height==0){
          return "clickable"
        } else {
          return ""
        }
      })
      .clone(true).lower()
      .attr("stroke", "white")
      .on("mouseover", displayAncestors)
      .text(function(d) { return d.data.name; }).each(wrap)

    node.on("click", function(d) {
      selectOccupation(d, this, "click");
    })
    $("#chart").on("click", "#closePopup", function() {
      var mypopup=svg.selectAll("#details-popup");
      mypopup.remove()
      var previous_sel=svg.selectAll(".clickednode");
      previous_sel
          .attr("class","");
      previous_sel.selectAll("text")
            .style("font",function(t){
                return setstyle_font(t,false)
            })
            .style("font-weight",function(t){
                  return setstyle_fontweight(t,false)
            })

    });
    node.on("mouseover", function(d) {
      selectOccupation(d, this, "hover");
    })
    node.on("mouseout", function() {
      svg.selectAll("#details-popup_hov").remove()
    });
     
    const leg = svg.append("g")
      .attr("transform", "translate(200,-600)")
      .attr("id","legend_box");
    
    leg.append("rect")
      .attr("rx", "5")
      .attr("ry", "5")
      .attr("x", "185")
      .attr("y", "115")
      .attr("width", "120px")
      .attr("height", "70px")
      .attr("fill", "white")
      .style("background-color","blue");
    leg.append("circle")
      .attr("cx",200)
      .attr("cy",130)
      .attr("r", 4)
      .style("fill", "#008000");
    leg.append("circle")
      .attr("cx",200)
      .attr("cy",150)
      .attr("r", 4)
      .style("fill", "#F5B745");
    leg.append("circle")
      .attr("cx",200)
      .attr("cy",170)
      .attr("r", 4)
      .style("fill", "#F80000");
    leg.append("text")
      .attr("x", 215)
      .attr("y", 135)
      .text("Active")
      .style("font", "12px sans-serif")
      .attr("alignment-baseline","middle");
    leg.append("text")
      .attr("x", 215)
      .attr("y", 155)
      .text("Intermediate")
      .style("font", "12px sans-serif")
      .attr("alignment-baseline","middle");
    leg.append("text")
      .attr("x", 215)
      .attr("y", 175)
      .text("Inactive")
      .style("font", "12px sans-serif")
      .attr("alignment-baseline","middle");




//--------------------------------------------
    // $("#tabs_col").css("height",$("#plot_col").css("height"));
    // function control_row_size(){
    //   var plot_h = $("#plot_col").css("height");
    //   var plot_h_num = Number(plot_h.replace("px",""));
    //   if (plot_h_num<700){
    //     plot_h="700px";
    //   }
    //   $("#tabs_col").css("height",plot_h);
    // }
    // control_row_size();
    // $(window).resize(function(){
    //       control_row_size();
    // });
  


    $(".tab_trigger").click(function(){
        var select=$(this).data("target")
        $(select).tab('show');
    })


//-------------------------- Stats charts


  function drawCharts_subm() {
          
          var data_pre=$("#stats_subm").data("subm_data");
          var datainfo=[['Date', 'GPCRmd simulations',{ role: 'annotation' }, "Trajectories", { role: 'annotation' }]];
          var data_all = datainfo.concat(data_pre);
          var data = google.visualization.arrayToDataTable(data_all);


          var options = {
            hAxis: {title: 'Date',slantedTextAngle:90},
            vAxis: {title: "", minValue: 0, maxvalue: 55 , gridlines: {count: 0, color:"#bfbfbf"}},
            legend: {position:"top"},
            annotations: {stem:{length:2}},
            colors: ['#423F3E', '#BF3C1F'],
            chartArea:{width:370,top:40}

          };

          var chart = new google.visualization.AreaChart(document.getElementById('stats_subm'));
          
          
          
          chart.draw(data, options);
      }
      google.load("visualization", "1", {packages:["corechart"],'callback': drawCharts_subm});


/*      function drawChart_class() {
        var data_pre=$("#stats_class").data("class_data");
        var datainfo=[['Class', 'GPCR']];
        var data_all = datainfo.concat(data_pre);
        var data = google.visualization.arrayToDataTable(data_all);

        var options = {
          legend: 'none',
          pieSliceText: 'label',
          width:300,
          height:350,
          chartArea:{width:280,height:280}
        };

        var chart = new google.visualization.PieChart(document.getElementById('stats_class'));

        chart.draw(data, options);
      }

      google.load("visualization", "1", {packages:["corechart"],'callback': drawChart_class});
*/

      function drawChart_famstats() {

        var data_all = $("#fam_stats").data("fam_stats");
        var data = google.visualization.arrayToDataTable(data_all);
        var options = {
          slices: {
            0: { color: '#D96B52' },
            1: { color: '#837d7b' }
          },
          pieHole: 0.4,
          // chartArea:{left: 125, top:-50, width:650, height:650 },
          pieSliceTextStyle:{
            color:"white", 
            fontSize:12,
            position: 'start',
          },
          width: 400,
          height: 400,
          legend:{ alignment:"center", position:'none', textStyle: {fontSize: 12}},
          pieSliceText: 'none',
          sliceVisibilityThreshold: 0,             
          // legend: 'labeled',
        };

        var chart = new google.visualization.PieChart(document.getElementById('fam_stats'));

        chart.draw(data, options);
      }
      google.load("visualization", "current", {packages:["corechart"],'callback': drawChart_famstats});



      function drawChart_subtypestats() {

        var data_all = $("#subtype_stats").data("subtype_stats");
        var data = google.visualization.arrayToDataTable(data_all);
        var options = {
          slices: {
            0: { color: '#D96B52' },
            1: { color: '#837d7b' }
          },
          pieHole: 0.4,
          // chartArea:{left: 125, top:-50, width:550, height:550 },
          pieSliceTextStyle:{
            color:"white", 
            fontSize:12,
            position: 'start',
          },
          width: 400,
          height: 400,
          legend:{ alignment:"center", position:'none', textStyle: {fontSize: 12}},
          pieSliceText: 'none',
          sliceVisibilityThreshold: 0,             
          // legend: 'labeled',
        };

        var chart = new google.visualization.PieChart(document.getElementById('subtype_stats'));

        chart.draw(data, options);
      }
      google.load("visualization", "1", {packages:["corechart"],'callback': drawChart_subtypestats});

      function drawChart_pdbstats() {

        var data_all = $("#pdb_stats").data("pdb_stats");
        var data = google.visualization.arrayToDataTable(data_all);
        var options = {
          slices: {
            0: { color: '#D96B52' },
            1: { color: '#837d7b' }
          },
          pieHole: 0.4,
          // chartArea:{left: 125, top:-50, width:550, height:550 },
          pieSliceTextStyle:{
            color:"white", 
            fontSize:12,
            position: 'start',
          },
          width: 400,
          height: 400,
          legend:{ alignment:"center", position:'none', textStyle: {fontSize: 12}},
          pieSliceText: 'none',
          sliceVisibilityThreshold: 0,             
          // legend: 'labeled',
        };

        var chart = new google.visualization.PieChart(document.getElementById('pdb_stats'));

        chart.draw(data, options);
      }
      google.load("visualization", "1", {packages:["corechart"],'callback': drawChart_pdbstats});

      /*      var data_act_pre=$("#stats_act").data("act_data");
      function drawChart_activation() {
        var datainfo=[['State', 'GPCR']];
        var data_all = datainfo.concat(data_act_pre);
        console.log(data_all)
        var data = google.visualization.arrayToDataTable(data_all);

        var options = {
          legend: 'none',
          pieSliceText: 'label',
          width:300,
          height:350,
          chartArea:{width:280,height:280},
          //pieStartAngle: -50,
          pieSliceTextStyle: {
            color: 'black',
            fontSize: 12
          }
        };

        var chart = new google.visualization.PieChart(document.getElementById('stats_act'));

        chart.draw(data, options);
      }
      if (data_act_pre){
            google.load("visualization", "1", {packages:["corechart"],'callback': drawChart_activation});
      }


//       */
})


