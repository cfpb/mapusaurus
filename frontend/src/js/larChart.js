function destroyLarChart() {
    d3.select("#plot-container").selectAll("*").remove();
}

function plotLarVolume() {

    var margin = {top: 20, right: 20, bottom: 30, left: 40},
        width = 1180 - margin.left - margin.right,
        height = 200 - margin.top - margin.bottom;
    var barWidth = width / larVolume.length;

    var data = _.zip(pctMinority, larVolume);
    data = _.sortBy(data, function(item) { return item[0]; });
    data = _.zip.apply(_, data);
    pctMinority = data[0];
    larVolume = data[1];

    var colorMap = d3.scale.quantile().domain([0, 0.5, 0.8, 1.0]).range(["#E8E7E3", "#B7C8D6", "#7FA2BB"]);

    d3.select("#plot-container").selectAll("*").remove();
    
    var larSvg = d3.select("#plot-container")
        .append("svg")
                .attr("width", width)
                .attr("height", height);

    var minSvg = d3.select("#plot-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
    
    var larChart = larSvg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    var minChart = minSvg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var larX = d3.scale.ordinal().rangeRoundBands([0, width], 0.1);
    var larY = d3.scale.linear().range([height, 0]);
    var larXAxis = d3.svg.axis().scale(larX).orient("bottom");
    var larYAxis = d3.svg.axis().scale(larY).orient("left");

    var minX = d3.scale.ordinal().rangeRoundBands([0, width], 0.1);
    var minY = d3.scale.linear().range([height, 0]);
    var minXAxis = d3.svg.axis().scale(minX).orient("bottom");
    var minYAxis = d3.svg.axis().scale(minY).orient("left");

    larX.domain(geoIds);
    larY.domain([0, d3.max(larVolume, function(d) { return d; })]);

    minX.domain(geoIds);
    minY.domain([0, d3.max(pctMinority, function(d) { return d; })]);


    /*chart.append("g").attr("class", "x axis")
        .attr("transform", "translate(0, " + height - margin.bottom - margin.top  + ")")
        .call(xAxis)
        .selectAll("text")
        .attr("y", 0)
        .attr("x", 9)
        .attr("dy", ".35em")
        .attr("transform", "rotate(90)")
        .style("text-anchor", "start"); */

    larChart.append("g")
        .attr("class", "y axis")
        .call(larYAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".5em")
        .style("text-anchor", "end")
        .text("LAR per 1000 households");

    larChart.selectAll(".bar-lar")
        .data(larVolume)
        .enter().append("rect")
        .attr("class", "bar-lar")
        .attr("x", function(d, i) { return larX(geoIds[i]); })
        .attr("width", larX.rangeBand())
        .attr("y", function(d) { return larY(d); })
        .attr("height", function(d) { return height - larY(d); })
        .style("fill", function(d, i) { return colorMap(pctMinority[i]); });

    minChart.append("g")
        .attr("class", "y axis")
        .call(minYAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".5em")
        .style("text-anchor", "end")
        .text("Minority Percentage");

    minChart.selectAll(".bar-min")
        .data(pctMinority)
        .enter().append("rect")
        .attr("class", "bar-min")
        .attr("x", function(d, i) { return minX(geoIds[i]); })
        .attr("width",larX.rangeBand())
        .attr("y", function(d) { return minY(d); })
        .attr("height", function(d, i) {
        if ((height - larY(larVolume[i])) > 0.0) {
            return height - minY(d);
        }
        else {
            return 0;
        }})
        .style("fill", function(d) { return colorMap(d); });
}