document.addEventListener("DOMContentLoaded", function() {
	const modal = new bootstrap.Modal(document.getElementById('infoModal'));

	var data = document.getElementById("divD3BarChart").getAttribute("data-value");
	var data = data.replace(/'/g, '"');

	var data = JSON.parse(data);

	var passers_per_day_2023 = document.getElementById("infoModal").getAttribute("data-value");
	var passers_per_day_2023 = passers_per_day_2023.replace(/'/g, '"');

	var passers_per_day_2023 = JSON.parse(passers_per_day_2023);

	const maxScore = d3.max(data, d => d.Passers);

	const width = 800;
	const height = 400;
	const margin = { top: 10, bottom: 45, left: 100, right: 80}

	const svg = d3.select('#d3-container')
		.append('svg')
		.attr('height', height - margin.top - margin.bottom)
		.attr('width', width - margin.left - margin.right)
		.attr('viewBox', [0, 0, width, height]);

	const x = d3.scaleBand ()
		.domain(d3.range(data.length))
		.range([margin.left, width - margin.right]) 
		.padding(0.1);

	const y = d3.scaleLinear()
		.domain([0, maxScore])
		.range([height - margin.bottom, margin.top]);

	const colorScale = d3.scaleOrdinal()
		.domain(data.map((d, i) => i))
		.range(d3.schemeCategory10);

	let tooltip = d3.select("body")
		.append("div")
		.style("position", "absolute")
		.style("z-index", "10")
		.style("visibility", "hidden")
		.style("background", "black")
		.style("color", "white")

		.style("border-radius", "5px")
		.style("padding", "10px");


	svg
		.append('g')
		.selectAll('rect')
		.data(data.sort((a, b) => d3.descending(a.Passers, b.Passers)))
		.join('rect')
			.attr('x', (d, i) => x(i))
			.attr('y', (d) => y(d.Passers))
			.attr('height', d => y(0) - y(d.Passers))
			.attr('width', x.bandwidth())
			.attr('fill', (d, i) => colorScale(i))
			.attr('class', 'rectangle')
		.on('click', function(d) {

			console.log("Bar clicked! Data:", d);

            // Call the createGraph function with the clicked bar's Area value
    		const graphSvg = createGraph(passers_per_day_2023, d.Area);

			// Append the created graph to the modal body
			document.querySelector('#infoModal .modal-body').innerHTML = '';
			document.querySelector('#infoModal .modal-body').appendChild(graphSvg);

			const modalInstance = new bootstrap.Modal(document.getElementById('infoModal'));
			modalInstance.show();
		})
		.on('mouseover', function(d, i) {
			tooltip.text(`${d.Area}: ${d.Passers}`);
			return tooltip.style("visibility", "visible");
		})
		.on('mousemove', function(d) {
			return tooltip.style("top", (d3.event.pageY - 10) + "px").style("left", (d3.event.pageX + 10) + "px");
		})
		.on('mouseout', function(d) {
			return tooltip.style("visibility", "hidden");
		});

	function xAxis(g) {
		g.attr('transform', `translate(0, ${height - margin.bottom})`)
		.call(d3.axisBottom(x).tickFormat(i=>data[i].Area))
		.attr('font-size', '16px')
	};

	function yAxis(g) {
		g.attr('transform', `translate(${margin.left}, 0)`)
		.call(d3.axisLeft(y).ticks (null, data.format)) 
		.attr('font-size', '16px')
	}

	svg.append('g').call(yAxis); 
	svg.append('g').call(xAxis);
	svg.node();
});

function createGraph(data, areaValue) {

	const filteredData = data.filter(d => d.Area === areaValue);
	// Specify the chart’s dimensions.
	const width = 900;
	const height = 530;
	const marginTop = 10;
	const marginRight = 30;
	const marginBottom = 20;
	const marginLeft = 50;

	// Create the horizontal (x) scale for DateHour.
	const x = d3.scaleTime() // Use scaleTime for dates
		.domain(d3.extent(filteredData, d => new Date(d["DateHour"]))) // Convert string to Date object
		.range([marginLeft, width - marginRight]);

	// Create the vertical (y) scale for Passers.
	const y = d3.scaleLinear()
		.domain([0, d3.max(filteredData, d => d["Passers"])]).nice()
		.range([height - marginBottom, marginTop]);

	// Create the SVG container.
	const svg = d3.create("svg")
		.attr("viewBox", [0, 0, width, height])
		.property("value", []);

	// Append the axes.
	svg.append("g")
		.attr("transform", `translate(0,${height - marginBottom})`)
		.call(d3.axisBottom(x))
		.call(g => g.select(".domain").remove())
		.call(g => g.append("text")
			.attr("x", width - marginRight)
			.attr("y", -4)
			.attr("fill", "#000")
			.attr("font-weight", "bold")
			.attr("text-anchor", "end")
			.text("DateHour"));

	svg.append("g")
		.attr("transform", `translate(${marginLeft},0)`)
		.call(d3.axisLeft(y))
		.call(g => g.select(".domain").remove())
		.call(g => g.select(".tick:last-of-type text").clone()
			.attr("x", 4)
			.attr("text-anchor", "start")
			.attr("font-weight", "bold")
			.text("Passers"));

	// Append the dots.
	const dot = svg.append("g")
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        .selectAll("circle")
        .data(filteredData)
        .join("circle")
        .attr("transform", d => `translate(${x(new Date(d["DateHour"]))},${y(d["Passers"])})`)
        .attr("r", 3)
        .on('mouseover', function(d, i) {
            tooltip.text(`${d.DateHour}: ${d.Passers}`);
            return tooltip.style("visibility", "visible");
        })
        .on('mousemove', function(d) {
            return tooltip.style("top", (d3.event.pageY - 10) + "px").style("left", (d3.event.pageX + 10) + "px");
        })
        .on('mouseout', function(d) {
            return tooltip.style("visibility", "hidden");
        });

	// Create the brush behavior.
	svg.call(d3.brush().on("start brush end", ({selection}) => {
	let value = [];
	if (selection) {
		const [[x0, y0], [x1, y1]] = selection;
		value = dot
		.style("stroke", "gray")
		.filter(d => x0 <= x(new Date(d["DateHour"])) && x(new Date(d["DateHour"])) < x1
				&& y0 <= y(d["Passers"]) && y(d["Passers"]) < y1)
		.style("stroke", "steelblue")
		.data();
	} else {
		dot.style("stroke", "steelblue");
	}

	// Inform downstream cells that the selection has changed.
	svg.property("value", value).dispatch("input");
	}));

	return svg.node();
}