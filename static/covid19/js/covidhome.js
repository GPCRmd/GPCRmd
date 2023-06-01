$(document).ready(function(){
  $('.tooltip_imageclickable').tooltip({
      html: true,
      placement: 'auto',
      container: 'body'

  }); 
  $('.hovertexttooltip').tooltip({
      html: true,
      placement: 'auto',
      container: 'body'
  }); 

  var mouseX;
  var mouseY;
  $(document).mousemove( function(e) {
     // mouse coordinates
     mouseX = e.pageX; 
     mouseY = e.pageY;

  });  
  $(document).on("mouseenter",".tooltip_imageclickable",function(e){
      $(".tooltip").css({'top':mouseY - 70,'left':mouseX });
  })
//-------- AJAX --------

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    //-------- fin ajax --------
  function encode (sth) {return encodeURIComponent(sth).replace(/%20/g,'+');}

  function platform_search(){
      var search_val=$(".input_search").val()
      if (search_val){
        window.location.href = '/covid19/search/?pre='+encode(search_val);
      }

  }

  $(".btn_input_search").click(function(){
    platform_search()
  })
  $('.input_search').keypress(function (e) {
    if (e.which == 13) {
      platform_search()
    }
  })

  function datestr_to_obj(myval){
    splitdate=myval.split("-");
    newval=new Date(Number(splitdate[0]), Number(splitdate[1])-1, Number(splitdate[2]))
    return newval
  }

  function obtain_data_values(data){
    for (e=0; e<data.length ; e++ ){
        myel=data[e];
        myval=myel["value"];
        if (typeof myval =="string"){
          if( myval.indexOf("-")>=0){
            newval=datestr_to_obj(myval);
            myel["value"]=newval
          }

        }
    }
    return data
  }

  function gradient_legend(data){
    data=obtain_data_values(data)

    var minnmaxli = [data[0]["value"],data[data.length -1]["value"]];
    var extent = minnmaxli;
    
    var padding = 9;
    var width = 175;
    var innerWidth = width - (padding * 2);
    var barHeight = 8;
    var height = 28;

    var xScale = d3.scaleLinear()
        .range([0, innerWidth])
        .domain(extent);

    var xTicks = [data[0]["value"],data[data.length -1]["value"]];
    var xAxis = d3.axisBottom(xScale)
        .tickSize(barHeight * 2)
        .tickValues(xTicks)
        .tickFormat(function (a){return Intl.DateTimeFormat('en-GB').format(a)})
        

    var g = svg_leg.append("g")
      .attr("transform", "translate(" + padding + ", 0)")
      .attr("class", "legend_box");

    var defs = svg_leg.append("defs");
    var linearGradient = defs.append("linearGradient").attr("id", "myGradient");
    linearGradient.selectAll("stop")
        .data(data)
      .enter().append("stop")
        .attr("offset", function(d){ 
            return (d.pos/data.length * 100) + "%"
          })
        .attr("stop-color", d => d.color);

    g.append("rect")
        .attr("width", innerWidth)
        .attr("height", barHeight)
        .style("fill", "url(#myGradient)");

    g.append("g")
        .call(xAxis)
      .select(".domain").remove();
  }

  function highlightNodesByDataInterval(datatype,valfrom,valto,el){
    if (datatype in el.data){
      var thisval=el.data[datatype]
      if ((thisval>= valfrom) && (thisval <= valto)){
        var myidval= el.data.id
        myid="#node_"+myidval.toString();
        svg.select(myid)
          .attr("r", 7)
      }

    }
    if (el.children){
      el.children.forEach(function(e){
        highlightNodesByDataInterval(datatype,valfrom,valto,e)
      })
    }
  }

  function highlightNodesByData(datatype,dataval,el){
    if (datatype in el.data){
      if (el.data[datatype]==dataval){
        var myidval= el.data.id
        myid="#node_"+myidval.toString();
        svg.select(myid)
          .attr("r", 7)
      }

    }
    if (el.children){
      el.children.forEach(function(e){
        highlightNodesByData(datatype,dataval,e)
      })
    }
  }

  function sort_str_or_number(data_keys){
    var any_not_number=false;
    for (var i=0;i<data_keys.length;i++){
      var e=data_keys[i]
      if (isNaN(e)){
        any_not_number=true;
        break;
      }
    }
    if (any_not_number){
      data_keys=data_keys.sort();
    } else {          
      data_keys.sort(function(a, b){return Number(a)-Number(b)});
    }
    return data_keys
  }

  function create_legend(colorvar){
    var mycolorscheme=colorschemes[colorvar];
    if (colorvar=="date"){
      var date_list=colorschemes["date_list"];
      gradient_legend(date_list)
      d3.select("#svg_leg").attr("width","220px")
        .attr("height","50px");

    } else {
      //Compute length
      //Generate legend
      if (colorvar=="age" || colorvar=="mutations"){
        max_len=100
        var new_colorscheme={};
        var new_data_keys=[];
        var last_color=false
        var last_date=false
        var date_pair_from=false
        for (dateval in mycolorscheme){
          color=mycolorscheme[dateval]
          if (! date_pair_from){
            date_pair_from=dateval;
          } else {
            if (color != last_color){
              date_pair_fromto=date_pair_from+ " - "+last_date;
              new_colorscheme[date_pair_fromto]=last_color;
              new_data_keys[new_data_keys.length]=date_pair_fromto;
              date_pair_from=dateval;
            }
          }
          last_color=color
          last_date=dateval
        }
        date_pair_fromto=date_pair_from+ " - "+last_date;
        new_colorscheme[date_pair_fromto]=last_color;
        new_data_keys[new_data_keys.length]=date_pair_fromto;
        
        mycolorscheme=new_colorscheme;
        data_keys=new_data_keys
      } else {

        var data_keys=[]
        for (c in mycolorscheme){
          data_keys[data_keys.length]=c
        }
        data_keys=sort_str_or_number(data_keys)

      }
      var max_len=0
      for (key in mycolorscheme){
        if (key.length > max_len){
          max_len=key.length
        }
      }
      d3.select("#svg_leg").attr("width",(30+(max_len)*7)+"px")
      var height=(data_keys.length * 20);
      svg_leg_el = d3.select("#svg_leg")
          .attr("height", height);

      var legendHolder = svg_leg.append('g')
        // translate the holder to the right side of the graph
        .attr('transform', "translate(" + (0) + ",0)")
        .attr("class", "legend_box")
   
      var legend = legendHolder.selectAll(".legend_el")
        .data(data_keys)
        .enter().append("g")
          .attr("class", "legend_el")
          .style("cursor","pointer")
          .attr("data-datatype",colorvar)
          .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; })
          .on("mouseover",function(d){
            var datatype= this.dataset.datatype;
            var dataval= this.__data__;
            if (datatype=="age"|| colorvar=="mutations"){
              datavalsp=dataval.split(" - ")
              highlightNodesByDataInterval(datatype,Number(datavalsp[0]),Number(datavalsp[ 1]),root)
            } else {
              highlightNodesByData(datatype,dataval,root)
            }
            displaypopup_legend(d,true);
          })
          .on("mouseout",function(d){
            svg.selectAll(".node_circle")
            .attr("r", function(d){
              if (d.data.is_terminal){
                return 5
              } else {
                return 0
              }
            })
            displaypopup_legend(d,false);
          });
      legend.append("circle")
        .attr("r", 5)
        .attr("cy", 10)
        .style("fill", function(d){
          return mycolorscheme[d]});

      legend.append("text")
        .attr("x", 10)
        .attr("y", 9)
        .attr("dy", ".35em")
          .attr("text-anchor", "left")
          .style("alignment-baseline", "middle")
                  .text(function(d) { return d; });

    }

  }



    function linkMouseOut(d){
      d3.selectAll("path")
        .attr("stroke-width", "1px");
      $("body").css("cursor","auto");
    }

//    function setwidth_children(el){
//      if (el.nextElementSibling != null){
//        e=el.nextElementSibling;
//        d3.select(e)
//          .attr("stroke-width", "4px");
//        setwidth_children(e)
//
//      }
//    }
    function setwidth_children(d){
      myid=d.data.id;
      myid="#path_"+myid.toString();
      svg.select(myid)
        .attr("stroke-width", "4px");

      if (d.children){
        d.children.forEach(function(e){
          setwidth_children(e)
        })        
      }
    }

    function linkMouseOver(d){
      if (d.children){

        //setwidth_children(this);
        setwidth_children(d);
        $("body").css("cursor","pointer");
      }
    }

    function obtainb_subtree(el,myid,mysubtree){
        if (el["id"]==myid){
          mysubtree= el
        }
        else{
          el.children.forEach(function(e) {
            mysubtree=obtainb_subtree(e,myid,mysubtree)
          });
        }
        return mysubtree
    }

    function showsubtree(d){
      if (d.children){
        svg.selectAll("*").remove();
        mysubtree=obtainb_subtree(data,d.data.id,false)
        create_tree(mysubtree)
        $("#showWholeTree").css("display","inline")
      }
    }

    $("#showWholeTree").on("click",function(){
        svg.selectAll("*").remove();
        create_tree(data)
        $("#showWholeTree").css("display","none")
    })

    function sort_by_variant_pos(a,b){
        aN=Number(a.slice(1,a.length-1))
        bN=Number(b.slice(1,b.length-1))
        return aN - bN
    }

    function displayFixedNodeData(d){
        var data_html=""


        var y_val=0;
        var y_sep=25;
        var info_to_add=["name", "gisaid_epi_isl", "genbank_accession", "date", "host", "age","sex", "region", "country","admin_division", "location", "region_of_exposure","country_of_exposure", "division_of_exposure","clade", "gisaid_clade", "pango_lineage","emerging_lineage","logistic_growth","author","originating_lab", "submitting_lab","s1_mutations"];
        for (i=0;i<info_to_add.length;i++){
          var info_var=info_to_add[i];
          info_var_name=info_var.replace(/_/g," ");
          info_var_name=info_var_name.substr(0,1).toUpperCase()+info_var_name.substr(1);
          var info_var_data=d.data[info_var];
          var include_url=false;
          if (d.data[info_var]){
            if ((info_var=="author") && (info_var_data.indexOf("(http") >-1)){
              var startind=info_var_data.indexOf("(");
              var endind=info_var_data.lastIndexOf(")");
              if ((startind>-1) && (endind>-1)){
                include_url=info_var_data.slice(startind+1,endind)
                info_var_data=info_var_data.slice(0,startind)
              }

            }
            if (info_var=="genbank_accession"){
              include_url="https://www.ncbi.nlm.nih.gov/nuccore/"+info_var_data;
            }
            if (include_url){
              data_html+='<tr>\
                <td style="font-weight:strong;">'+info_var_name+'</td>\
                <td><a href="'+include_url+'" target="_blank">'+info_var_data+'</a></td>\
              </tr>'
          
            } else {
              data_html+='<tr>\
                <td style="font-weight:bold">'+info_var_name+'</td>\
                <td>'+info_var_data+'</td>\
              </tr>'
            }

          }

        }
        //Mutated proteins table
        var mutations_html_sect=""
        var coln="12";
        var isolateid=d.data["gisaid_epi_isl"];
        var genome_mut_prot={}
        if ("mutation_data" in d.data){
          genome_mut_prot=d.data["mutation_data"];
          var mutations_html=""
          for (protName in genome_mut_prot){
            var mutli=genome_mut_prot[protName];
            var mutli_s=mutli.sort(sort_by_variant_pos).join(", ");
            var mut_prot_avail=false;
            var simulation_avail=false;
            if (simulated_prots.indexOf(protName)> -1){
              simulation_avail=true;
            }
            var extrainfo_btn_html="";
            if (simulation_avail){
              extrainfo_btn_html="<span class='glyphicon glyphicon-plus-sign more_info_mutated_prot' style='padding-left:10px;font-size:12px' data-prot='"+protName+"' data-isolateid='"+isolateid+"'></span>\
                                  <span class='pannel_mutated_prot'></span>";
            }
            mutations_html+="<div class='additional_info_muts'>\
                              <p style='font-weight:bold'>\
                                    "+protName+"\
                                    "+extrainfo_btn_html+"\
                              </p>\
                            <p>"+mutli_s+"</p></div>"
          }
          mutations_html_sect='<div class="col-md-6" id="popup_mutated_prots">\
                                    <h3>Variant proteins</h3>\
                                    '+mutations_html+'\
                                  </div>';
          coln="6";
        }
        var final_html='<div id="popup_click">\
                          <span id="close_popup">x</span>\
                          <div class="col-md-'+coln+'">\
                            <h3>Genome details</h3>\
                            <table class="table table-condensed">\
                              '+data_html+'\
                            </table>\
                          </div>\
                          '+mutations_html_sect+'\
                        </div>';
        $("#additional_info_cont").html(final_html)

        //remove when clicked out
        $(document).on("mouseup.hideDocClick",function(e) {
            var container = $("#popup_click");
            // if the target of the click isn't the container nor a descendant of the container
            var close_btn= $("#close_popup");
            if ((!container.is(e.target) && container.has(e.target).length === 0) || close_btn.is(e.target)) {
                $("#popup_click").remove();
                $(document).off('.hideDocClick');
            }
        });
    }

    $("#additional_info_cont").on("click",".more_info_mutated_prot", function(){
      var clickedplus=$(this);
      var isolateid=clickedplus.data("isolateid")
      var myprot=clickedplus.data("prot")
      if (clickedplus.hasClass("open")){
        var activation=false;
        clickedplus.removeClass("open");
      } else {
        var activation=true;
        $("#additional_info_cont").find(".pannel_mutated_prot.open").html("");
        clickedplus.addClass("open");
      }
      display_mut_prot_popup(clickedplus,myprot,isolateid,activation)
    });

    function display_mut_prot_popup(clickedplus,myprot,isolateid,activation){
      $("#additional_info_cont").find(".pannel_mutated_prot").html("");
      if (activation){
        var mutprot_selector=clickedplus.parent("p")
        var pannel_sect=mutprot_selector.find(".pannel_mutated_prot")
        var parentpopup_offset=$("#popup_mutated_prots").offset();
        var clickedplus_offset=clickedplus.offset();
        var mytop=clickedplus_offset["top"] - parentpopup_offset["top"];
        var myleft=(clickedplus_offset["left"] - parentpopup_offset["left"])+30 ;

        var btn_open_wb_html="";
        if (simulated_prots.indexOf(myprot)> -1){
          prot_link="/covid19/prot/"+myprot+"/"+isolateid;
          btn_open_wb_html="<p><a href='"+prot_link+"' class='btn btn-default btn-xs' role='button'>See simulations</a></p>";
        } 
        var btn_download_fasta="<p><a href='/covid19/dwl/fasta/"+isolateid+"/"+myprot+"' class='btn btn-default btn-xs' role='button' >Download fasta</a></p>";

        var btn_download_structure="";
        var include_btn_download_structure=false;// [!] to do
        if (include_btn_download_structure){
          btn_download_structure="<p><button type='button' class='btn btn-default btn-xs disabled'>Download variant protein</button></p>";
        }
        ////[!]
        btn_download_fasta="";
        if (btn_open_wb_html){
          pannel_html="<div class='pannel_mutated_prot_popup' style='position:absolute;top:"+mytop+"px;left:"+myleft+"px;'>\
                              "+btn_open_wb_html+"\
                              "+btn_download_fasta+"\
                              "+btn_download_structure+"\
                          </div>";

          pannel_sect.html(pannel_html)

        }
      }
    }


    function displaypopup_legend(d,appear){
      if (appear){
        var legend_html="<div style='top:"+(mouseY+10)+"px;left:"+(mouseX+50)+"px'>"+d+"</div>";
        $("#legend_popup").html(legend_html)
      } else {
        $("#legend_popup").html("")
      }
    }

    function displaypopup(d,appear){
      if (appear){
        var mypopup_hover = svg.append("g")
            .attr("transform",function(){
              return "translate(" + (d.y+20) + "," + (d.x - 50) + ")"
            })
          .attr("id","popup_hover")
          .attr("text-anchor", "start");
        mypopup_hover.append("rect")
          .attr("rx", "5")
          .attr("ry", "5")
          .attr("fill", "white")
          .attr("opacity", 0.9)
          .attr("x", "-10")
          .attr("y", "-20")
        var y_val=0;
        var y_sep=25;
        if (d.data.name){
          mypopup_hover.append("text")
            .attr("y", y_sep*y_val)
            .attr("font-weight", 600)
            .text("Name: ")
            .append("tspan")
            .attr("font-weight", 300)
            .text(d.data.name);          
            y_val+=1;
        }
        if (d.data.date){
          mypopup_hover.append("text")
            .attr("y", y_sep*y_val)
            .attr("font-weight", 600)
            .text("Date: ")
            .append("tspan")
            .attr("font-weight", 300)
            .text(d.data.date);          
            y_val+=1;
        }
        if (d.data.author){
          mypopup_hover.append("text")
            .attr("y", y_sep*y_val)
            .attr("font-weight", 600)
            .text("Author: ")
            .append("tspan")
            .attr("font-weight", 300)
            .text(function(){
              var authorname=d.data.author;
              if (authorname.indexOf("(")> -1) {
                var myind=authorname.indexOf("(");
                authorname=authorname.slice(0,myind)
              }
              return authorname
            });
            y_val+=1;
        }
        if (d.data.gisaid_epi_isl){
          mypopup_hover.append("text")
            .attr("y", y_sep*y_val)
            .attr("font-weight", 600)
            .text("GISAID EPI ISL: ")
            .append("tspan")
            .attr("font-weight", 300)
            .text(d.data.gisaid_epi_isl);          
            y_val+=1;
        }
        if (d.data.genbank_accession){
          mypopup_hover
            .append("a").attr("xlink:href", "www.ncbi.nlm.nih.gov/nuccore/" + d.data.genbank_accession )
              .append("text")
              .attr("y", y_sep*y_val)
              .attr("font-weight", 600)
              .text("Genbank accession: ")
              .append("tspan")
              .attr("font-weight", 300)
              .text(d.data.genbank_accession);     
              y_val+=1;
        }


        //Mutated proteins table
        var mut_n=d.data.mutations;
        mypopup_hover.append("text")
          .attr("y", y_sep*y_val)
          .attr("font-weight", 600)
          .text("Mutations: ")
          .append("tspan")
          .attr("font-weight", 300)
          .text(mut_n);          
          y_val+=1;

        //Set size
        var popup_size = document.getElementById("popup_hover").getBBox();
        var whole_popup_width=popup_size.width +40;
        var whole_popup_height=popup_size.height +15;
        mypopup_hover.select("rect")
            .attr("width",(whole_popup_width) + "px")
            .attr("height",(whole_popup_height) + "px")

      } else {
        svg.select("#popup_hover").remove();
      }

    }

    function obtain_time_limits(n,min_pos,max_pos,min_date,max_date){
      if (n.data && n.data.length != null && n.data.is_terminal){
        var thispos=n.y;
        if (min_pos===false || thispos<min_pos){
          min_pos=thispos;
        }
        if (max_pos===false || thispos>max_pos){
          max_pos=thispos;
        }
        var strdate=n.data.date;
        dateobj=datestr_to_obj(strdate)
        if (min_date){
          if (min_date<dateobj){
            min_date=dateobj;
          }
          if (max_date>dateobj){
            max_date=dateobj
          }
        } else {
          min_date=dateobj;
          max_date=dateobj;
        }
      }
      if (n.children)
        n.children.forEach(function(n) {
          limit_res=obtain_time_limits(n,min_pos,max_pos,min_date,max_date);
          min_pos=limit_res[0];
          max_pos=limit_res[1];
          min_date=limit_res[2];
          max_date=limit_res[3];
        });
      return [min_pos,max_pos,min_date,max_date]
    }

    function assign_x_val(n,offset){
      n.x =offset+ n.x/1.2;
      if (n.children)
        n.children.forEach(function(n) {
          assign_x_val(n,offset);
        });
    }


    function assign_y_val(n, offset,) {
      //var correction=1750
      var correction=1000
      if (n.data && n.data.length != null)
        offset += n.data.length * correction;
      n.y = offset;
      if (n.children)
        n.children.forEach(function(n) {
          assign_y_val(n, offset);
        });
    }


    function obtain_tree_data(){
      $.ajax({
          type: "POST",
          url: "/covid19/home/", 
          dataType: "json",
        //  data: { "a":"A"},
          success: function(out_data) {
              $("#loading").css({"display":"none"})
              $(".hiddenwhenload").css({"display":"inline"})
              data=out_data.tree_data;
              simulated_prots=out_data.simulated_prots;
              create_tree(data)
          },
          error: function() {
              console.log(":(")
          },
          timeout: 600000
      });
    }

    // set the dimensions and margins of the graph
    var width = 1500
    var height = 800


    // read json data
    colorschemes=$("#chart").data("colors_dict")

    var svg_leg = d3.select("#legend_cont")
      .append("svg")
        .attr("height", 0)
        .attr("id", "svg_leg")
      .append("g")
        .attr("transform", "translate(20,0)");  // bit of margin on the left = 40

    // append the svg object to the body of the page
    var svg = d3.select("#chart")
      .append("svg")
        .attr("width", width)
        .attr("height", height)
      .append("g")
        .attr("transform", "translate(20,0)");  // bit of margin on the left = 40



    data=$("#chart").data("tree_data")
    simulated_prots=$("#chart").data("simulated_prots");
    obtain_tree_data()


  function LightenDarkenColor(col, amt) {    
      var usePound = false;
      if (col[0] == "#") {
          col = col.slice(1);
          usePound = true;
      }
      var num = parseInt(col,16);
      var r = (num >> 16) + amt;
      if (r > 255) r = 255;
      else if  (r < 0) r = 0;
   
      var b = ((num >> 8) & 0x00FF) + amt;
   
      if (b > 255) b = 255;
      else if  (b < 0) b = 0;
   
      var g = (num & 0x0000FF) + amt;
   
      if (g > 255) g = 255;
      else if (g < 0) g = 0;
   
      return (usePound?"#":"") + (g | (b << 8) | (r << 16)).toString(16);
    
  }


    function getDaysBetweenDates(start, end) {
        for(var arr=[],dt=new Date(start); dt<=end; dt.setDate(dt.getDate()+1)){
            arr.push(new Date(dt));
        }
        return arr;
    };


    function add_timeline(minval_h,maxval_h,min_date,max_date,timeline_y_base){
      var timeline_color='#b3b3b3';
      //var timeline_y_base=20;
      //Horizontal line
      var h_diff=maxval_h-minval_h;
      svg.append("g")
          .append('rect') 
          .attr("id","timeline_h")
            .attr('x',  minval_h)
            .attr('y',  timeline_y_base)
            .attr("width",h_diff)
            .attr("height","1px")
            .attr("fill","none") 
            .attr("stroke",timeline_color) 
            .attr("stroke-width","1px");
            //.attr("opacity","0.5")
      //Vertical lines
      var days_between=getDaysBetweenDates(max_date,min_date)
      var dist_per_day=h_diff/days_between.length;
      for (var t = 0; t<days_between.length;t++){
        var mydat=days_between[t];
        if (mydat.getDate()==1){
          //Vertical line position
          var linepos_h=((t+1)*dist_per_day)+minval_h;
          //Date format
          var ye = new Intl.DateTimeFormat('en', { year: 'numeric' }).format(mydat);
          var mo = new Intl.DateTimeFormat('en', { month: 'short' }).format(mydat);
          var date_str=`${mo} ${ye}`;
          //draw vertical line
          svg.append('line') 
            .attr('style', "stroke:"+timeline_color+"; stroke-width:1;")
            .attr('x1', linepos_h)
            .attr('y1', timeline_y_base)
            .attr('x2', linepos_h)
            .attr('y2', timeline_y_base+10)
          svg.append("text")
            .attr("x", linepos_h-25)
            .attr("y", timeline_y_base+20)
            .attr("dy", ".35em")
            .style('fill', timeline_color)
            .text(date_str);

        }
      }
    }


    function create_tree(data){
      // Create the cluster layout:
      var cluster = d3.tree()
        .size([height, width ]);  // 100 is the margin I will have on the right side
      root = d3.hierarchy(data, function(d) {
          return d.children;
      });
      cluster(root);
      assign_y_val(root,0)
      assign_x_val(root,70)
      // Give the data to this cluster layout:

      // Add the links between nodes:
      svg.selectAll('path')
        .data( root.descendants().slice(1) )
        .enter()
        .append('path')
        .attr("d", function(d) {
            return "M" + d.y + "," + d.x
                 + "H" + d.parent.y + "V" + d.parent.x;        
  //          return "M" + d.y + "," + d.x
  //                  + "C" + (d.parent.y + 50) + "," + d.x
                    //+ " " + (d.parent.y + 150) + "," + d.parent.x // 50 and 150 are coordinates of inflexion, play with it to change links shape
  //                  + " " + d.parent.y + "," + d.parent.x;
                  })
        .style("fill", 'none')
        .attr("stroke", '#ccc')
        .attr("id", function(d){
          return "path_"+d.data.id
        })
        .on("mouseover", linkMouseOver)
        .on("mouseout", linkMouseOut)
        .on("click", showsubtree);
      // Add a circle for each node.
      var mynode=svg.selectAll("g")
          //.data(root.descendants())
          .data(root.descendants().filter(function(d){ return d.data.name; }))
          .enter()
          .append("g")
          .attr("transform", function(d) {
              return "translate(" + d.y + "," + d.x + ")"
          });
      var sel_classified=get_phyl_filters()
      mynode.append("circle")
            .attr("class","node_circle")
            .attr("id", function(d){
              return "node_"+d.data.id
            })
            .attr("r", function(d){
              if (d.data.is_terminal){
                return 5
              } else {
                return 0
              }
            })
            .style("fill", function(d){
              var colorvar=$("#colorby").val();
              if (d.data[colorvar]){
                myval=d.data[colorvar]
                return colorschemes[colorvar][myval]
              } else {
                return "#ffffff"
              }
            })
            .style("display", function(d){
              return display_if_in_dict(d,sel_classified)
            })
            .attr("stroke", function(d){
              var colorvar=$("#colorby").val();
              if (d.data[colorvar]){
                myval=d.data[colorvar]
                return LightenDarkenColor(colorschemes[colorvar][myval],-40)
              } else {
                return "#999999"
              }
            })
            .style("stroke-width", 1)
            .on("mouseover", function(d){
              displaypopup(d,true)
            })
            .on("mouseout", function(d){
              displaypopup(d,false)
            })
            .on("click", function(d){
              if (d.data.is_terminal){
                displayFixedNodeData(d)
              }
            });
      //mynode.append("text")
      //      .text(function(d){return d.data.genbank_accession});
      limit_res=obtain_time_limits(root,false,false,false,false)
      var minval_h=limit_res[0];
      var maxval_h=limit_res[1];
      var min_date=limit_res[2];
      var max_date=limit_res[3];
      add_timeline(minval_h,maxval_h,min_date,max_date,20);
      add_timeline(minval_h,maxval_h,min_date,max_date,height-40);

      // legend
      var colorvar=$("#colorby").val();
      create_legend(colorvar)


  $('.selectpicker').selectpicker();
  $(".selectpicker_clear").click(function(){
      var myselector=$(this).data("target");
      //$($(this).data("target")).selectpicker('deselectAll');

      $(myselector).selectpicker('val', '');
      $(myselector).selectpicker('refresh');

      svg.selectAll(".node_circle")
        .style("display", "inline")
  })

  function get_range(start,end){    
      var step=1;
      var range=[];
      while ( end > start ) {
          range.push(start);
          start += step;
      }
      return range
  }

  function range_srt_to_li(range_str){
    var sp_res=range_str.split(" - ");
    var start=Number(sp_res[0]);
    var end=Number(sp_res[1]);
    return get_range(start,end+1)
  }

  function get_phyl_filters(){
    var sel_classified={};
    var sp_sel=$("#phyltree_filter").val();
    if (sp_sel){
      for (var sn=0;sn<sp_sel.length;sn++){
        var sel_opt=sp_sel[sn];
        var sel_opt_sp=sel_opt.split("__");
        var opt_group=sel_opt_sp[0];
        var opt_val=sel_opt_sp[1];
        if (! (opt_group in sel_classified)){
          sel_classified[opt_group]=[];
        }
        var groupli=sel_classified[opt_group];
        if (opt_group == "age" || opt_group == "mutations"){
          opt_val_li=range_srt_to_li(opt_val);
          for (var oi=0;oi<opt_val_li.length;oi++){
            groupli[groupli.length]=opt_val_li[oi];
          }
        } else {
          groupli[groupli.length]=opt_val;

        }
      }
    }
    return sel_classified

  }

  function display_if_in_dict(d,sel_classified){
      var display_this=true;
      for (phyl_param in sel_classified){
        if (phyl_param in d.data){
          var phyl_vals=sel_classified[phyl_param];
          var myval=d.data[phyl_param];
          if (phyl_vals.indexOf(myval)==-1){
            display_this=false;
          }
        } else {
          display_this=false;
        }
      }
      if (display_this){
        return "inline"
      } else {
        return "none"
      }
  }

  function filter_treenodes(sel_classified){
    svg.selectAll(".node_circle")
      .style("display", function(d){
        return display_if_in_dict(d,sel_classified)
      })
  }

  $("#phyltree_filter").on("change",function(){
    var sel_classified=get_phyl_filters()
    filter_treenodes(sel_classified)
  })

  //---------------------------

    $("#colorby").change(function(){
        var colorvar=$(this).val();
        if (colorvar in colorschemes){
          var myschemedict=colorschemes[colorvar];
          svg.selectAll(".node_circle")
            .style("fill", function(d){
              var myval=d.data[colorvar]
              if (myval in myschemedict){
                return myschemedict[myval]
              } else {
                return "#ffffff"
              }
            })
            .attr("stroke", function(d){
              var myval=d.data[colorvar]
              if (myval in myschemedict){
                return LightenDarkenColor(myschemedict[myval],-40)
              } else {
                return "#999999"
              }
            })  
        }
        svg_leg.selectAll("*").remove();
        
        create_legend(colorvar)
    });

  }


  function trigger_hide_display(trigger_sel,icon_sel,gi_open,gi_closed){
      $(trigger_sel).click(function(){
          var target=$(this).attr("data-target");
          var displaycss=$(target).css("display");
          var icon=$(this).children(icon_sel);
          if (displaycss=="none"){
            icon.removeClass(gi_closed)
            icon.addClass(gi_open)
            $(target).css("display","block");
          } else {
            icon.removeClass(gi_open)
            icon.addClass(gi_closed)
            $(target).css("display","none");
          }

      });
  }
  trigger_hide_display(".trigger_collapse",".glyphicon","glyphicon-minus-sign","glyphicon-plus-sign")


$(function(){
    $(".scrolltop_wrapper1").scroll(function(){
        $(".scrolltop_wrapper2")
            .scrollLeft($(".scrolltop_wrapper1").scrollLeft());
    });
    $(".scrolltop_wrapper2").scroll(function(){
        $(".scrolltop_wrapper1")
            .scrollLeft($(".scrolltop_wrapper2").scrollLeft());
    });
});

})
