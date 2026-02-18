//
//  dashboard.js
/*
Dashboard charts.
*/
//
//  Copyright © 2026 Dominic Davis-Foster <dominic@davis-foster.co.uk>
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy
//  of this software and associated documentation files (the "Software"), to deal
//  in the Software without restriction, including without limitation the rights
//  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
//  copies of the Software, and to permit persons to whom the Software is
//  furnished to do so, subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in all
//  copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
//  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
//  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
//  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
//  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
//  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
//  OR OTHER DEALINGS IN THE SOFTWARE.
//

const pie_datalabels_options = {
	formatter: (value, ctx) => {
		const datapoints = ctx.chart.data.datasets[0].data;
		const total = datapoints.reduce((total, datapoint) => total + datapoint, 0);
		const percentage = (value / total) * 100;
		return percentage.toFixed(2) + '%';
	},
	textStrokeColor: 'black',
	textStrokeWidth: 2,
	color: '#fff',
	font: {
		weight: 'bold',
		size: 14,
	},
};

const groups_pie_chart_options = {
	tooltips: {
		enabled: false,
	},

	plugins: {
		title: {
			display: true,
			text: 'Company Groups',
		},
		datalabels: pie_datalabels_options,
	},
};

const companies_bar_chart_options = {
	maintainAspectRatio: false,
	aspectRatio: 1,
	responsive: true,
	indexAxis: 'y',
	scales: {
		y: {
			beginAtZero: true,
			ticks: {
				autoSkip: false,
				stepSize: 1,
			},
		},
	},
	plugins: {
		legend: {
			display: false,
		},
		title: {
			display: true,
			text: 'Companies',
		},
	},
};

const materials_pie_chart_options = {
	tooltips: {
		enabled: false,
	},

	plugins: {
		title: {
			display: true,
			text: 'Materials',
		},
		datalabels: pie_datalabels_options,
	},
};

const types_bar_chart_options = {
	maintainAspectRatio: false,
	aspectRatio: 1,
	responsive: true,
	indexAxis: 'y',
	scales: {
		y: {
			beginAtZero: true,
			ticks: {
				autoSkip: false,
				stepSize: 1,
			},
		},
	},
	plugins: {
		legend: {
			display: false,
		},
		title: {
			display: true,
			text: 'Item Types',
		},
	},
};

var groups_pie_chart_ctx = document.getElementById('groups-pie-chart').getContext('2d');
var groups_pie_chart = new Chart(groups_pie_chart_ctx, {
	type: 'pie',
	data: groups_pie_chart_data,
	options: groups_pie_chart_options,
	plugins: [ChartDataLabels],
});

var companies_bar_chart_ctx = document.getElementById('companies-bar-chart').getContext('2d');
var companies_bar_chart = new Chart(companies_bar_chart_ctx, {
	type: 'bar',
	data: companies_bar_chart_data,
	options: companies_bar_chart_options,
});

var materials_pie_chart_ctx = document.getElementById('materials-pie-chart').getContext('2d');
var materials_pie_chart = new Chart(materials_pie_chart_ctx, {
	type: 'pie',
	data: materials_pie_chart_data,
	options: materials_pie_chart_options,
	plugins: [ChartDataLabels],
});

var types_bar_chart_ctx = document.getElementById('types-bar-chart').getContext('2d');
var types_bar_chart = new Chart(types_bar_chart_ctx, {
	type: 'bar',
	data: types_bar_chart_data,
	options: types_bar_chart_options,
});
