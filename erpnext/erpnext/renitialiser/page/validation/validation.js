frappe.pages['validation'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Validation',
        single_column: true
    });

    let message = $('<div style="text-align: center; margin: 20px;"><h4>Voulez-vous vraiment réinitialiser les donnee ?</h4></div>').appendTo(page.body);

    let button_container = $('<div style="text-align: center; margin-top: 20px;"></div>').appendTo(page.body);

    $('<button class="btn btn-primary btn-sm" style="margin-right: 10px;">Valider</button>')
        .appendTo(button_container)
        .click(function() {
            window.location.href = 'http://erpnext.localhost:8000/api/method/erpnext.controllers.data.database_reset_controller.reset_specific_doctypes';
        });

    // Ajouter le bouton Annuler
    $('<button class="btn btn-default btn-sm">Annuler</button>')
        .appendTo(button_container)
        .click(function() {
            frappe.set_route('/');
        });
}