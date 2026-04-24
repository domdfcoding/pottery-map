const toggleButton = document.getElementById('toggle-btn');
const sidebar = document.getElementById('sidebar');

function updateQueryStringParam(key, value) {
	const url = new URL(window.location.href);
	url.searchParams.set(key, value.toString()); // Add or update the parameter
	// window.history.pushState({}, null, url);
	window.history.replaceState({}, '', url);
}

function deleteQueryStringParam(key) {
	const url = new URL(window.location.href);
	url.searchParams.delete(key);
	// window.history.pushState({}, null, url);
	window.history.replaceState({}, '', url);
}

function getCompanyName(li) {
	return li.dataset.company;
}

const fuzzySearch = createFuzzySearch([...companiesMenu.querySelectorAll('li[data-company]')], {
	getText: (item) => [getCompanyName(item)],
});

function filterCompanies(query) {
	// console.log("Search query:", query);
	// console.log("Results:", fuzzySearch(query))
	let results = [];
	fuzzySearch(query).forEach((item) => {
		const li = item.item;
		results.push(li);
	});

	companiesMenu.querySelectorAll('li[data-company]').forEach((li) => {
		if (results.includes(li)) {
			li.classList.remove('d-none');
		} else {
			li.classList.add('d-none');
		}
	});
}

function setupSidebar() {
	const url = new URL(window.location.href);

	let showSidebar = 0;
	if (url.searchParams.has('sidebar')) {
		showSidebar = parseInt(url.searchParams.get('sidebar'));
	}

	if (showSidebar === 1) {
		sidebar.classList.remove('close');
	}

	if (sidebar.classList.contains('close')) {
		toggleButton.classList.add('rotate');
	} else {
		toggleButton.classList.remove('rotate');
	}

	if (url.searchParams.has('sidebar_expand')) {
		const sectionTitle = url.searchParams.get('sidebar_expand');
		toggleSubMenu(document.querySelector(`a[title=${sectionTitle}]`));
	}

	companiesSearch.addEventListener('input', (e) => {
		filterCompanies(companiesSearch.value);
	});
	companiesSearchForm.addEventListener('reset', (e) => {
		console.log('Form reset');
		companiesMenu.querySelectorAll('li[data-company]').forEach((li) => {
			li.classList.remove('d-none');
		});
	});

	if (companiesSearch.value !== '') {
		filterCompanies(companiesSearch.value);
	}
}

function toggleSidebar() {
	sidebar.classList.toggle('close');
	toggleButton.classList.toggle('rotate');

	if (sidebar.classList.contains('close')) {
		deleteQueryStringParam('sidebar_expand');
		deleteQueryStringParam('sidebar');
	} else {
		updateQueryStringParam('sidebar', 1);
	}

	closeAllSubMenus();
}

function toggleSubMenu(button) {
	if (!button.nextElementSibling.classList.contains('show')) {
		closeAllSubMenus();
	}

	button.nextElementSibling.classList.toggle('show');
	button.classList.toggle('rotate');

	if (sidebar.classList.contains('close')) {
		sidebar.classList.toggle('close');
		toggleButton.classList.toggle('rotate');
	}

	if (button.nextElementSibling.classList.contains('show')) {
		updateQueryStringParam('sidebar_expand', button.title);
	} else {
		deleteQueryStringParam('sidebar_expand');
	}
}

function closeAllSubMenus() {
	Array.from(sidebar.getElementsByClassName('show')).forEach((ul) => {
		ul.classList.remove('show');
		ul.previousElementSibling.classList.remove('rotate');
	});
}

setupSidebar();
