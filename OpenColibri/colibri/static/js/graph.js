var m = [50, 150, 50, 150],
    w = 350 - m[1] - m[3],
    h = 350 - m[0] - m[2],
    i = 0,
    root;
var max_x = 0;
var max_y = 0;
var tree = d3.layout.tree()
    .size([h, w]);

var diagonal = d3.svg.diagonal()
    .projection(function (d) {
        return [d.y, d.x];
    });

var vis = d3.select("#tree-container")
    .append("svg:svg")
    .attr("width", w + m[1] + m[3])
    .attr("height", h + m[0] + m[2])
    .append("svg:g")
    //.attr("transform", "translate(" + m[3] + "," + m[0] + ")");
    .attr("transform", "translate(10,0)");

var datasetID = window.location.pathname.split('/')[2]
d3.json("/api/colibri/extensiongraph/" + datasetID + "/tree/?format=json", function (json) {
    root = JSON.parse(json.extensionTreeGraph);
    root.x0 = h / 2;
    root.y0 = 0;

    function toggleAll(d) {
        if (d.children) {
            d.children.forEach(toggleAll);
            toggle(d);
        }
    }

    // Initialize the display to show a few nodes.
    // root.children.forEach(toggleAll);
    // toggle(root.children[1]);
    // toggle(root.children[1].children[2]);
    // toggle(root.children[9]);
    // toggle(root.children[9].children[0]);


    update(root);
    var vis2 = d3.select("#tree-container svg")
        .attr("width", max_x + 150)
        .attr("height", max_y + 150);
    var vis3 = d3.select("#tree-container svg g")
        .attr("transform", "translate(10, " + (max_y - 90 - 125) + ")");
});

function update(source) {
    var duration = d3.event && d3.event.altKey ? 5000 : 500;

    // Compute the new tree layout.
    var nodes = tree.nodes(root).reverse();

    // Normalize for fixed-depth.
    nodes.forEach(function (d) {
        d.y = d.depth * 90;
        if (d.y > max_x) {
            max_x = d.y
        }
        ;
        if (d.x > max_y) {
            max_y = d.x
        }
        ;
    });

    // Update the nodes…
    var node = vis.selectAll("g.node")
        .data(nodes, function (d) {
            return d.id || (d.id = ++i);
        });

    // Enter any new nodes at the parent's previous position.
    var nodeEnter = node.enter().append("svg:g")
        .attr("class", "node")
        .attr("transform", function (d) {
            return "translate(" + source.y0 + "," + source.x0 + ")";
        })
    nodeEnter.append("svg:circle")
        .attr("r", 1e-6)
        .on("click", function (d) {
            toggle(d);
            update(d);
        })
        .style("fill", function (d) {
            return d._children ? "lightsteelblue" : "#fff";
        });
    details = nodeEnter.append("svg:text")
        .attr("id", function (d) {
            return 'dataset_' + d.id
        })
        .attr("x", function (d) {
            return d.children || d._children ? -10 : 10;
        })
        .attr("dy", ".35em")
        .attr("text-anchor", "start")
        .style("fill-opacity", 1e-6)
    details.append("tspan")
        .attr('x', 0).attr('dy', '15')
        .append("svg:a")
        .attr("xlink:href", function (d) {
            return d.url;
        })
        .text(function (d) {
            return d.name.substr(0, 15) + (d.name.length > 15 ? '...' : '')
        });
    noderectagle = nodeEnter.append("svg:g")
        .attr("fill", "white")
        .attr("dy", "50")
        .attr("id", function (d) {
            return 'rec_dataset_' + d.id
        })
    noderec = noderectagle.append("svg:rect")
        .attr('x', 0).attr('y', 30)
        .attr("height", "130")
        .attr("class", "infobox hidden")
        .attr("width", "120")
        .attr("fill", "white")
        .attr('stroke', '#006C71')
    nodeimg = noderectagle.append("svg:image")
        .attr('x', 45).attr('y', 30)
        .attr("height", "32")
        .attr("class", "nodeimg hidden")
        .attr("width", "32")
        .attr("xlink:href", function (d) {
            if (d.revision_type) {
                return '/s/imgs/r_' + d.revision_type + '.png';
            } else {
                return '';
            }
        })
    detailstxt = noderectagle.append("svg:text")
        .attr("id", function (d) {
            return 'txtdataset_' + d.id
        })
        .attr("class", "infobox hidden")
        .attr("x", "0")
        .attr("dy", "50")
        .attr("fill", "black")
    detailstxt.append("tspan")
        .attr('x', 5).attr('dy', '80')
        .text(function (d) {
            return 'uploaded by ' + d.uploader;
        })
    detailstxt.append("tspan")
        .attr('x', 5).attr('dy', '15')
        .text(function (d) {
            return d.dateExtended;
        })
    detailstxt.append("tspan")
        .attr('x', 5).attr('dy', '15')
        .attr('class', function (d) {
            return ' ' + (d.shortDescription ? 'shortDescription' : '');
        })

    var insertLinebreaks = function (d) {
        if (d.shortDescription) {
            var el = d3.select(this);
            var words = d.shortDescription.split('\n');
            el.text('');

            for (var i = 0; i < words.length; i++) {
                var tspan = el.append('tspan').text(words[i]);
                if (i > 0)
                    tspan.attr('x', 5).attr('dy', '15');
            }
        }
    };

    d3.selectAll('.shortDescription').each(insertLinebreaks);

    details.on('mouseover', function (d) {
        $('#rec_dataset_' + d.id).children().show();
        $('#rec_dataset_' + d.id + ' .nodeimg').css("display", "inline");
    });
    node.on('mouseout', function (d) {
        $('#rec_dataset_' + d.id).children().hide();
        $('#rec_dataset_' + d.id + ' .nodeimg').css("display", "none");
    });

    // Transition nodes to their new position.
    var nodeUpdate = node.transition()
        .duration(duration)
        .attr("transform", function (d) {
            return "translate(" + d.y + "," + d.x + ")";
        });

    nodeUpdate.select("circle")
        .attr("r", 4.5)
        .style("fill", function (d) {
            return d.id == datasetID ? "red" : (d._children ? "lightsteelblue" : "#fff");
        });

    nodeUpdate.select("text")
        .style("fill-opacity", 1);

    // Transition exiting nodes to the parent's new position.
    var nodeExit = node.exit().transition()
        .duration(duration)
        .attr("transform", function (d) {
            return "translate(" + source.y + "," + source.x + ")";
        })
        .remove();

    nodeExit.select("circle")
        .attr("r", 1e-6);

    nodeExit.select("text")
        .style("fill-opacity", 1e-6);

    // Update the links…
    var link = vis.selectAll("path.link")
        .data(tree.links(nodes), function (d) {
            return d.target.id;
        });

    // Enter any new links at the parent's previous position.
    link.enter().insert("svg:path", "g")
        .attr("class", "link")
        .attr("d", function (d) {
            var o = {x: source.x0, y: source.y0};
            return diagonal({source: o, target: o});
        })
        .transition()
        .duration(duration)
        .attr("d", diagonal);

    // Transition links to their new position.
    link.transition()
        .duration(duration)
        .attr("d", diagonal);

    // Transition exiting nodes to the parent's new position.
    link.exit().transition()
        .duration(duration)
        .attr("d", function (d) {
            var o = {x: source.x, y: source.y};
            return diagonal({source: o, target: o});
        })
        .remove();

    // Stash the old positions for transition.
    nodes.forEach(function (d) {
        d.x0 = d.x;
        d.y0 = d.y;
    });
}

// Toggle children.
function toggle(d) {
    if (d.children) {
        d._children = d.children;
        d.children = null;
    } else {
        d.children = d._children;
        d._children = null;
    }
}
