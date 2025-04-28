frappe.pages['importdata'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'IMPORT DATA',
        single_column: true
    });

    // Inject custom CSS for black and white theme
    $('<style>')
        .html(`
            .import-container {
                max-width: 800px;
                margin: 30px auto;
                background-color: #fff;
                border-radius: 10px;
                box-shadow: 0 5px 30px rgba(0, 0, 0, 0.15);
                padding: 30px;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            
            .import-header {
                margin-bottom: 30px;
                text-align: center;
                border-bottom: 1px solid #eee;
                padding-bottom: 20px;
            }
            
            .import-header h2 {
                font-weight: 600;
                color: #000;
                margin-bottom: 10px;
                font-size: 24px;
            }
            
            .import-header p {
                color: #666;
                font-size: 14px;
            }
            
            .form-group {
                margin-bottom: 25px;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 500;
                color: #333;
                font-size: 14px;
            }
            
            .file-input-container {
                position: relative;
                border: 2px dashed #ddd;
                border-radius: 6px;
                padding: 28px 15px;
                text-align: center;
                transition: all 0.3s;
                background-color: #fafafa;
            }
            
            .file-input-container:hover {
                border-color: #bbb;
                background-color: #f5f5f5;
            }
            
            .file-input-container input[type="file"] {
                position: absolute;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                opacity: 0;
                cursor: pointer;
            }
            
            .file-placeholder {
                color: #999;
                font-size: 14px;
            }
            
            .file-placeholder i {
                font-size: 24px;
                margin-bottom: 8px;
                display: block;
            }
            
            .file-placeholder.file-selected {
                color: #333;
            }
            
            .btn-import {
                background-color: #000;
                border: none;
                color: #fff;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: 500;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.3s;
                width: 100%;
                margin-top: 10px;
            }
            
            .btn-import:hover {
                background-color: #333;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            }
            
            .btn-import:disabled {
                background-color: #ccc;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            
            .import-result {
                margin-top: 30px;
            }
            
            .alert {
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 15px;
                border-left: 5px solid;
            }
            
            .alert-info {
                background-color: #f8f9fa;
                border-left-color: #0dcaf0;
                color: #055160;
            }
            
            .alert-success {
                background-color: #f8f9fa;
                border-left-color: #198754;
                color: #0f5132;
            }
            
            .alert-danger {
                background-color: #f8f9fa;
                border-left-color: #dc3545;
                color: #842029;
            }
            
            .validation-errors {
                margin-top: 15px;
            }
            
            .file-error-group {
                margin-bottom: 25px;
            }
            
            .file-error-group h5 {
                margin-bottom: 12px;
                font-weight: 600;
                font-size: 15px;
                color: #333;
            }
            
            .error-table {
                width: 100%;
                border-collapse: collapse;
                border: 1px solid #eee;
                font-size: 13px;
            }
            
            .error-table th {
                background-color: #f8f8f8;
                padding: 10px;
                text-align: left;
                font-weight: 600;
                color: #333;
                border-bottom: 2px solid #ddd;
            }
            
            .error-table td {
                padding: 10px;
                border-bottom: 1px solid #eee;
                color: #555;
            }
            
            .error-table tr:nth-child(even) {
                background-color: #fafafa;
            }
            
            .error-table tr:hover {
                background-color: #f5f5f5;
            }
            
            .file-name {
                display: inline-block;
                max-width: 200px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                vertical-align: middle;
                font-size: 13px;
                color: #333;
                margin-left: 10px;
            }
        `)
        .appendTo('head');

    // HTML form avec deux champs de type file
    $(wrapper).find('.layout-main-section').html(`
        <div class="import-container">
            <div class="import-header">
                <h2>Import de Données</h2>
                <p>Sélectionnez les fichiers CSV à importer dans le système</p>
            </div>
            <form id="import-form">
                <div class="form-group">
                    <label for="csv-file-1">Fichier CSV 1</label>
                    <div class="file-input-container">
                        <input type="file" id="csv-file-1" accept=".csv" required>
                        <div class="file-placeholder" id="placeholder-1">
                            <i class="fa fa-file-csv"></i>
                            Cliquez ou glissez le fichier CSV ici
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label for="csv-file-2">Fichier CSV 2</label>
                    <div class="file-input-container">
                        <input type="file" id="csv-file-2" accept=".csv" required>
                        <div class="file-placeholder" id="placeholder-2">
                            <i class="fa fa-file-csv"></i>
                            Cliquez ou glissez le fichier CSV ici
                        </div>
                    </div>
                </div>
                <button type="submit" id="import-button" class="btn-import">Importer les Données</button>
            </form>
            <div id="import-result" class="import-result"></div>
        </div>
    `);

    // Update file placeholders when files are selected
    $('#csv-file-1').on('change', function() {
        const fileName = this.files[0] ? this.files[0].name : null;
        if (fileName) {
            $('#placeholder-1').addClass('file-selected').html(`
                <i class="fa fa-file-csv"></i>
                <span class="file-name">${fileName}</span>
            `);
        } else {
            $('#placeholder-1').removeClass('file-selected').html(`
                <i class="fa fa-file-csv"></i>
                Cliquez ou glissez le fichier CSV ici
            `);
        }
    });

    $('#csv-file-2').on('change', function() {
        const fileName = this.files[0] ? this.files[0].name : null;
        if (fileName) {
            $('#placeholder-2').addClass('file-selected').html(`
                <i class="fa fa-file-csv"></i>
                <span class="file-name">${fileName}</span>
            `);
        } else {
            $('#placeholder-2').removeClass('file-selected').html(`
                <i class="fa fa-file-csv"></i>
                Cliquez ou glissez le fichier CSV ici
            `);
        }
    });

    // Debug CSRF token availability
    if (!frappe.csrf_token) {
        console.error("CSRF token is not available. Ensure you are logged in and the page is loaded in an authenticated context.");
        $('#import-result').html(`<div class="alert alert-danger">Erreur : CSRF token non disponible. Veuillez vous reconnecter.</div>`);
        return;
    }
    console.log("CSRF token:", frappe.csrf_token);

    // Handle form submission
    $('#import-form').on('submit', function(e) {
        e.preventDefault();

        const fileInput1 = $('#csv-file-1')[0].files[0];
        const fileInput2 = $('#csv-file-2')[0].files[0];

        // Validate inputs
        if (!fileInput1 || !fileInput2) {
            $('#import-result').html(`<div class="alert alert-danger">Veuillez sélectionner les deux fichiers CSV.</div>`);
            return;
        }

        // Validate file size (optional, max 10MB per file)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (fileInput1.size > maxSize || fileInput2.size > maxSize) {
            $('#import-result').html(`<div class="alert alert-danger">La taille d'un fichier dépasse la limite autorisée de 10MB.</div>`);
            return;
        }

        // Function to upload a file and return a promise
        function uploadFile(file) {
            return new Promise((resolve, reject) => {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('is_private', 0);

                $.ajax({
                    url: '/api/method/upload_file',
                    type: 'POST',
                    data: formData,
                    processData: false,
                    contentType: false,
                    headers: {
                        'X-Frappe-CSRF-Token': frappe.csrf_token
                    },
                    success: function(response) {
                        if (response.message && response.message.name) {
                            resolve({
                                id: response.message.name,
                                name: file.name
                            });
                        } else {
                            reject("File upload failed");
                        }
                    },
                    error: function(err) {
                        reject(err);
                    }
                });
            });
        }

        // Show loader
        $('#import-result').html(`
            <div class="alert alert-info">
                <div style="display: flex; align-items: center;">
                    <div style="margin-right: 15px;">
                        <i class="fa fa-spinner fa-spin" style="font-size: 20px;"></i>
                    </div>
                    <div>
                        Téléchargement des fichiers en cours...
                    </div>
                </div>
            </div>
        `);
        $('#import-button').prop('disabled', true);

        // Upload both files
        Promise.all([uploadFile(fileInput1), uploadFile(fileInput2)])
            .then(fileResults => {
                const fileIds = {
                    "input1": fileResults[0].id,
                    "input2": fileResults[1].id
                };
                
                // Store file names for reference
                const fileNames = {
                    "input1": fileResults[0].name,
                    "input2": fileResults[1].name
                };
                
                console.log("Files uploaded successfully, fileIds:", fileIds);
                console.log("File names:", fileNames);
                
                $('#import-result').html(`
                    <div class="alert alert-info">
                        <div style="display: flex; align-items: center;">
                            <div style="margin-right: 15px;">
                                <i class="fa fa-spinner fa-spin" style="font-size: 20px;"></i>
                            </div>
                            <div>
                                Import des données en cours...
                            </div>
                        </div>
                    </div>
                `);

                // Call the import controller with both file IDs
                frappe.call({
                    method: 'erpnext.controllers.data.ImportController.import_csv_files',
                    args: {
                        files_data: JSON.stringify(fileIds)
                    },
                    freeze: true,
                    btn: $('#import-button'),
                    callback: function(r) {
                        console.log("Import response:", r);
                        if (r.message && r.message.status === 'success') {
                            $('#import-result').html(`
                                <div class="alert alert-success">
                                    <div style="display: flex; align-items: center;">
                                        <div style="margin-right: 15px;">
                                            <i class="fa fa-check-circle" style="font-size: 20px;"></i>
                                        </div>
                                        <div>${r.message.data.message}</div>
                                    </div>
                                </div>
                            `);
                        } else {
                            displayErrors(r.message, fileNames);
                        }
                        $('#import-button').prop('disabled', false);
                    },
                    error: function(err) {
                        console.error("Import error:", err);
                        $('#import-result').html(`
                            <div class="alert alert-danger">
                                <div style="display: flex; align-items: center;">
                                    <div style="margin-right: 15px;">
                                        <i class="fa fa-exclamation-circle" style="font-size: 20px;"></i>
                                    </div>
                                    <div>Erreur serveur: ${err.responseText || "Une erreur inconnue s'est produite"}</div>
                                </div>
                            </div>
                        `);
                        $('#import-button').prop('disabled', false);
                    }
                });
            })
            .catch(error => {
                console.error("File upload error:", error);
                $('#import-result').html(`
                    <div class="alert alert-danger">
                        <div style="display: flex; align-items: center;">
                            <div style="margin-right: 15px;">
                                <i class="fa fa-exclamation-circle" style="font-size: 20px;"></i>
                            </div>
                            <div>Erreur lors du téléchargement des fichiers</div>
                        </div>
                    </div>
                `);
                $('#import-button').prop('disabled', false);
            });
    });
    
    // Function to display errors in a structured way
    function displayErrors(message, fileNames) {
        if (!message || !message.errors) {
            $('#import-result').html(`
                <div class="alert alert-danger">
                    <div style="display: flex; align-items: center;">
                        <div style="margin-right: 15px;">
                            <i class="fa fa-exclamation-circle" style="font-size: 20px;"></i>
                        </div>
                        <div>Erreur inconnue lors de l'importation</div>
                    </div>
                </div>
            `);
            return;
        }
        
        let errorHtml = `
            <div class="alert alert-danger">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="margin-right: 15px;">
                        <i class="fa fa-exclamation-triangle" style="font-size: 20px;"></i>
                    </div>
                    <div>
                        <h4 style="margin: 0; font-size: 16px; font-weight: 600;">Erreurs d'importation détectées</h4>
                    </div>
                </div>`;
            
        // Group validation errors by file if they exist
        const validationErrors = message.errors.find(error => error.code === "validation_error");
        if (validationErrors && validationErrors.details && validationErrors.details.length > 0) {
            // Group errors by file/input
            const errorsByFile = {};
            
            validationErrors.details.forEach(detail => {
                const fileKey = detail.input_name || 'unknown';
                const fileName = detail.file || fileNames[fileKey] || 'Fichier inconnu';
                
                if (!errorsByFile[fileKey]) {
                    errorsByFile[fileKey] = {
                        fileName: fileName,
                        errors: []
                    };
                }
                
                errorsByFile[fileKey].errors.push(detail);
            });
            
            // Display errors by file
            errorHtml += `<div class="validation-errors">`;
            Object.keys(errorsByFile).forEach(fileKey => {
                const fileData = errorsByFile[fileKey];
                errorHtml += `
                    <div class="file-error-group">
                        <h5>
                            <i class="fa fa-file-alt" style="margin-right: 8px;"></i>
                            Erreurs dans le fichier: ${fileData.fileName}
                        </h5>
                        <table class="error-table">
                            <thead>
                                <tr>
                                    <th>Ligne</th>
                                    <th>Colonne</th>
                                    <th>Valeur</th>
                                    <th>Message</th>
                                </tr>
                            </thead>
                            <tbody>`;
                
                fileData.errors.forEach(error => {
                    errorHtml += `
                        <tr>
                            <td>${error.row || 'N/A'}</td>
                            <td>${error.field || 'N/A'}</td>
                            <td>${error.value || 'N/A'}</td>
                            <td>${error.message || 'Erreur de validation'}</td>
                        </tr>`;
                });
                
                errorHtml += `
                            </tbody>
                        </table>
                    </div>`;
            });
            errorHtml += `</div>`;
        } else {
            // Display general errors
            errorHtml += `<ul style="padding-left: 20px; margin-bottom: 0;">`;
            message.errors.forEach(error => {
                errorHtml += `<li style="margin-bottom: 8px;">${error.message || 'Erreur inconnue'}</li>`;
            });
            errorHtml += `</ul>`;
        }
        
        errorHtml += `</div>`;
        $('#import-result').html(errorHtml);
    }
};