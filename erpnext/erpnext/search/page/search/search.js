frappe.pages['search'].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
	   parent: wrapper,
	   title: 'Rechercher les Doctypes liés à un Doctype cible',
	   single_column: true
	});
	
	const html = `
	<div class="container">
	  <div class="card p-4 shadow-sm mb-4" style="border-radius: 8px; border: 1px solid #eee;">
		<div class="form-group">
		  <label for="doctype_input" class="text-base font-weight-bold mb-2" style="color: #4a5568;">
			<i class="fa fa-database mr-2" style="color: #5e64ff;"></i>Doctype
		  </label>
		  <div id="doctype_field_container" class="mb-3"></div>
		</div>
		<div class="mt-2">
		  <button class="btn btn-primary" id="search_btn" style="background-color: #5e64ff; border-color: #5e64ff; border-radius: 6px; padding: 8px 16px; box-shadow: 0 2px 4px rgba(94, 100, 255, 0.2);">
			<i class="fa fa-search mr-2"></i>Rechercher
		  </button>
		</div>
	  </div>
	  <div id="result_area" style="margin-top: 20px;"></div>
	</div>
	`;
	
	$(page.body).html(html);
	
	// Création du champ auto-complété pour les Doctypes avec style amélioré
	let doctype_field = frappe.ui.form.make_control({
	   df: {
		   fieldtype: 'Link',
		   options: 'DocType',
		   label: 'Doctype',
		   fieldname: 'doctype_input',
		   reqd: 1,
		   description: 'Sélectionnez un DocType pour voir tous les champs qui y font référence',
		   placeholder: 'Rechercher un DocType...'
	   },
	   parent: $('#doctype_field_container'),
	   render_input: true
	});
	
	// Ajouter des styles CSS personnalisés après le rendu
	setTimeout(() => {
	   // Styliser l'input
	   $(doctype_field.$input)
		   .addClass('form-control-lg')
		   .css({
			   'border': '1px solid #ddd',
			   'border-radius': '6px',
			   'padding': '10px 15px',
			   'box-shadow': '0 1px 3px rgba(0,0,0,0.05)',
			   'transition': 'all 0.3s ease'
		   })
		   .on('focus', function() {
			   $(this).css({
				   'border-color': '#5e64ff',
				   'box-shadow': '0 0 0 3px rgba(94, 100, 255, 0.2)'
			   });
		   })
		   .on('blur', function() {
			   $(this).css({
				   'border-color': '#ddd',
				   'box-shadow': '0 1px 3px rgba(0,0,0,0.05)'
			   });
		   });
	   
	   // Styliser la description
	   $('.control-value-description').css({
		   'color': '#718096',
		   'font-style': 'italic',
		   'margin-top': '5px'
	   });
	}, 100);
	
	// Action sur bouton "Rechercher"
	$('#search_btn').on('click', function () {
	   let field_value = doctype_field.get_value();
	   if (!field_value) {
		   frappe.msgprint("Veuillez sélectionner un Doctype.");
		   return;
	   }
	   
	   // Récupérer d'abord les informations sur le module du doctype sélectionné
	   frappe.db.get_value('DocType', field_value, ['module'], function(r) {
		   const doctype_module = r.module;
		   
		   // Ensuite récupérer les relations
		   frappe.call({
			   method: 'erpnext.controllers.search.get_linked_doctypes',
			   args: {
				   field: field_value
			   },
			   callback: function (r) {
				   const area = document.getElementById("result_area");
				   const data = r.message.linked_doctypes;
				   
				   if (data && data.length) {
					   // Collecter les doctypes uniques et récupérer leurs modules
					   const uniqueDoctypes = [...new Set(data.map(item => item.doctype))];
					   
					   // Fonction pour récupérer tous les modules des doctypes
					   const getModules = (doctypes, callback) => {
						   let completed = 0;
						   const moduleInfo = {};
						   
						   // Si aucun doctype à traiter, appeler directement le callback
						   if (doctypes.length === 0) {
							   callback(moduleInfo);
							   return;
						   }
						   
						   // Pour chaque doctype, récupérer son module
						   doctypes.forEach(doctype => {
							   frappe.db.get_value('DocType', doctype, ['module'], function(result) {
								   moduleInfo[doctype] = result.module;
								   completed++;
								   
								   // Une fois tous les modules récupérés, appeler le callback
								   if (completed === doctypes.length) {
									   callback(moduleInfo);
								   }
							   });
						   });
					   };
					   
					   // Récupérer les modules puis afficher les résultats
					   getModules(uniqueDoctypes, (moduleInfo) => {
						   // Ajouter CSS pour le format MCD
						   const styleEl = document.createElement('style');
						   styleEl.innerHTML = `
							   .mcd-container {
								   padding: 20px;
								   margin-top: 20px;
								   overflow: auto;
							   }
							   .mcd-entity {
								   border: 2px solid #5e64ff;
								   border-radius: 8px;
								   background-color: #f8fafc;
								   display: inline-block;
								   margin: 10px;
								   width: 220px;
								   box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
								   position: relative;
							   }
							   .mcd-entity-title {
								   background-color: #5e64ff;
								   color: white;
								   padding: 8px 12px;
								   font-weight: bold;
								   border-top-left-radius: 6px;
								   border-top-right-radius: 6px;
								   text-align: center;
							   }
							   .mcd-entity-content {
								   padding: 10px;
							   }
							   .mcd-field {
								   margin-bottom: 6px;
								   padding: 4px 8px;
								   border-radius: 4px;
								   background-color: #EDF2F7;
							   }
							   .mcd-field-name {
								   font-weight: 500;
								   color: #2D3748;
							   }
							   .mcd-field-label {
								   font-size: 0.85em;
								   color: #718096;
								   display: block;
							   }
							   .mcd-module-badge {
								   display: inline-block;
								   padding: 2px 8px;
								   border-radius: 12px;
								   background-color: #EBF4FF;
								   color: #4C51BF;
								   font-size: 0.8em;
								   margin-top: 5px;
								   margin-bottom: 8px;
								   border: 1px solid #C3DAFE;
							   }
							   .mcd-arrow {
								   position: absolute;
								   z-index: 1;
								   pointer-events: none;
							   }
							   .mcd-description {
								   margin-bottom: 15px;
								   color: #4A5568;
								   padding: 10px;
								   background-color: #EDF2F7;
								   border-radius: 6px;
							   }
							   .mcd-legend {
								   margin-top: 15px;
								   padding: 10px;
								   background-color: #F7FAFC;
								   border-radius: 6px;
								   border-left: 4px solid #5e64ff;
							   }
							   .mcd-target {
								   border-color: #3182CE;
							   }
							   .mcd-target .mcd-entity-title {
								   background-color: #3182CE;
							   }
							   .mcd-entities-container {
								   display: flex;
								   flex-wrap: wrap;
								   justify-content: center;
								   padding: 20px;
							   }
							   .mcd-diagram {
								   position: relative;
								   min-height: 500px;
							   }
						   `;
						   document.head.appendChild(styleEl);
						   
						   let mcdHTML = `
						   <div class="card shadow-sm">
							   <div class="card-header bg-light" style="background-color: #f8fafc;">
								   <h5 class="mb-0">Modèle de Relations (${data.length} référence${data.length > 1 ? 's' : ''} vers ${field_value})</h5>
							   </div>
							   <div class="card-body">
								   <div class="mcd-description">
									   <i class="fa fa-info-circle mr-2" style="color: #3182CE;"></i>
									   Ce diagramme montre tous les doctypes qui référencent <strong>${field_value}</strong> via leurs champs de type Link.
									   <div class="mt-2">
										   <strong>Module:</strong> <span class="mcd-module-badge"><i class="fa fa-cube mr-1"></i>${doctype_module}</span>
									   </div>
								   </div>
								   
								   <div class="mcd-diagram">
									   <!-- Entité cible -->
									   <div class="mcd-entities-container">
										   <div class="mcd-entity mcd-target" id="entity-target">
											   <div class="mcd-entity-title">
												   <i class="fa fa-database mr-2"></i>${field_value}
											   </div>
											   <div class="mcd-entity-content">
												   <div class="text-center mb-2">
													   <span class="mcd-module-badge">
														   <i class="fa fa-cube mr-1"></i>${doctype_module}
													   </span>
												   </div>
												   <div class="text-center text-muted py-2">
													   <i class="fa fa-star mb-2" style="font-size: 1.5em;"></i>
													   <div>Doctype cible</div>
												   </div>
											   </div>
										   </div>
										   
										   <!-- Entités qui référencent la cible -->
										   ${uniqueDoctypes.map(doctype => {
											   const fields = data.filter(item => item.doctype === doctype);
											   const moduleLabel = moduleInfo[doctype] || 'Module inconnu';
											   
											   return `
											   <div class="mcd-entity" id="entity-${doctype.replace(/\s+/g, '-')}">
												   <div class="mcd-entity-title">
													   <i class="fa fa-table mr-2"></i>${doctype}
												   </div>
												   <div class="mcd-entity-content">
													   <div class="text-center mb-2">
														   <span class="mcd-module-badge">
															   <i class="fa fa-cube mr-1"></i>${moduleLabel}
														   </span>
													   </div>
													   ${fields.map(field => `
														   <div class="mcd-field" title="${field.label || 'Champ sans libellé'}">
															   <div class="mcd-field-name">
																   <i class="fa fa-link mr-1" style="color: #5e64ff; font-size: 0.9em;"></i>
																   ${field.fieldname}
															   </div>
															   <div class="mcd-field-label">
																   ${field.label || '<i>sans libellé</i>'}
															   </div>
														   </div>
													   `).join('')}
													   <div class="text-center mt-2">
														   <button class="btn btn-sm btn-light" 
															   onclick="frappe.set_route('Form', '${doctype}')">
															   <i class="fa fa-external-link mr-1"></i> Ouvrir
														   </button>
													   </div>
												   </div>
											   </div>
											   `;
										   }).join('')}
									   </div>
								   </div>
								   
								   <div class="mcd-legend">
									   <div><i class="fa fa-info-circle mr-2"></i> <strong>Légende:</strong></div>
									   <div class="mt-2 ml-3">
										   <div><i class="fa fa-database mr-2" style="color: #3182CE;"></i> Doctype cible</div>
										   <div><i class="fa fa-table mr-2" style="color: #5e64ff;"></i> Doctypes référençant</div>
										   <div><i class="fa fa-link mr-2" style="color: #5e64ff;"></i> Champs de type Link</div>
										   <div><i class="fa fa-cube mr-2" style="color: #4C51BF;"></i> Module</div>
									   </div>
								   </div>
							   </div>
						   </div>`;
						   
						   area.innerHTML = mcdHTML;
						   
						   // Dessiner les flèches après le rendu pour obtenir les positions correctes
						   setTimeout(() => {
							   // Code pour dessiner des connexions visuelles entre les entités
							   const jsPlumb = window.jsPlumb;
							   if (jsPlumb) {
								   jsPlumb.ready(function() {
									   const instance = jsPlumb.getInstance({
										   PaintStyle: { 
											   stroke: "#5e64ff", 
											   strokeWidth: 2 
										   },
										   Connector: ["Flowchart", { cornerRadius: 5 }],
										   Endpoint: ["Dot", { radius: 3 }],
										   EndpointStyle: { fill: "#5e64ff" },
										   Anchors: ["Right", "Left"]
									   });
									   
									   uniqueDoctypes.forEach(doctype => {
										   instance.connect({
											   source: `entity-${doctype.replace(/\s+/g, '-')}`,
											   target: "entity-target",
											   overlays: [
												   ["Arrow", { location: 1, width: 12, length: 12 }],
												   ["Label", { 
													   label: "référence", 
													   cssClass: "connection-label",
													   location: 0.5
												   }]
											   ]
										   });
									   });
								   });
							   } else {
								   // Si jsPlumb n'est pas disponible, utiliser une mise en page en cercle simple
								   const targetEl = document.getElementById('entity-target');
								   if (targetEl) {
									   targetEl.style.margin = '0 auto 30px auto';
								   }
							   }
						   }, 500);
					   });
				   } else {
					   // Afficher un message pour aucune relation trouvée
					   frappe.db.get_value('DocType', field_value, ['module'], function(r) {
						   const doctype_module = r.module || 'Module inconnu';
						   
						   area.innerHTML = `
						   <div class="card shadow-sm">
							   <div class="card-header bg-light" style="background-color: #f8fafc;">
								   <h5 class="mb-0">Modèle de Relations</h5>
							   </div>
							   <div class="card-body">
								   <div class="mcd-description mb-4">
									   <div>
										   <i class="fa fa-info-circle mr-2" style="color: #3182CE;"></i>
										   Informations sur <strong>${field_value}</strong>:
									   </div>
									   <div class="mt-2 ml-3">
										   <strong>Module:</strong> <span class="mcd-module-badge"><i class="fa fa-cube mr-1"></i>${doctype_module}</span>
									   </div>
								   </div>
								   <div class="text-center py-4">
									   <div class="mb-3">
										   <i class="fa fa-sitemap" style="font-size: 3em; color: #cbd5e0;"></i>
									   </div>
									   <h4 class="text-muted mb-2">Aucune relation trouvée</h4>
									   <p class="text-muted">Aucun champ ne pointe vers <b>${field_value}</b>.</p>
								   </div>
							   </div>
						   </div>`;
					   });
				   }
			   }
		   });
	   });
	});
};