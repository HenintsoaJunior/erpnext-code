frappe.pages['success'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'DONNEE EFFACER',
		single_column: true
	});

	// Ajouter le H1 avec animation
	$(wrapper).html(`
		<style>
			.center-container {
				display: flex;
				justify-content: center;
				align-items: center;
				height: 80vh;
				text-align: center;
			}
			.typewriter h1 {
				overflow: hidden;
				border-right: .15em solid orange;
				white-space: nowrap;
				margin: 0 auto;
				letter-spacing: .15em;
				animation: typing 3.5s steps(30, end), blink-caret .75s step-end infinite;
				font-size: 3em;
			}

			@keyframes typing {
				from { width: 0 }
				to { width: 100% }
			}

			@keyframes blink-caret {
				from, to { border-color: transparent }
				50% { border-color: orange; }
			}
		</style>

		<div class="center-container">
			<div class="typewriter">
				<h1>DONNEE EFFACER</h1>
			</div>
		</div>
	`);
}
