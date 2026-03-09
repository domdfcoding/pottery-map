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

const pie_chart_layout_option = {
	padding: {
		left: 32,
		right: 32,
		bottom: 32,
	},
};

function formatLabel(value, ctx) {
	return ctx.chart.data.labels[ctx.dataIndex];
}

function formatTooltip(context) {
	let total_value = context.dataset.data.reduce(
		(accumulator, currentValue) => accumulator + currentValue,
		0,
	);

	let value = context.parsed;

	let label = ' ';
	label += value;
	label += ' ';

	if (label > 1) {
		label += context.chart.options.countTypePlural ?? 'items';
	} else {
		label += context.chart.options.countType ?? 'item';
	}

	label += ' (';
	label += (value / total_value).toFixed(2);
	label += '%)';
	return label;
}

const pie_datalabels_options = {
	textStrokeColor: 'black',
	textStrokeWidth: 2,
	color: '#fff',
	font: {
		weight: 'bold',
		size: 14,
	},
	display: function(context) {
		var dataset = context.dataset;
		var value = dataset.data[context.dataIndex];
		return value > 1;
	},
};

const pie_rich_datalabels_options = {
	color: 'black',
	font: {
		weight: 'bold',
		size: 14,
	},

	labels: {
		'label': {
			anchor: 'end',
			formatter: formatLabel,
			borderColor: function(context) {
				return context.dataset.backgroundColor;
			},
			backgroundColor: 'white',
			borderRadius: 25,
			borderWidth: 2,
		},
		'value': {
			textStrokeColor: 'black',
			textStrokeWidth: 3,
			color: '#fff',
			font: {
				weight: 'bold',
				size: 16,
			},
		},
	},

	padding: 6,
};

const pie_chart_tooltip_options = {
	enabled: true,
	callbacks: {
		title: (context) => {
			return context[0].label;
		},
		label: formatTooltip,
	},
	titleFont: {
		weight: 'bold',
		size: 14,
	},
	bodyFont: {
		size: 14,
	},
};

const groups_pie_chart_options = {
	plugins: {
		tooltip: pie_chart_tooltip_options,
		title: {
			display: true,
			font: {
				size: 16,
			},
			color: 'black',
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
		legend: { display: false },
		title: {
			display: true,
			font: {
				size: 16,
			},
			color: 'black',
			text: 'Companies',
		},
	},
};

const materials_pie_chart_options = {
	plugins: {
		tooltip: pie_chart_tooltip_options,
		title: {
			display: true,
			font: {
				size: 16,
			},
			color: 'black',
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
		legend: { display: false },
		title: {
			display: true,
			font: {
				size: 16,
			},
			color: 'black',
			text: 'Item Types',
		},
	},
};

const areas_pie_chart_options = {
	countType: 'factory',
	countTypePlural: 'factories',
	plugins: {
		legend: { display: false },
		tooltip: pie_chart_tooltip_options,
		title: {
			display: true,
			font: {
				size: 16,
			},
			color: 'black',
			text: 'Areas',
		},
		datalabels: pie_rich_datalabels_options,
	},
	layout: pie_chart_layout_option,
};

const categories_pie_chart_options = {
	plugins: {
		legend: { display: false },
		tooltip: pie_chart_tooltip_options,
		title: {
			display: true,
			font: {
				size: 16,
			},
			color: 'black',
			text: 'Categories',
		},
		datalabels: pie_rich_datalabels_options,
	},
	layout: pie_chart_layout_option,
};

var groups_pie_chart_ctx = document.getElementById('groups-pie-chart').getContext('2d');
var groups_pie_chart = new Chart(groups_pie_chart_ctx, {
	type: 'doughnut',
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
	type: 'doughnut',
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

var areas_pie_chart_ctx = document.getElementById('areas-pie-chart').getContext('2d');
var areas_pie_chart = new Chart(areas_pie_chart_ctx, {
	type: 'doughnut',
	data: areas_pie_chart_data,
	options: areas_pie_chart_options,
	plugins: [ChartDataLabels],
});

var categories_pie_chart_ctx = document.getElementById('categories-pie-chart').getContext('2d');
var categories_pie_chart = new Chart(categories_pie_chart_ctx, {
	type: 'doughnut',
	data: categories_pie_chart_data,
	options: categories_pie_chart_options,
	plugins: [ChartDataLabels],
});
