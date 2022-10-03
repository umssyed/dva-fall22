var formatTime = d3.timeFormat("%b %y");
const parseDate = d3.timeParse("%Y-%m-%d");
const dataset = d3.csv("boardgame_ratings.csv");
var margin = {top: 20, right: 10, bottom: 20, left: 10};
var width = 960 - margin.left - margin.right;
var height = 500 - margin.top - margin.bottom;

//Function to handle date-time
var timeConv = function(input_date) {
    const date = new Date(input_date);
    return formatTime(date);
}

//Create time array if required
const time = dataset.then(function(data) {
    time_array = [];
    data.forEach(function(d) {
        time_array.push(timeConv(d.date))
    });
    return time_array;
})

//--------------------Start Import and adjust data----------------//
dataset.then(function(data) {
    //Converting all date elements
    data.forEach(function(d) {
        d.date = parseDate(d.date)
    })
    var dataset_1 = data
    console.log("original data: ")
    console.log(data)


    console.log("\n\n\n=========================\n\n\n")
    //For each line in the linechart
    var gameLines = data.columns.slice(1).map(function(id) {
        var x = {
            id: id,
            values: data.map(function(d) {

                return {
                    date: d.date,
                    y_val: +d[id]
                }
            })
        }
        return x;
    });

    console.log("Log gameLines:")
    console.log(gameLines)
    console.log("\n\n\n=========================\n\n\n")

    var gameLines_1 = []
    for (var i in gameLines) {
        var game = gameLines[i];
        if (game['id'].includes('=count')) {
            gameLines_1.push(game)
        }
    }

    //Find maxDate and minDate for scaling
    var maxDate = d3.max(data, function(d) {return d.date});
    var minDate = d3.min(data, function(d) {return d.date});

    //Create X-SCALE
    const xScale = d3.scaleTime().range([0, width]);
    xScale.domain(d3.extent(data, function(d) {
        return d.date;
    }))

    //Create Y-SCALE
    const yScale = d3.scaleLinear().range([height, 0]);
    yScale.domain([
        (0),
        d3.max(gameLines, function(l) {
            return d3.max(l.values, function(v) {
                return v.y_val;
            })
        })
    ]);

    //Create AXES
    const yAxis = d3.axisLeft()
        .ticks(10)
        .scale(yScale);

    const xAxis = d3.axisBottom()
        .ticks(d3.timeMonth.every(3))
        .tickFormat(d3.timeFormat("%b %y"))
        .scale(xScale);

    //---------------------------Start Plotting Q3 A---------------------------//
    //Identify coloring
    var color = d3.schemeCategory10;
    //Create Lines using the line generator
    var line = d3.line()
        .x(function(d) {
            return xScale(d.date);
        })
        .y(function(d) {
            return yScale(d.y_val);
        });

    //Create the base SVG element with height/width for Chart 1
    const svg1 = d3.select("body").append("svg")
        .attr("id", "svg-a")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("text").attr("id", "title-a")
        .text("Number of Ratings 2016-2020")

    //Append G element and start building chart
    var chart_one = d3.select("#svg-a").append("g")
        .attr("transform", "translate(" + 5*margin.left + "," + margin.top + ")")
        .attr("id", "plot-a")
        .append("g")
        .attr("id", "lines-a")

    //Create x-axis
    d3.select("#plot-a").append("g")
        .attr("id", "x-axis-a")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .append("text")
        .text("Month")

    //Create y-axis
    d3.select("#plot-a").append("g")
        .attr("id", "y-axis-a")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("dy", ".75em")
        .attr("y", 6)
        .text("Num of Ratings")

    //Generate lines
    const lines = chart_one.selectAll("lines")
        .data(gameLines_1)
        .enter()
        .append("g")

    //Append path to lines
    lines.append("path")
        .attr("d", function(d) {
            return line(d.values)
        })
        .style("stroke", function(d, i) {
            return color[i]
        })
        .style("fill", "None");

    //Format lines
    lines.append("text")
        .attr("class", "series_label")
        .datum(function(d) {
            return {
                id: d.id,
                value: d.values[d.values.length - 1]
            }
        })
        .attr("transform", function(d) {
            var date = d.value.date;
            var val = d.value.y_val;
            return "translate(" + xScale(date)  + "," + yScale(val) + ")";
        })
        .attr("x", 3)
        .attr("dy", ".35em")
        .text(function(d) {
            var name_full = d.id;
            var name = name_full.substr(0, name_full.indexOf('='));
            return name
        });


    //---------------------------Start Plotting Q3 B---------------------------//

    //Identify coloring
    var color_2 = d3.schemeCategory10;
        //Create Lines using the line generator
    var line_2 = d3.line()
        .x(function(d) {
            return xScale(d.date);
        })
        .y(function(d) {
            return yScale(d.y_val);
        });

    //Create the base SVG element with height/width for Chart 1
    const svg2 = d3.select("body").append("svg")
        .attr("id", "svg-b")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("text").attr("id", "title-b")
        .text("Number of Ratings 2016-2020 with Rankings")

    //Append G element and start building chart
    var chart_two = d3.select("#svg-b").append("g")
        .attr("transform", "translate(" + 5*margin.left + "," + margin.top + ")")
        .attr("id", "plot-b")
        .append("g")
        .attr("id", "lines-b")

    //Create x-axis
    d3.select("#plot-b").append("g")
        .attr("id", "x-axis-b")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .append("text")
        .text("Month")


    //Create y-axis
    d3.select("#plot-b").append("g")
    .attr("id", "y-axis-b")
    .call(yAxis)
    .append("text")
    .attr("transform", "rotate(-90)")
    .attr("dy", ".75em")
    .attr("y", 6)
    .text("Num of Ratings")


    /**
    //Generate lines
    const lines_2 = chart_two.selectAll("lines")
    .data(gameLines_1)
    .enter()
    .append("g")

    //Append path to lines
    lines_2.append("path")
    .attr("d", function(d) {
        return line_2(d.values)
    })
    .style("stroke", function(d, i) {
        return color[i]
    })
    .style("fill", "None");

    //Format lines
    lines_2.append("text")
    .datum(function(d) {
        return {
            id: d.id,
            value: d.values[d.values.length - 1]
        }
    })
    .attr("transform", function(d) {
        var date = d.value.date;
        var val = d.value.y_val;
        return "translate(" + xScale(date)  + "," + yScale(val) + ")";
    })
    .attr("x", 3)
    .attr("dy", ".35em")
    .text(function(d) {
        var name_full = d.id;
        var name = name_full.substr(0, name_full.indexOf('='));
        return name
    });
    **/


});


    var gameOverviewRanks = [];

    //Populate date first and initialize object elements
    for (i in gameLines_1[0].values) {
        var elm = {}
        elm.date = gameLines_1[0].values[i].date;
        gameOverviewRanks.push(elm)
    }

    //Populate the name of each boardgame as an object
    for (i in gameLines_1) {
        var name_full = gameLines_1[i]['id'];
        var name = name_full.substr(0, name_full.indexOf('='));
        for (j in gameOverviewRanks) {
            gameOverviewRanks[j][name] = {}
        }
    }

    console.log(gameOverviewRanks)


