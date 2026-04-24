const toggleButton = document.getElementById('toggle-btn');
const sidebar = document.getElementById('sidebar');

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
	if (sidebar.classList.contains('close')) {
		toggleButton.classList.add('rotate');
	} else {
		toggleButton.classList.remove('rotate');
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
}

function closeAllSubMenus() {
	Array.from(sidebar.getElementsByClassName('show')).forEach((ul) => {
		ul.classList.remove('show');
		ul.previousElementSibling.classList.remove('rotate');
	});
}

setupSidebar();
