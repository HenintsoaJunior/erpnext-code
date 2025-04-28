frappe.pages['test1'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'test1',
        single_column: true
    });

    // Créer un conteneur pour le formulaire
    $(wrapper).find('.layout-main-section').append(`
        <form id="test1-form" class="form">
            <div class="form-group">
                <label for="field1">Nom :</label>
                <input type="text" id="field1" class="form-control" placeholder="Entrez votre nom">
            </div>
            <div class="form-group">
                <label for="field2">Email :</label>
                <input type="email" id="field2" class="form-control" placeholder="Entrez votre email">
            </div>
            <button type="submit" class="btn btn-primary">Envoyer</button>
        </form>
    `);

    // Ajouter un comportement lors de la soumission
    $('#test1-form').on('submit', function(e) {
        e.preventDefault();
        var nom = $('#field1').val();
        var email = $('#field2').val();
        frappe.msgprint('Formulaire envoyé !<br>Nom : ' + nom + '<br>Email : ' + email);
    });
}
