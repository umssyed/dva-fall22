map.selectAll('path')
    .data(world.features)
    .enter()
    .append('path')
    .attr('d', path)
    .attr('fill', function(country)
        {
            let
            name = country.properties.name

            let
            rating = gameData.find(function(item)
            {
            if (item["Game"] === selectedGame)
            {
            return item;
            }
            });
            let
            rating_by_country = rating["Game"]
            console.log(rating["Average Rating"])
            if (rating_by_country < 5)
            {
            return 'red';
            } else {
            return 'green';
            }
        })