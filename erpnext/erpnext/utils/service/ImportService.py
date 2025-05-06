import frappe
import csv
import os
import io
from frappe import _
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImportService:
    # Dans la méthode handle_file_errors de ImportService
    def handle_file_errors(self, files):
        errors = []
        logger.info(f"Checking for file errors, filesCount: {len(files)}")
        
        for input_name, file in files.items():
            try:
                logger.info(f"Checking file: {input_name}, file_name: {file.file_name}")
                
                # Vérifier si le fichier existe
                if not file or not hasattr(file, 'file_url') or not frappe.db.exists("File", file.name):
                    error_msg = f"{input_name}: Erreur de fichier: Fichier non trouvé ou invalide"
                    logger.error(f"File error detected, inputName: {input_name}, errorMessage: {error_msg}")
                    errors.append(error_msg)
                    continue
                
                # Obtenir le contenu du fichier
                try:
                    content = file.get_content()
                    if not content:
                        error_msg = f"{input_name}: Erreur de fichier: Fichier vide"
                        logger.error(f"File error detected, inputName: {input_name}, errorMessage: {error_msg}")
                        errors.append(error_msg)
                        continue
                    
                    # Conversion en texte si nécessaire
                    if isinstance(content, bytes):
                        try:
                            text_content = content.decode('utf-8')
                        except UnicodeDecodeError:
                            error_msg = f"{input_name}: Erreur de fichier: Problème d'encodage"
                            logger.error(f"File error detected, inputName: {input_name}, errorMessage: {error_msg}")
                            errors.append(error_msg)
                            continue
                    else:
                        # Le contenu est déjà une chaîne de caractères
                        text_content = content
                    
                    # Vérifier si c'est un CSV valide
                    # Autres validations...
                    
                except Exception as e:
                    error_msg = f"{input_name}: Erreur de fichier: {str(e)}"
                    logger.error(f"File error detected, inputName: {input_name}, errorMessage: {error_msg}")
                    errors.append(error_msg)
                    continue
                    
            except Exception as e:
                error_msg = f"{input_name}: Erreur de fichier: {str(e)}"
                logger.error(f"File error detected, inputName: {input_name}, errorMessage: {error_msg}")
                errors.append(error_msg)
        
        logger.info(f"File error check complete, errorsCount: {len(errors)}")
        return errors

    def _is_valid_file(self, file):
        """
        Check if the uploaded file is valid
        """
        try:
            # Check if the File doc exists and has a valid file_url
            if not hasattr(file, 'file_url') or not file.file_url:
                return False
            # Construct file path using frappe.get_site_path
            file_path = os.path.join(frappe.get_site_path('public', 'files'), file.file_url.lstrip('/files/'))
            return os.path.exists(file_path) and os.access(file_path, os.R_OK)
        except Exception as e:
            logger.error(f"File validation failed: {str(e)}")
            return False

    def adjust_column_mappings(self, column_mappings, files):
        """
        Adjust column mappings based on uploaded files
        """
        logger.info(f"Adjusting column mappings, originalMappingsCount: {len(column_mappings)}, filesCount: {len(files)}")
        
        adjusted_mappings = column_mappings.copy()
        for input_name in list(adjusted_mappings.keys()):
            if input_name not in files:
                del adjusted_mappings[input_name]
                logger.info(f"Removed mapping for missing file, inputName: {input_name}")
        
        logger.info(f"Column mappings adjusted, finalMappingsCount: {len(adjusted_mappings)}")
        return adjusted_mappings

    def read_csv_file(self, file, separator=","):
        """
        Read CSV file using File doctype content
        """
        logger.info(f"Reading CSV file, fileUrl: {file.file_url}, separator: {separator}")
        data = []
        
        try:
            # Get file content directly from File doctype
            file_content = file.get_content()
            if not file_content:
                raise ValueError("No content found in file")
            
            # Use io.StringIO to treat bytes content as a file-like object
            csvfile = io.StringIO(file_content.decode('utf-8') if isinstance(file_content, bytes) else file_content)
            reader = csv.reader(csvfile, delimiter=separator)
            headers = next(reader)
            logger.info(f"CSV headers: {headers}")
            
            row_count = 0
            for row in reader:
                entry = {headers[i]: row[i] if i < len(row) else None for i in range(len(headers))}
                data.append(entry)
                row_count += 1
            
            logger.info(f"CSV file read complete, rowCount: {row_count}")
        
        except Exception as e:
            logger.error(f"Error reading CSV file, fileUrl: {file.file_url}, error: {str(e)}")
        
        return data

    def prepare_tables(self, files, file_mappings):
        """
        Prepare tables (doctypes in ERPNext) for import
        """
        logger.info(f"Preparing tables, filesCount: {len(files)}, fileMappingsCount: {len(file_mappings)}")
        tables = {}
        
        for input_name, doctype in file_mappings.items():
            if input_name in files and self._is_valid_file(files[input_name]):
                tables[input_name] = doctype
                logger.info(f"Added table mapping, inputName: {input_name}, doctype: {doctype}")
            else:
                if input_name in files:
                    del files[input_name]
                logger.info(f"Removed invalid file, inputName: {input_name}")
        
        logger.info(f"Tables prepared, tablesCount: {len(tables)}, remainingFilesCount: {len(files)}")
        return tables

    def import_files(self, files, tables, column_mappings, separator=","):
        """
        Import CSV files into ERPNext doctypes
        """
        logger.info(f"Starting import process, filesCount: {len(files)}, tablesCount: {len(tables)}, "
                    f"columnMappingsCount: {len(column_mappings)}, separator: {separator}")
        
        if not self.validate_input(files, tables, column_mappings):
            logger.error(f"Input validation failed, filesCount: {len(files)}, tablesCount: {len(tables)}, "
                         f"columnMappingsCount: {len(column_mappings)}")
            return {
                "status": "errors",
                "data": None,
                "errors": [{
                    "code": None,
                    "field": "input",
                    "message": _("Le nombre de fichiers, tables et mappings de colonnes doit être identique."),
                    "details": None
                }]
            }

        errors = []
        insert_errors = []
        table_list = ", ".join(tables.values())
        logger.info(f"Processing tables: {table_list}")

        frappe.db.begin()
        logger.info("Transaction started")

        try:
            for index, (input_name, file) in enumerate(files.items()):
                doctype = tables.get(input_name)
                mapping = column_mappings.get(input_name, {})
                
                logger.info(f"Processing file, index: {index}, fileName: {file.file_name}, doctype: {doctype}")

                if not self.validate_doctype(doctype, file.file_name, errors):
                    logger.error(f"Doctype validation failed, doctype: {doctype}")
                    continue

                data = self.read_csv_file(file, separator)
                logger.info(f"CSV data loaded, fileName: {file.file_name}, rowCount: {len(data)}")

                if not data:
                    errors.append({
                        "code": None,
                        "field": "file",
                        "message": _("Aucune donnée trouvée dans le fichier CSV."),
                        "details": {"file_name": file.file_name}
                    })
                    logger.error(f"Empty CSV file, fileName: {file.file_name}")
                    continue

                for row_index, row in enumerate(data):
                    logger.info(f"Processing row, fileName: {file.file_name}, rowIndex: {row_index}, doctype: {doctype}")
                    
                    doc = frappe.new_doc(doctype)
                    mapped_row = {}
                    
                    for csv_column_name, value in row.items():
                        if csv_column_name in mapping:
                            field_name = mapping[csv_column_name]
                            if field_name in doc.as_dict():
                                doc.set(field_name, value)
                                mapped_row[field_name] = value
                                logger.info(f"Set document field, field: {field_name}, csvColumn: {csv_column_name}, "
                                            f"mappedField: {field_name}, value: {value}")
                            else:
                                logger.warning(f"No field found for column, csvColumn: {csv_column_name}, "
                                               f"mappedField: {field_name}")
                        else:
                            logger.warning(f"No mapping found for CSV column, csvColumn: {csv_column_name}")

                    try:
                        doc.insert()
                        logger.info(f"Row inserted successfully, doctype: {doctype}, rowIndex: {row_index}")
                    except Exception as e:
                        insert_errors.append({
                            "field": "database",
                            "message": _("Échec d'insertion dans la base de données: {0}").format(str(e)),
                            "details": {
                                "row_number": row_index + 2,
                                "row_data": row,
                                "file_name": file.file_name,
                                "mapped_data": mapped_row
                            }
                        })
                        logger.error(f"Insert error, doctype: {doctype}, rowIndex: {row_index}, error: {str(e)}, "
                                     f"row_data: {row}")

            if insert_errors:
                frappe.db.rollback()
                logger.info(f"Transaction rolled back due to insert errors, errorCount: {len(insert_errors)}")
                return {
                    "status": "errors",
                    "data": None,
                    "errors": insert_errors
                }

            frappe.db.commit()
            logger.info("Transaction committed successfully")
            return {
                "status": "success",
                "data": {"message": _("Import successful. Doctypes processed: {0}").format(table_list)},
                "errors": None
            }

        except Exception as e:
            frappe.db.rollback()
            logger.error(f"Import failed with exception, message: {str(e)}")
            return {
                "status": "errors",
                "data": None,
                "errors": [{
                    "code": None,
                    "field": "exception",
                    "message": _("Échec de l'importation: {0}").format(str(e)),
                    "details": {"errors": errors, "insert_errors": insert_errors}
                }]
            }

    def validate_input(self, files, tables, column_mappings):
        """
        Validate input consistency
        """
        is_valid = len(files) == len(tables) == len(column_mappings)
        logger.info(f"Validating input consistency, filesCount: {len(files)}, tablesCount: {len(tables)}, "
                    f"columnMappingsCount: {len(column_mappings)}, isValid: {is_valid}")
        return is_valid

    def validate_doctype(self, doctype, file_name, errors):
        """
        Validate ERPNext doctype
        """
        exists = frappe.db.exists("DocType", doctype)
        logger.info(f"Validating doctype, doctype: {doctype}, fileName: {file_name}, exists: {exists}")
        
        if not exists:
            errors.append({
                "file": file_name,
                "message": _("Doctype does not exist: {0}").format(doctype)
            })
            return False
        return True