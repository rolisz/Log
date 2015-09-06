/**
 * Created with PyCharm.
 * User: Roland
 * Date: 8/21/12
 * Time: 12:58 PM
 * To change this template use File | Settings | File Templates.
 */

// A formatter for counts.
var formatCount = d3.format(".2f");
// Generate an Irwin–Hall distribution of 10 random variables.
var values = d3.range(100).map(d3.random.normal(100,30));

var parse = d3.time.format("%Y-%m-%d").parse;
format = d3.time.format("%Y-%m-%d");
var min = 0, max = 41;
filter = function(d,i) {
    return i > min && i < max;
}

w = 40;
h = 400;
var x = d3.time.scale()
    .domain([parse("2012-01-01"), parse("2012-12-12")])

var y = d3.scale.linear()
    .domain([0, d3.max(values)])
    .range([0,h]);

var chart = d3.select("body").append("svg")
    .attr("class", "chart")
    .attr("width", w * values.filter(filter).length)
    .attr("height", h+100).call(d3.behavior.drag()
    .on("dragstart", function(d) {
        console.log(d3.event)
    })
    .on("drag", function(d) {
        console.log(d3.event)
        console.log(max,min,d3.event.dx)
        if (d3.event.dx > 2 && max < values.length) {
            min +=1;
            max +=1;
        }
        else if (d3.event.dx < -2 && min >= 1) {
            min -= 1;
            max -=1;
        }
        redraw()
    })
    .on("dragend", function() {
        console.log("end");
    }));

chart.selectAll("rect")
    .data(values.filter(filter))
    .enter().append("rect")
    .attr("x", function(d, i) { return i * w; })
    .attr("y",h)
    .attr("height", 0)
    .attr("width", w)
    .transition()
    .attr("y", function(d) { return h - y(d) - .5; })
    .duration(1000)
    .attr("height",y)
    .each("end",function() {
        chart.selectAll("text")
            .data(values.filter(filter))
            .enter().append("text")
            .attr("x", function(d, i) { return i * w; })
            .attr("y", function(d) { return h - y(d) - .5; })
            .attr("opacity",0)
            .attr("dx", 0) // padding-right
            .attr("dy", ".35em") // vertical-align: middle
            .attr("text-anchor", "begin") // text-align: right
            .text(function(d) { return formatCount(d) })
            .transition()
            .attr("opacity",1)

    })


chart.selectAll(".date")
    .data(x.ticks(10))
    .enter().append("text")
    .attr("x", function(d, i) { return i * w * 3.9})
    .attr("y", h+20)
    .attr("opacity",0)
    .attr("dx", 10) // padding-right
    .attr("dy", ".35em") // vertical-align: middle
    .attr("text-anchor", "begin") // text-align: right
    .attr("transform",function(d,i) { return "rotate(60 "+ i*w*3.9 +" 420)" })
    .text(function(d) { return format(d); } )
    .transition()
    .attr("opacity",1)
chart.selectAll("line")
    .data(y.ticks(10))
    .enter().append("line")
    .attr("x1", 0)
    .attr("x2", w * values.length)
    .attr("y1", y)
    .attr("y2", y)
    .style("stroke", "#ccc");

function redraw() {
    chart.selectAll("rect")
        .data(values.filter(filter))
        .attr("x", function(d, i) { return i * w; })
        .attr("y", function(d) { return h - y(d) - .5; })
        .attr("height",y)
    chart.attr("transform","")


}


/*  chart.selectAll(".rule")
 .data(y.ticks(10))
 .enter().append("text")
 .attr("class", "rule")
 .attr("x", 0)
 .attr("y", function(d) { return h - y(d) - .5 })
 .attr("dx", 20)
 .attr("text-anchor", "middle")
 .text(String);

 chart.append("line")
 .attr("x1", 0)
 .attr("x2", w * values.length)
 .attr("y1", h - .5)
 .attr("y2", h - .5)
 .style("stroke", "#000");*/
