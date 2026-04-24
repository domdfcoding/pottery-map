const fuzzySearchItems = createFuzzySearch([...document.querySelectorAll('div.item[data-item-name]')], {
	getText: (item) => [item.dataset.itemName],
});

function filterItems(query) {
	// console.log("Search query:", query);
	// console.log("Results:", fuzzySearchItems(query))
	let results = [];

	if (query !== '') {
		fuzzySearchItems(query).forEach((item) => {
			const div = item.item;
			results.push(div);
		});
	}

	document.querySelectorAll('div.item[data-item-name]').forEach((div) => {
		if (query === '' || results.includes(div)) {
			div.classList.remove('d-none');
		} else {
			div.classList.add('d-none');
		}
	});
}

function setupItemSearch() {
	itemsSearch.addEventListener('input', (e) => {
		filterItems(itemsSearch.value);
	});
	itemsSearchForm.addEventListener('reset', (e) => {
		console.log('Form reset');
		document.querySelectorAll('div.item[data-item-name]').forEach((div) => {
			div.classList.remove('d-none');
		});
	});

	if (itemsSearch.value !== '') {
		filterItems(itemsSearch.value);
	}
}

setupItemSearch();
