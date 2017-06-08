// hightlight links
// highlight tracks



var clustering = 'LigandPocket: "2.2x51 2.2x53 2.2x56 2.2x57 2.2x60 2.2x61 2.2x63 2.2x64 2.2x65 3.3x28 3.3x29 3.3x32 3.3x33 3.3x36 3.3x37 3.3x40 4.4x56 4.4x57 4.4x59 4.4x60 4.4x61 5.5x38 5.5x39 5.5x42 5.5x43 5.5x44 5.5x45 5.5x46 5.5x461 5.5x47 6.6x44 6.6x45 6.6x48 6.6x51 6.6x52 6.6x54 6.6x55 6.6x58 6.6x59 7.7x30 7.7x31 7.7x32 7.7x33 7.7x34 7.7x35 7.7x36 7.7x37 7.7x38 7.7x39 7.7x40 7.7x41 7.7x42 7.7x43 7.7x44" GproteinPocket: "3.3x50 3.3x53 3.3x54 3.3x55 5.5x61 5.5x64 6.6x33 6.6x36 6.6x37"'
//5x58 -> 7x53 disappears

var w = 800,
    h   = 800,
    rx  = w / 2,
    ry  = h / 2,
    m0,
    rotate = 0;

//var stdEdgeColor = "#1f77b4";
var stdEdgeColor = "rgba(0,0,0,200)";
var stdEdgeWidth = 2;

var svg, div, buttons, bundle, line, nodes, splines, links, graph;
var summaryMode = false;

var originalCluster = true;
var originalKeys;
var toggledNodes = {};
var originalText;

var sortOnNodeValue = false;
var trackWidth = 10;
var trackMode = false;


var clusterSortEnabled = false, wholeChartSortEnabled = false;


var splinesMap = {};

var newSplinesMap = {};


// create a table with column headers, types, and data
function create_bundle(rawText) {
    originalText = rawText;
    var cluster = d3.layout.cluster()
        .size([360, ry - 120])
        .sort(function(a, b) {
            if (sortOnNodeValue) {
                return d3.ascending(a.someValue, b.someValue);
            }

            var aRes = a.key.match(/[0-9]*$/);
            var bRes = b.key.match(/[0-9]*$/);
            if(aRes.length==0 || bRes.length==0){
                aRes = a.key;
                bRes = b.key;
            }else{
                aRes = parseInt(aRes[0]);
                bRes = parseInt(bRes[0]);
            }

            if (!originalCluster) {
                // we need to take the key into account
                var aCluster = a.key.match(/^[0-9]*/);
                var bCluster = b.key.match(/^[0-9]*/);
                aCluster = parseInt(aCluster[0]);
                bCluster = parseInt(bCluster[0]);
                return d3.ascending(aCluster * 1000 + aRes, bCluster * 1000 + bRes);
            }

            return d3.ascending(aRes, bRes);
        });

    bundle = d3.layout.bundle();

    line = d3.svg.line.radial()
        .interpolate("bundle")
        .tension(.85)
        .radius(function(d) { return d.y; })
        .angle(function(d) { return d.x / 180 * Math.PI; });

    d3.select("#evobundlediv").style("position","relative");

    // Chrome 15 bug: <http://code.google.com/p/chromium/issues/detail?id=98951>
    div = d3.select("#evobundlediv").insert("div")
        .style("width", w + "px")
        .style("height", w + "px")
        .style("-webkit-backface-visibility", "hidden");

    svg = div.append("svg:svg")
        .attr("width", w)
        .attr("height", h)
        .append("svg:g")
        .attr("transform", "translate(" + rx + "," + ry + ")");

    svg.append("svg:path")
        .attr("class", "arc")
        .attr("d", d3.svg.arc().outerRadius(ry - 120).innerRadius(0).startAngle(0).endAngle(2 * Math.PI))

    d3.select(".switchButton").on("click", function() {
        transitionToCluster();
    });

    d3.select(".summaryButton").on("click", function() {
        transitionToSummary();
    });

    d3.select(".sortButton").on("click", function() {
        changeSortingOrder();
    });
    d3.select(".sortWithoutButton").on("click", function() {
        changeAbsoluteSortingOrder();
    });
    d3.select(".trackButton").on("click", function(){
        changeTrack();
    });


    //d3.json("interactionTimeline.json", function(classes) {
    //    console.log(classes);
    //  var nodes = cluster.nodes(genRoot(classes)),
    //      links = genLinks(classes),
    //      splines = bundle(links[0]);
    //  console.log("Links:");
    //  console.log(links[0]);

    //var classes = d3.csv.parseRows(rawText)
    //  .map(function(d){return {rawArr:d}; });
    var json = JSON.parse(rawText);
    graph = parse(json);
    originalKeys = graph.nodes.map(function(n){
        return n.name;
    });


    /** This part computes the small out bar **/

    var valueAssigned = [];
    graph.nodes.forEach(function(n){
        if (!n.children) {
            // assign a random value to the node for the
            n.someValue = Math.random()*90;
            valueAssigned.push(n.someValue);
        }
    });

    var extent = d3.extent(valueAssigned);
    var pieBarScale = d3.scale.linear().domain(extent).range([0,20]);

    var clusterDefinition = parseCluster(clustering);
    if(json.defaults && json.defaults.color) stdEdgeColor = json.defaults.color;
    if(json.defaults && json.defaults.width) stdEdgeWidth = json.defaults.width;
    nodes = cluster.nodes(graph.treeRoot);
    links = graph.frames;
    splines = bundle(links[0]);

    // not efficient, there must be a better way
    splinesMap = {}
    links[0].forEach(function(link, index){
       splinesMap[link.name1 + '-' + link.name2] = index;
    });

    var path = svg.selectAll("path.link")
        .data(links[0], function(d,i){
            var key = "source-" + d.source.key + "target-" + d.target.key;
            return key;
        })
        .enter().append("svg:path")
        .attr("class", function(d) {
            var ret = "link source-" + d.source.key + " target-" + d.target.key;
            var clusterSource = "cluster-" + d.source.parent.key;

            if (d.source.parent.key != d.target.parent.key) {
                var clusterTarget = "cluster-" + d.target.parent.key;
                ret = ret + ' ' + clusterTarget;
            }
            ret = ret + ' ' + clusterSource;

            if( d.source.key in toggledNodes || d.target.key in toggledNodes)
                ret+=" toggled";
            return ret;
        })
        .style("stroke-width",function(d){ return d.width?d.width:stdEdgeWidth; })
        .style("stroke",function(d){ return ("color" in d)?d.color:stdEdgeColor; })
        .attr("d", function(d, i) { return line(splines[i]); });






    /********************************************/


    svg.selectAll("g.node")
        .data(nodes.filter(function(n) { return !n.children; }), function(d){ return d.key})
        .enter().append("svg:g")
        .attr("class", function(d){ return "node" + " cluster-"+ d.parent.key})
        .attr("id", function(d) { return "node-" + d.key; })
        .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; })
        .append("svg:text")
        .attr("dx", function(d) { return d.x < 180 ? 8 : -8; })
        .attr("dy", ".31em")
        .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
        .attr("transform", function(d) { return d.x < 180 ? null : "rotate(180)"; })
        .text(function(d) { return d.key; })
        .on("click", toggleNode)
        .on("mouseover", mouseoverNode)
        .on("mouseout", mouseoutNode);

    var arcWidth = 300.0/graph.nodes.length;
    var innerRadius = ry - 80;

    var arc = d3.svg.arc()
        .innerRadius(function() { return ry - 80})
        .outerRadius(function(d){
            if (trackMode) {
                return ry - 60 - pieBarScale(d.someValue);
            } else {
                return ry - 60 - trackWidth;
            }
        })
        .startAngle(-arcWidth*Math.PI/360)
        .endAngle(arcWidth*Math.PI/360);

    var clusters = graph.treeRoot.children; // cereals
    var arcCluster =  d3.svg.arc()
        .innerRadius(ry-40)
        .outerRadius(ry-20)
        .startAngle(function(d){
            return  d.children[0].x * Math.PI/180;
        })
        .endAngle(function(d){
            return  d.children[d.children.length-1].x * Math.PI/180;
        });

    svg.selectAll("g.nodeBar")
        .data(nodes.filter(function(n) { return !n.children; }), function(d){ return d.key})
        .enter().append("svg:g")
        .attr("class", function(d){ return "nodeBar" + " cluster-"+ d.parent.key})
        .attr("id", function(d) { return "nodeBar-" + d.key; })
        .append("path")
        .attr("transform", function(d) { return "rotate(" + (d.x )+ ")" ; })
        .style("fill", function(d){ return ("color" in d)?d.color:"white"; })
        .attr("d", arc)


    // some crazy stuff
    function clickcancel() {
        // we want to a distinguish single/double click
        // details http://bl.ocks.org/couchand/6394506
        var event = d3.dispatch('click', 'dblclick');
        function cc(selection) {
            var down, tolerance = 5, last, wait = null, args;
            // euclidean distance
            function dist(a, b) {
                return Math.sqrt(Math.pow(a[0] - b[0], 2), Math.pow(a[1] - b[1], 2));
            }
            selection.on('mousedown', function() {
                down = d3.mouse(document.body);
                last = +new Date();
                args = arguments;
                console.log('clicked');
            });
            selection.on('mouseup', function() {
                var self = this;
                if (dist(down, d3.mouse(document.body)) > tolerance) {
                    return;
                } else {
                    if (wait) {
                        window.clearTimeout(wait);
                        wait = null;
                        event.dblclick.apply(self, args);
                    } else {
                        wait = window.setTimeout((function() {
                            return function() {
                                event.click.apply(self, args);
                                wait = null;
                            };
                        })(), 200);
                    }
                }
            });
        };
        return d3.rebind(cc, event, 'on');
    }

    var cc = clickcancel();
    d3.selectAll('g.nodeBar > path').call(cc);
    cc.on("dblclick",function(d){
        var transform = d3.transform(d3.select('svg > g').attr('transform'));
        transform.scale = [1, 1];
        transform.translate = [400, 400];
        d3.select('svg > g')
            .transition(200)
            .attr('transform', transform);

    });
    cc.on("click", function(e) {
        console.log (this,e);
            var transform = d3.transform(d3.select('svg > g').attr('transform'));
            var transformNode = d3.transform(d3.select(this).attr('transform'));
            var rotate = - transformNode.rotate;
            var halfHeight = 400;
            var moveupTo = halfHeight * 1.6;
            transform.scale = [1.6, 1.6];
            transform.rotate = rotate;
            transform.translate = [400, 600];
            console.log(rotate, transform);
            d3.select('svg > g')
                .transition(200)
                .attr('transform', transform);
        });




    /* we dont display cluster bar right now
    var clusterBars = svg.selectAll("g.clusterBar")
        .data(clusters)
        .enter().append("svg:g")
        .attr("class", function(d) { return "clusterBar cluster-"+ d.key})
        .attr("id", function(d) { return "clusterBar-" + d.key; })
        .append("path")
        //.attr("transform", function(d) { return "rotate(" + (d.x )+ ")" ; })
        .style("fill", function(d){ return d.children[0].color ? d.children[0].color:"white"; })
        .style("stroke-width", "2px")
        .style("stroke", "black")
        .attr("d", arcCluster);

    clusterBars.on("click", function(d){
        var clusterKey = d.key;
        var selectClass = 'path.link:not(.cluster-' + clusterKey + ')';
        var linksToHide = svg.selectAll(selectClass);
        linksToHide.transition().duration(500).style("opacity", "0.1");

        selectClass =  'g:not(.cluster-' + clusterKey + ')';
        linksToHide = svg.selectAll(selectClass);
        linksToHide.transition().duration(500).style("opacity", "0.1");
        console.log('Should do something with', linksToHide);
    });*/


    // we assume we only have a clustering with one level !!




    d3.select("input[type=range]")
        .on("input", function() {
            line.tension(this.value / 100);
            var path = svg.selectAll("path.link"); // you need to reselect cause the data can have changed
            path.attr("d", function(d, i) { return line(splines[i]); });
        });


    d3.select("input[id=timeRange]")
        .attr("max", links.length-1)
        .on("input", function(){fireTickListeners(this.value);} );

    //Set up controls
    var ch = 35,
        cp = 2,
        cw = 3*ch+2*cp;

    var controls = d3.select("div#evocontrols")
        .select("#controls")
        .style("width",cw)
        .style("height",ch)
        .append("svg:svg")
        .attr("width", cw)
        .attr("height", ch);

    var controlData = [
        {xoffset:0, id:"reverse",   symbol:"<<", callback:reverse},
        {xoffset:1, id:"playpause", symbol:">", callback:playpause},
        {xoffset:2, id:"forward",   symbol:">>", callback:forward}
    ];

    //buttons = controls.selectAll("g")
    //    .data(controlData)
    //  .enter().append("g").append("circle")
    var buttons = controls.selectAll("g")
        .data(controlData)
        .enter().append("g");

    buttons
        .append("circle")
        .style("fill",  "white")
        .style("stroke","gray")
        .style("stroke-width","1")
        .attr("r",  ch/2-cp)
        .attr("cx", function(d){ return d.xoffset*(ch+cp)+ch/2; })
        .attr("cy", function(d){ return ch/2; })
        .style("cursor", "pointer")
        .on("click", function(d){ d.callback(); });

    buttons
        .append("text")
        .attr("id", function(d){ return d.id; })
        .attr("x", function(d){ return d.xoffset*(ch+cp)+ch/2; })
        .attr("y", function(d){ return ch/2; })
        //.style("dominant-baseline","central")
        .style("alignment-baseline","middle")
        .style("text-anchor","middle")
        .style("font-size",ch/3)
        .attr('pointer-events', 'none')
        .html(function(d){ return d.symbol; });

    d3.select("div#evocontrols #timeRange")
        .style("width",(w-2*cw-20)+"px")
        .style("height", ch+"px");

    d3.select("div#evocontrols #timeLabel")
        .style("position","relative")
        .style("left", "20px")
        .style("alignment-baseline","middle")
        .style("width",cw+"px")
        .style("line-height", ch+"px")
        .style("height", ch+"px")
        .style("bottom", "13px");

    changeButton();
    //makeLegend( );

    function resetClustering() {
        // we use the initial ordering of key
        var keys = originalKeys;
        var nodesMap = graph.nodeMap;
        var oldCoordinatesMap = {};
        keys.forEach(function(nodeKey){
            var node = nodesMap[nodeKey];
            oldCoordinatesMap[nodeKey] = {
                x : node.x,
                y : node.y,
                value: node.someValue
            }
        });

        // it is currently very brute force.. i'd like to find a more incremental approach to manage
        // the new hierarchies
        var json = JSON.parse(originalText);
        graph = parse(json);
        originalKeys = graph.nodes.map(function(n){
            return n.name;
        });
        graph.nodes.forEach(function(node){
            var oldCoordinate = oldCoordinatesMap[node.name];
            if (oldCoordinate) {
                node.oldX = oldCoordinate.x;
                node.oldY = oldCoordinate.y;
                node.someValue = oldCoordinate.value;
            }
        });

    }

    function changeTrack() {
        trackMode = !trackMode;
        svg.selectAll("g.nodeBar")
            .data(nodes.filter(function(n) { return !n.children; }), function(d){ return d.key})
            .selectAll("path")
            .transition().duration(300).attr("d", arc);
        changeButton();
    }

    function changeButton() {
        function evaluateButton() {
            if (trackMode) return null;
            return true;
        }
        function evaluateOpacity() {
            return trackMode ? 1 : 0.5;
        }

        d3.select(".sortButton").attr('disabled', evaluateButton);
        d3.select(".sortWithoutButton").attr('disabled', evaluateButton);
        d3.select(".sortButton").style("opacity", evaluateOpacity);
        d3.select(".sortWithoutButton").style("opacity", evaluateOpacity);
    }




    function changeSortingOrder() {
        if (wholeChartSortEnabled) {
            wholeChartSortEnabled = false;
            sortOnNodeValue = clusterSortEnabled = true;
            // in that case we need to re-enable the original clustering
            if (originalCluster) {
                resetClustering()
            } else {
                assignCluster(clusterDefinition, graph);
            }
            transitionToCluster(true);
            return;
        } else {
            sortOnNodeValue = !sortOnNodeValue;
            clusterSortEnabled = !clusterSortEnabled;
        }
        //debugger;
        // we do like a cluster transition, but we know that the control points of the spline will not change,
        // as nodes are reorganized inside cluster
        // if we are already sorting on whole chart, sort on cluster

        // we just need to move nodes and links accordingly

        nodes.forEach(function(n){
            n.oldX = n.x;
        });

        nodes = cluster.nodes(graph.treeRoot);

        // move links

        // move nodes
        var selection = svg.selectAll("g.node")
            .data(nodes.filter(function(n) { return !n.children; }),  function(d){ return d.key});


        // fix key problem, you shpuld use a key function there to fix issues
        selection.select('text').attr("dx", function(d) { return d.x < 180 ? 8 : -8; })
            .attr("dy", ".31em")
            .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
            .attr("transform", function(d) { return d.x < 180 ? null : "rotate(180)"; })

        selection.transition().duration(900)
            .attrTween("transform", function(d) {
                var oldMatrix = "rotate(" + (d.oldX - 90) + ")translate(" + d.y + ")";
                var newMatrix = "rotate(" + (d.x - 90) + ")translate(" + d.y + ")";
                return d3.interpolateString(oldMatrix, newMatrix);
            });
        selection.exit().remove();

        var handle = svg.selectAll("g.nodeBar")
            .data(nodes.filter(function(n) { return !n.children; }), function(d){ return d.key});

        // see https://bl.ocks.org/mbostock/5348789 for concurrent transitions,
        // but i really find it bad... so i will no do it
        handle.select("path").transition().duration(900).attr("transform", function(d) {
            var newMatrix = "rotate(" + (d.x  ) + ")";
            return newMatrix
        });

        var path = svg.selectAll("path.link");

        // right now we use a map, keys are sourceKey-targetKey, values are the index in the new spline array
        path.transition().attrTween("d",
            function(d, i, a) {
                // oldspline use oldX
                // newspline use x
                var key = d.name1 + '-' + d.name2;
                var index = splinesMap[key];
                var oldSpline = [];
                for (var j = 0; j < splines[index].length; j++) {
                    var s = Object.assign({}, splines[index][j]);
                    // when we get back to old cluster, splines array is not updated
                    // as we got NEW nodes in the graph array, so the x coordinate
                    // is really the old coordinate in that case
                    if (s.oldX) { s.x = s.oldX; }
                    oldSpline.push(s);
                }

                var newSpline = splines[index].map(function(s) {
                        return {x: s.x, y:s.y}}
                );
                var interpolate = d3.interpolate(oldSpline, newSpline);
                return function(t) {

                    return line(interpolate(t))
                };

            }


        ).duration(900);
    }


    // things are now complicated, due to the fact that we have a 'third' clustering, ie
    // when we sort on the whole 'tracks' we do not take cluster into account anymore

    // we return to no-sorting when we switch clustering
    function transitionToCluster(dontChangeCluster) {

        if (!dontChangeCluster) {
            originalCluster = !originalCluster;
        }

        if (!dontChangeCluster) {
            if (wholeChartSortEnabled) {
                wholeChartSortEnabled = false;
                clusterSortEnabled = sortOnNodeValue = true;
            }
            if (!originalCluster) {
                assignCluster(clusterDefinition, graph);
                fireClusterListeners(true);
            } else {
                resetClustering();
                fireClusterListeners(false);
            }
        } else {
            if (!sortOnNodeValue) {
                if (originalCluster) {
                    resetClustering();
                } else {
                    assignCluster(clusterDefinition,graph);
                }
                fireClusterListeners(false);
            } else {
                fireClusterListeners(false);
            }
        }

        // brute-force approach, there may be an incremental way to do it
        var newSplines;
        if (summaryMode) {
            newSplines = bundle(summaryLinks);
            summaryLinks.forEach(function(link, index){
                newSplinesMap[link.name1 + '-' + link.name2] = index;
            });
        } else
        {
            links = graph.frames;
            newSplinesMap = {};
            links[0].forEach(function(link, index){
                newSplinesMap[link.name1 + '-' + link.name2] = index;
            });
            newSplines = bundle(graph.frames[curFrame]);
        }
        nodes = cluster.nodes(graph.treeRoot);
        var done = false;
        var path = svg.selectAll("path.link");

        // right now we use a map, keys are sourceKey-targetKey, values are the index in the new spline array
        path.transition().attrTween("d",
            function(d, i, a) {

                //if (i != 2) return;
                // make a copy of the targeted Spline, and put all x to the value of OldX..
                var oldSpline = [];
                var key = d.name1 + '-' + d.name2;
                var index = splinesMap[key];

                var debug = false;
                if (!splines[i]) {
                    console.log('No spline found for this index', i);
                    return;
                }
                for (var j = 0; j < splines[index].length; j++) {
                    var s = Object.assign({}, splines[index][j]);
                    // when we get back to old cluster, splines array is not updated
                    // as we got NEW nodes in the graph array, so the x coordinate
                    // is really the old coordinate in that case
                    if (s.oldX && (!originalCluster || wholeChartSortEnabled)) { s.x = s.oldX; }
                    oldSpline.push(s);
                }


                oldSpline = oldSpline.map(function(s) {
                    return {x: s.x, y: s.y};
                });
                var simpleSpline = newSplines[index].map(function(s) {
                        return {x: s.x, y:s.y}}
                );

                // we want to have the simple numbers of points between the two spline, to
                // have a nice transition
                var delta = simpleSpline.length - oldSpline.length;

                // TODO find a way to automate this step
                if (oldSpline.length < simpleSpline.length) {
                    var pathToTop = Math.floor(simpleSpline.length / 2);
                    // for 1 => 0 then add index 1(CP) 2(center) 3 (CP) (should not happen)
                    // for 3 => 1 then add index 1(CP) and 3(CP)

                    var recomposedOldSpline = [];
                    recomposedOldSpline[0] = oldSpline[0];
                    if (delta == 2 && oldSpline.length == 3) {
                        recomposedOldSpline[1] = oldSpline[0];
                        recomposedOldSpline[2] = oldSpline[1];
                        recomposedOldSpline[3] = oldSpline[2];
                        recomposedOldSpline[4] = oldSpline[2];
                    }  else if (delta == 2 && oldSpline.length == 1) {
                        recomposedOldSpline[1] = oldSpline[0];
                        recomposedOldSpline[2] = oldSpline[0];
                    } else if (delta == 4 && oldSpline.length ==1) {
                        recomposedOldSpline[1] = oldSpline[0];
                        recomposedOldSpline[2] = oldSpline[0];
                        recomposedOldSpline[3] = oldSpline[0];
                        recomposedOldSpline[4] = oldSpline[0];
                    }
                    else {
                        recomposedOldSpline = oldSpline;
                    }

                } else if (delta == -2) { // (5 < 3)
                    // newer spline has less target point than older spline
                    var recomposedNewSpline = [];
                    if (simpleSpline.length === 3) {
                        recomposedNewSpline[0] = simpleSpline[0];
                        recomposedNewSpline[1] = simpleSpline[0];
                        recomposedNewSpline[2] = simpleSpline[1];
                        recomposedNewSpline[3] = simpleSpline[2];
                        recomposedNewSpline[4] = simpleSpline[2];
                    } else if (simpleSpline.length === 1) {
                        recomposedNewSpline[0] = simpleSpline[0];
                        recomposedNewSpline[1] = simpleSpline[0];
                        recomposedNewSpline[2] = simpleSpline[0];
                    }
                    simpleSpline = recomposedNewSpline;
                    recomposedOldSpline = oldSpline;

                } else if (delta == -4) {
                    console.log(oldSpline, simpleSpline, '-4, this case should not happens');
                } else {
                    console.log('CASE NOT HANDLED', delta);
                    recomposedOldSpline = oldSpline;
                }

                var interpolate = d3.interpolate(recomposedOldSpline, simpleSpline);

                // we can update the spline as we are done
                setTimeout(function(){
                    if (!done){
                        done = true;
                        splines = newSplines;
                        // we do not want to rebind data here
                    }

                },800);

                return function(t) {

                    return line(interpolate(t))
                };
                //return d3.interpolateString(a, line(splines[i]));
                //return line(splines[i]);
            })
            .duration(900);

        // why if i forget the key function,
        var selection = svg.selectAll("g.node")
            .data(nodes.filter(function(n) { return !n.children; }), function(d){ return d.key});
        selection.enter().append("svg:g")
            .attr("class", "node")
            .attr("id", function(d) { return "node-" + d.key; })
            .attr("transform", function(d) {
                var matrix = "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"
                return matrix;
            })
            .append("svg:text")
            .text(function(d) { return d.key; });
        selection.select('text').attr("dx", function(d) { return d.x < 180 ? 8 : -8; })
            .attr("dy", ".31em")
            .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
            .attr("transform", function(d) { return d.x < 180 ? null : "rotate(180)"; })

        selection.transition().duration(900)
            .attrTween("transform", function(d) {
                var oldMatrix = "rotate(" + (d.oldX - 90) + ")translate(" + d.y + ")";
                var newMatrix = "rotate(" + (d.x - 90) + ")translate(" + d.y + ")";
                return d3.interpolateString(oldMatrix, newMatrix);
            });
        selection.exit().remove();



        var handle = svg.selectAll("g.nodeBar")
            .data(nodes.filter(function(n) { return !n.children; }), function(d){ return d.key});

        // see https://bl.ocks.org/mbostock/5348789 for concurrent transitions,
        // but i really find it bad... so i will no do it
        var hpath = handle.select("path").transition().duration(900).attr("transform", function(d) {
            var newMatrix = "rotate(" + (d.x  ) + ")";
            return newMatrix
        });
        //TODO remove unused handle

        hpath.transition()
            .delay(function(d,i){return 900+i;})
            .duration(900).style("fill", function(d){
                if (originalCluster) {
                    if (!wholeChartSortEnabled) {
                        return ("color" in d)?d.color:stdEdgeColor;
                    }
                    return 'grey'

                } else {
                    if (d.clusterKey === 'LigandPocket: ') {
                        return 'cyan';
                    }
                    if (d.clusterKey === ' GproteinPocket: ') {
                        return 'magenta';
                    }
                    return 'grey';
                }
            });

    }





    function changeAbsoluteSortingOrder() {
        // if we are already sorting on whole chart, sort on cluster
        if (clusterSortEnabled) {
            clusterSortEnabled = false;
            sortOnNodeValue = wholeChartSortEnabled = true;
        } else {
            sortOnNodeValue = !sortOnNodeValue;
            wholeChartSortEnabled = sortOnNodeValue;
        }
        if (wholeChartSortEnabled) {
            assignSimpleCluster(graph);
        }
        transitionToCluster(true);
    }


    /**
     *
     * we generate a clustering with a rooot node
     *
     * @param graph
     */
    function assignSimpleCluster(graph) {
        var filteredNodes = nodes.filter(function(n) { return !n.children; });
        var nodesMap = graph.nodeMap;
        var tempNodes = [];
        var root = nodesMap[""];
        root.children = [];
        filteredNodes.forEach(function(node){
            node.oldX = node.x;
            node.parent = root;
            node.clusterKey = '';
            tempNodes.push(node);
            root.children.push(node);
        });
        graph.nodes = tempNodes;
    }

    /**
     *
     * @param clusterDefinition {}
     *
     * keys are the key of the cluster
     * values are array that correspond to node keys
     *
     */
    function assignCluster(clusterDefinition, graph) {

        var keys = Object.keys(clusterDefinition);
        var tempNodes = [];
        var nodesMap = graph.nodeMap;
        var root = nodesMap[""];
        root.children = [];
        keys.forEach(function(clusterKey){

            var nodesArray = clusterDefinition[clusterKey];
            var clusterNode;

            // if a cluster node already exist, we take it into account, but reset its children
            if   (nodesMap[clusterKey]) {
                clusterNode = nodesMap[clusterKey];
                clusterNode.children = [];
                clusterNode.oldX = clusterNode.x;
                clusterNode.oldY = clusterNode.y;
            } else
            {
                clusterNode = {
                    key: clusterKey,
                    name: clusterKey,
                    children: [],
                    parent: root,
                    clusterName: clusterKey
                };
            }
            root.children.push(clusterNode);
            nodesMap[clusterKey] = clusterNode;
            tempNodes.push(clusterNode);
            nodesArray.forEach(function(node){
                if (!node.clusterKey) {
                    node = nodesMap[node];
                }
                node.oldX = node.x;
                node.parent = clusterNode;
                node.clusterKey = clusterKey;
                tempNodes.push(node);
                clusterNode.children.push(node);
            });
            // for legend, we can map the names of the cluster with an ordinal scale, iterates over it
            // and we are done with the legend part
        });
        graph.nodes = tempNodes;
        // A   => ROOT
        // 1  2  3 => CLUSTERS
        // . . . . . . . . . => NODES
        // once this is done, we use a pass thru the cluster and bundle layout
    }
}

var playing = false;
var frameskip = 1;
var curFrame = 0;

function setFrame(frame){
    if (summaryMode) {
        return; // make no sense to setFrame in summary mode
    }
    curFrame = frame;
    d3.select("span[id=timeLabel]")
        .text(""+frame);

    splines = bundle(links[frame]);

    path = svg.selectAll("path.link")
        .data(links[frame], function(d,i){ return "source-" + d.source.key + "target-" + d.target.key;});//, function(d){ return {source:d.source, target:d.target}; });

    path.enter().append("svg:path")
        .attr("class", function(d) {
            var ret = "link source-" + d.source.key + " target-" + d.target.key;
            if( d.source.key in toggledNodes || d.target.key in toggledNodes)
                ret+=" toggled";
            return ret;
        });
    //.attr("class", function(d) { return "link source-" + d.source.key + " target-" + d.target.key; });
    path.style("stroke-width",function(d){ return d.width?d.width:stdEdgeWidth; })
        .attr("class", function(d) {
            var ret = "link source-" + d.source.key + " target-" + d.target.key;
            if( d.source.key in toggledNodes || d.target.key in toggledNodes)
                ret+=" toggled";
            return ret;
        })
        //.attr("class", function(d) { return "link source-" + d.source.key + " target-" + d.target.key; })
        .style("stroke",function(d){ return ("color" in d)?d.color:stdEdgeColor; })
        .attr("d", function(d, i) { return line(splines[i]); });

    path.exit().remove();
    splinesMap = {}
    links[frame].forEach(function(link, index){
        splinesMap[link.name1 + '-' + link.name2] = index;
    });

    curFrame = frame;
}

var tickListeners = [];
tickListeners[0] = setFrame;

function fireTickListeners(frame){
    for(var i=0;i<tickListeners.length;i++){
        tickListeners[i](frame);
    }
}

function playTick(){
    var timeRange = d3.select("input[id=timeRange]");
    var curValue = parseInt(timeRange[0][0].value);
    if(playing && curValue+frameskip<links.length-1) {
        var skip = Math.min(frameskip, links.length-1-frameskip);
        timeRange[0][0].value = curValue+skip;
        fireTickListeners(curValue+skip);
        //setFrame(curValue+skip);

        setTimeout(playTick, 50);
    }else{
        playing=false;
    }

    //Update play/pause symbol
    var sym = playing?"#":">";
    d3.select("#playpause")
        .html(sym);
}

function playpause(){
    playing = !playing;
    if(playing) {
        playTick();
    }
}

function reverse(){
    var timeRange = d3.select("input[id=timeRange]");
    var minVal = timeRange.attr("min");
    timeRange[0][0].value = minVal;
    fireTickListeners(minVal);
    //setFrame(minVal);
}

function forward(){
    playing = false;
    var timeRange = d3.select("input[id=timeRange]");
    var maxVal = timeRange.attr("max");
    timeRange[0][0].value = maxVal;
    fireTickListeners(maxVal);
    //setFrame(maxVal);
}


function toggleNode(d,i){
    var toggled = !d3.select(this.parentNode).classed("toggledNode");
    d3.select(this.parentNode)
        .classed("toggledNode", function(d){return toggled; });

    var name = d.name.substring(d.name.lastIndexOf(".")+1);
    if(!toggled)
        delete toggledNodes[name];
    else
        toggledNodes[name] = "";

    path = svg.selectAll("path.link")
        .classed("toggled", function(d) {
            return ( d.source.key in toggledNodes || d.target.key in toggledNodes)
        });

    //svg.selectAll("path.link/target-"+d.key);
    fireTickListeners(curFrame);
}

function mouse(e) {
    return [e.pageX - rx, e.pageY - ry];
}

function mouseoverNode(d) {
    svg.selectAll("path.link.target-" + d.key)
        .classed("target", true)
        .each(updateNodes("source", true));

    svg.selectAll("path.link.source-" + d.key)
        .classed("source", true)
        .each(updateNodes("target", true));
}

function mouseoutNode(d) {
    svg.selectAll("path.link.source-" + d.key)
        .classed("source", false)
        .each(updateNodes("target", false));

    svg.selectAll("path.link.target-" + d.key)
        .classed("target", false)
        .each(updateNodes("source", false));
}

function updateNodes(name, value) {
    return function(d) {
        //if (value) this.parentNode.appendChild(this);
        svg.select("#node-" + d[name].key).classed(name, value);
    };
}

function cross(a, b) {
    return a[0] * b[1] - a[1] * b[0];
}

function dot(a, b) {
    return a[0] * b[0] + a[1] * b[1];
}

// handle upload button
function upload_button(el, callback) {
    var uploader = document.getElementById(el);
    var reader = new FileReader();

    reader.onload = function(e) {
        var contents = e.target.result;
        callback(contents);
    };

    uploader.addEventListener("change", handleFiles, false);

    function handleFiles() {
        d3.select("#table").text("loading...");
        var file = this.files[0];
        reader.readAsText(file);
    }
}



function parseCluster(cluster) {
    var keyValuesClusterArray = cluster.split('"');
    var numberOfObjects = Math.floor(keyValuesClusterArray.length / 2);
    var clusterDefinition = {};
    for (var i = 0; i < numberOfObjects; i++) {
        var keys = keyValuesClusterArray[i * 2 + 1].split(' ');

        clusterDefinition[keyValuesClusterArray[i * 2]] = keys;
        keys.forEach(function(k){
            graph.nodeMap[k].present = true;
        });
    }
    var absentCluster = [];
    graph.nodes.forEach(function(n){
        if (!n.present) {
            absentCluster.push(n.name);
        }
    });
    clusterDefinition['Others'] = absentCluster;

    // for whatever reasons, i have 2 MORE nodes here !!
    return clusterDefinition;
}


var clusterListeners = [];
function fireClusterListeners(clusteringEnabled){
    for(var i=0;i<clusterListeners.length;i++){
        clusterListeners[i](clusteringEnabled);
    }
}



var summaryListeners = [];
function fireSummaryListeners(){
    for(var i=0;i<summaryListeners.length;i++){
        summaryListeners[i](summaryLinks);
    }
}

var summaryLinks;

var D;



function transitionToSummary(){
    //links contains all the frames
    if (summaryMode) {
        // take from setFrame, but with transition
        splines = bundle(links[curFrame]);
        path = svg.selectAll("path.link")
            .data(links[curFrame], function(d,i){ return "source-" + d.source.key + "target-" + d.target.key;});//, function(d){ return {source:d.source, target:d.target}; });

        //.attr("class", function(d) { return "link source-" + d.source.key + " target-" + d.target.key; });
        path.attr("class", function(d) {
            var ret = "link source-" + d.source.key + " target-" + d.target.key;
            if( d.source.key in toggledNodes || d.target.key in toggledNodes)
                ret+=" toggled";
            return ret;
        });
        path.transition().duration(800).style("stroke-width",function(d){ return d.width?d.width:stdEdgeWidth; });

        path.exit().transition().duration(800)
            .style("stroke-width",function(d){ return 0; }).remove();
        summaryMode = !summaryMode;
        removeLegend();
        splinesMap = {};
        links[curFrame].forEach(function(link, index){
            splinesMap[link.name1 + '-' + link.name2] = index;
        });
        return;
    }


    if(playing) { playpause(); }

    summaryMode = !summaryMode;

    //Initialize empty two-dim array
    var n = nodes.length;
    var countMatrix = new Array(n);
    for(var i=0;i<n;i++) {
        countMatrix[i] = new Array(n);
        for(var j=0;j<n;j++)
            countMatrix[i][j] = 0;

        //Add index to nodes for faster lookup
        nodes[i].idx = i;
    }

    var maxVal = 0;

    //Go through all frames and add counts to distMatrix
    for(var f=0;f<links.length;f++){
        for(var i=0;i<links[f].length;i++){
            idx1 = links[f][i].source.idx;
            idx2 = links[f][i].target.idx;
            countMatrix[idx1][idx2]++;
            countMatrix[idx2][idx1]++;
            if (countMatrix[idx2][idx1]>maxVal)
                maxVal = countMatrix[idx2][idx1];
        }
    }

    summaryLinks = [];
    for(var i=0;i<n;i++) {
        for(var j=0;j<n;j++){
            if(countMatrix[i][j]==0) continue;
            var ndi, ndj;
            for(var nd=0;nd<n;nd++) {
                if (nodes[nd].idx == i) ndi = nodes[nd];
                if (nodes[nd].idx == j) ndj = nodes[nd];
            }
            summaryLinks.push( {
                "source":ndi,
                "target":ndj,
                "name1": ndi.name,
                "name2": ndj.name,
                "weight":countMatrix[i][j]} );
        }
    }



    var summaryLinksExtent = d3.extent(summaryLinks, function(d) {
        return d.weight;
    });

    var legendMaxHeight = 20;

    var linkWidthScale = d3.scale.linear()
        .domain(summaryLinksExtent)
        .range([0, legendMaxHeight]);

    D = countMatrix;
    splines = bundle(summaryLinks);

    options = {
        width: 200,
        height: legendMaxHeight,
        minValue:0,
        maxValue: Math.floor(summaryLinksExtent[1] / 1000)
    };

    //TODO(chab) make a better leged
    //makeLegend(options);


    path = svg.selectAll("path.link")
        .data(summaryLinks, function(d,i){
            var key = "source-" + d.source.key + "target-" + d.target.key;
            return key;
        });


    // some nodes are removed because they are not

    path.enter().insert("svg:path")
        .style("stroke-width",function(d){ return 0; });

    path.attr("class", function(d) {
        var ret = "link source-" + d.source.key + " target-" + d.target.key;
        if( d.source.key in toggledNodes || d.target.key in toggledNodes)
            ret+=" toggled";
        return ret;
    })
        .attr("d", function(d, i) { return line(splines[i]); })
        .transition().duration(800)
        .style("stroke-width",function(d){ return linkWidthScale(d.weight) })
        .style("stroke",function(d){ return ("color" in d)?d.color:stdEdgeColor; });

    path.exit().remove();

    splinesMap = {};
    summaryLinks.forEach(function(link, index){
        splinesMap[link.name1 + '-' + link.name2] = index;
    });
}

function checkDuplicate(dicoA, dicoB) {
    dicoA.forEach(function(key) {
        if (dicoB[key]) {
            console.log(key, 'is here');
        } else {
            console.log(key, 'Absent from', dicoB);
        }
    })
}


// width legend                   (0,0)           - (maxWidhth, 0)
//                                               --
//                                            -----
//                                         --------
// x axis on the bottom (0,legendHeight) ---------- (maxwidth, legendHeight )
// SVG PATH would be   M 0 <LH>  L <MX> <LH> L <MW> 0 L <MW> <LH>

function removeLegend() {
    svg.select(".legendChart").remove();
}

function makeLegend(options) {

    // remove old legend
    removeLegend();

    var lineGenerator = d3.svg.line()
        .x(function(d) { return d.x; })
        .y(function(d) { return d.y; })
        .interpolate("linear");


    var topX = 0, topY= 0, width = options.width, height = options.height,
        minValue = options.minValue, maxValue = options.maxValue


    var axisXScale = d3.scale.linear()
        .domain([options.minValue, options.maxValue])
        .range([0, options.width]);

    var xAxis = d3.svg.axis().scale(axisXScale).tickSize(1);


    var linePoints = [
        {x:0, y:height},
        {x:width, y:height},
        {x:width, y:0},
        {x:0, y:height }
    ];

    // main leged

   //

    var xOrigin = 180;
    var yOrigin = 250;
    var axisPadding = 10;
    // add axis

    var legendGraph = svg.append("g")
        .attr("class","legendChart")
        .attr("transform", "translate(" + xOrigin+ "," + yOrigin + ")");

    legendGraph.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + (axisPadding + height) + ")")
        .call(xAxis);
    var path = legendGraph.append("path").classed("legend", true);
    path.datum(linePoints).attr("d", lineGenerator);
}
