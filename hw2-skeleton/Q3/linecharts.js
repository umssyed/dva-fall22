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
    console.log("\n\n================ Q3 B ================\n\n")
    //Find Catan, Codenames, Terraforming Mars, Gloomhavens data points
    console.log(gameLines_1)
    var gameOverview = [];
    var game_table = gameLines_1.map(function(d) {
        var name_full = d['id'];
        var name = name_full.substr(0, name_full.indexOf('='));
        var name_ranking = name + '=rank'

        var res = data.map(function(x) {
            var res = {
                name: name,
                date: x.date,
                count: +x[name_full],
                rank: +x[name_ranking],
            }
            return res;
        })
        return res
    })
    //Enter the dates and the first game only for now.
    for (i in game_table[0]) {
        x =  {
            date: game_table[0][i]['date']
        };
        x[game_table[0][i]['name']] = {
            count: game_table[0][i]['count'],
            rank: game_table[0][i]['rank']
        }
        gameOverview.push(x)
    }
    console.log("======================xxxxxxxxxxxxxxxx================")
    for (i in game_table) {
        var name = game_table[i][0]['name']
        if (name == 'Codenames' || name == 'Terraforming Mars' || name == 'Gloomhaven') {
            for (j in game_table[i]) {
                j_date = game_table[i][j]['date'];
                j_count = game_table[i][j]['count'];
                j_rank = game_table[i][j]['rank'];
                for (k in gameOverview) {
                    k_date = gameOverview[k]['date']
                    if (k_date == j_date) {
                        gameOverview[k][name] = {
                            count: j_count,
                            rank: j_rank
                        }
                        break;
                    }

                }

            }
        }
    }
    console.log(gameOverview)
    console.log("======================xxxxxxxxxxxxxxxx================")

    console.log("below here")

    //Identify coloring
    var color_2 = d3.schemeCategory10;
    var circleArray = []
    var colorArray = [d3.schemeCategory10, d3.schemeAccent];

    for (i=0; i < colorArray[0].length; i++) {
        var circleDict = {};
        circleDict.cx = (i*15)/0.2;
        circleDict.cy = 15;
        circleDict.r = 15;
        circleDict.color = colorArray[0][i];

        circleArray.push(circleDict);
    }

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

    //Append symbols
    //d3.select("#plot-b").append("g")
    //    .attr("id", "symbols-b")

    //Generate lines
    const lines_2 = chart_two.selectAll("lines")
        .data(gameLines_1)
        .enter()
        .append("g")

    //Append path to lines
    lines_2.append("path")
        .attr("d", function(d) {
            return line(d.values)
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

    //Append legends
    d3.select("#plot-b").append("g")
        .attr("id", "symbols-b")
        .selectAll("circle")
        .data(gameOverview).enter()
        .append("circle")
        .attr("cx", function(d) {

            return xScale(d.date)
        })
        .attr("cy", function(d) {
            console.log(d)
            return d.cy;
        })
        .attr("r", 10)
        .attr("fill", function(d) {
            return d.color;
        })


});





