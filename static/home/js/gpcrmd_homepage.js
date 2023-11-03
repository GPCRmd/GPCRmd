
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
          var datainfo=[['Date', 'Trajectories',{ role: 'annotation' }, "GPCRmd simulations", { role: 'annotation' }]];
          var data_all = datainfo.concat(data_pre);
          var data = google.visualization.arrayToDataTable(data_all);

          var options = {
            hAxis: {title: 'Date',slantedTextAngle:90},
            vAxis: {title: "", minValue: 0, maxvalue: 55 , gridlines: {count: 0, color:"#bfbfbf"}},
            legend: {position:"top"},
            annotations: {stem:{length:2}},
            colors: ['#423F3E', '#BF3C1F'],
            chartArea:{width:390}

          };

          var chart = new google.visualization.AreaChart(document.getElementById('stats_subm'));
          
          chart.draw(data, options);
      }
  google.load("visualization", "1", {packages:["corechart"],'callback': drawCharts_subm});

  function drawCharts_time() {
        
      var data_pre=$("#stats_time").data("time_data");
      var data = new google.visualization.DataTable();
      data.addColumn('string', 'Date');
      data.addColumn('number', 'Total');
      data.addColumn({type: 'string', role: 'annotation'});
      data.addColumn('number', 'GPCRmd community');
      data.addColumn({type: 'string', role: 'annotation'});
      data.addColumn('number', 'Individual');
      data.addColumn({type: 'string', role: 'annotation'});

      for (v = 0; v < data_pre.length; v++) {
        data.addRows([
          [data_pre[v][0], data_pre[v][1]+data_pre[v][3], ((data_pre[v][1]+data_pre[v][3]).toFixed(2)).toString(), data_pre[v][1], data_pre[v][2],
                                  data_pre[v][3], data_pre[v][4]],
        ]);
      }

        var options = {
          hAxis: {title: 'Date',slantedTextAngle:90},
          vAxis: {title: "Accumulated time (microseconds)", minValue: 0, maxvalue: 55 , gridlines: {count: 0, color:"#bfbfbf"}},
          legend: {position:"top"},
          annotations: {stem:{length:2}},
          colors: ['#7393B3', '#BF3C1F','#423F3E'],
          chartArea:{
            width:400,
            height: 250
          },
          width: 650,
          height: 350,

        };

        var chart = new google.visualization.AreaChart(document.getElementById('stats_time'));
        
        chart.draw(data, options);
    }
  google.load("visualization", "1", {packages:["corechart"],'callback': drawCharts_time});

  // function drawCharts_time() {
      
  //     var data_pre=$("#stats_time").data("time_data");
  //     // var datainfo=[['Date', 'GPCRmd community',{ role: 'annotation' }, "Individual", { role: 'annotation' }]];
  //     // var data_all = datainfo.concat(data_pre);
  //     // var data = google.visualization.arrayToDataTable(data_all);
  //     var data = new google.visualization.DataTable();
  //     data.addColumn('date', 'Date');
  //     data.addColumn('number', 'Total (ns)');
  //     data.addColumn('number', 'GPCRmd community (ns)');
  //     // data.addColumn('string', 'GPCRmd community date');
  //     data.addColumn('string', 'GPCRmd community time');
  //     data.addColumn('number', 'Individual (ns)');
  //     // data.addColumn('string', 'Individual date');
  //     data.addColumn('string', 'Individual time');

  //     for (v = 0; v < data_pre.length; v++) {
  //       // var stringArray = data_pre[v][0].split("/");
  //       // var year = stringArray[2];
  //       // var month = stringArray[0];
  //       data.addRows([
  //         [new Date(Number(data_pre[v][0]), 12), data_pre[v][1]+data_pre[v][3],data_pre[v][1], data_pre[v][2],
  //                                 data_pre[v][3], data_pre[v][4]],
  //       ]);
  //     }

  //     var chart = new google.visualization.AnnotationChart(document.getElementById('stats_time'));

  //     var options = {
  //       displayAnnotations: false,
  //       displayAnnotationsFilter:false,
  //       displayRangeSelector: false,
  //       displayDateBarSeparator: true,
  //       displayZoomButtons: false,
  //       dateFormat: "yyyy",
  //       chartArea:{
  //         width:300,
  //       },
  //       width: 650,
  //       height: 325,
  //       colors: ['#7393B3', '#BF3C1F','#423F3E'],
  //       thickness: 5,
  //       fill: 50,
  //       annotations: {stem:{length:2}},
  //     };
      
  //     chart.draw(data, options);
  // }
  // // google.load("visualization", "1", {packages:["annotationchart"],'callback': drawCharts_time});
  // google.charts.load('current', {'packages':['annotationchart'],'callback': drawCharts_time});

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
          chartArea:{width:600, height:300 },
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
          legend: 'labeled',
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
          chartArea:{width:600, height:300 },
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
          legend: 'labeled',
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
          chartArea:{width:600, height:300 },
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
          legend: 'labeled',
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
      // This part refresh the graphs, due to hide the tabs, google chart can not draw correctly some elements for this reason
      // we display the two firsts graphs (active class) and then "refresh" the carousel activating the arrows to display the first
      // position again. 
  document.getElementsByClassName("left carousel-control")[0].click();
  setTimeout(function(){ // need to wait 1 second to click the other arrow again
      document.getElementsByClassName("right carousel-control")[0].click();
  }, 1500);

})


