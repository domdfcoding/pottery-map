// TODO: nice animation when closing bottom sheet, not just disappear

class PopupOrBottomSheet {
	constructor(marker, content, popup) {
		this.marker = marker;
		this.content = content;
		this.popup = popup;

		this.breakpoint = 500; // px

		this.popup.setContent(`<div class="item-details">${this.content}</div>`);

		addEventListener('resize', (event) => {
			this.switch();
		});
	}

	openBottomSheet() {
		// TODO: dismiss any tooltips
		L.setBottomSheetContent(this.content);

		Array.prototype.forEach.call(document.getElementsByClassName('marker-highlight'), (m) => {
			m.classList.remove('marker-highlight');
		});
		bottomSheetDialog.show();
		bottomSheetContent.shadowRoot.querySelector('.sheet-content').scroll({ top: 0 });
		const el = this.marker.getElement();
		if (el != undefined) {
			el.classList.add('marker-highlight');
			bottomSheetDialog.addEventListener('close', (event) => {
				el.classList.remove('marker-highlight'), { once: true };
			});
		}
	}

	enableBottomSheet() {
		this.marker.unbindPopup(this.popup);
		this.marker.on('click', this.openBottomSheet, this);
	}

	enablePopup() {
		this.marker.bindPopup(this.popup);
		this.marker.off('click', this.openBottomSheet, this);
	}

	switch() {
		if (window.innerWidth < this.breakpoint) {
			this.enableBottomSheet();
		} else {
			this.enablePopup();
		}
	}

	show() {
		if (window.innerWidth < this.breakpoint) {
			this.openBottomSheet();
		} else {
			this.marker.openPopup();
		}
	}
}

function PopupResizeMonitor(map) {
	let lastWidth = window.innerWidth;

	function onResize() {
		console.log('Width was', lastWidth, 'now', window.innerWidth);

		if (lastWidth > 500 && window.innerWidth <= 500) {
			map.closePopup();
			// TODO: reopen if it was open  map.openPopup(...);
		} else if (lastWidth <= 500 && window.innerWidth > 500) {
			document.getElementById('bottomSheetDialog').close();
		}

		lastWidth = window.innerWidth;
	}

	window.addEventListener('resize', onResize);
}
