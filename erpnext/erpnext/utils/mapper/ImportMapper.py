import frappe
from frappe import _
from erpnext.utils.service.ImportService import ImportService
import logging
import re
from datetime import datetime
import csv
import io
import os
import uuid
import tempfile

from erpnext.services.importeval.import_service import fichier1_data_to_item,fichier1_data_to_material_request,fichier1_data_to_warehouse,fichier2_data_to_supplier,fichier3_data_to_request_for_quotation

# Configure logging
logger = logging.getLogger(__name__)

class ImportMapper:
        
    def __init__(self, doctypes, column_mappings, numeric_fields=None, date_validation=None, valid_values=None, separator=","):
            self.doctypes = doctypes
            self.column_mappings = column_mappings
            self.numeric_fields = numeric_fields or {}
            self.date_validation = date_validation or {}  # New parameter for date validation
            self.valid_values = valid_values or {}
            self.separator = separator
            self.service = ImportService()
            logger.info(f"ImportMapper initialized with {len(doctypes)} doctypes, {len(column_mappings)} mappings")        
    
    def validate_cross_file_columns(self, files_data, file1_name, file1_column, file2_name, file2_column):
        try:
            # Vérifier que les fichiers existent dans files_data
            if file1_name not in files_data or file2_name not in files_data:
                missing_file = file1_name if file1_name not in files_data else file2_name
                return {
                    "status": "error",
                    "message": _("File {0} not found in files_data").format(missing_file),
                    "valid_values": self.valid_values
                }
            
            # Construire le dictionnaire pour _collect_files
            files_to_collect = {
                file1_name: files_data[file1_name],
                file2_name: files_data[file2_name]
            }
            
            files = self._collect_files(files_to_collect)
            if not isinstance(files, dict):
                return files
            
            file1_doc = files.get(file1_name)
            file2_doc = files.get(file2_name)
            
            if not file1_doc or not file2_doc:
                return {
                    "status": "error",
                    "message": _("One or both files not found"),
                    "valid_values": self.valid_values
                }
            
            file1_data = self.service.read_csv_file(file1_doc, self.separator)
            file2_data = self.service.read_csv_file(file2_doc, self.separator)
            
            file1_values = set()
            for row in file1_data:
                if file1_column in row and row[file1_column]:
                    file1_values.add(str(row[file1_column]).strip())
            
            file2_values = []
            missing_values = []
            for row_index, row in enumerate(file2_data):
                if file2_column in row and row[file2_column]:
                    value = str(row[file2_column]).strip()
                    file2_values.append(value)
                    if value not in file1_values:
                        missing_values.append({
                            "row": row_index + 2,
                            "value": value,
                            "file": file2_doc.file_name,
                            "column": file2_column
                        })
            
            if missing_values:
                if file2_name not in self.valid_values:
                    self.valid_values[file2_name] = {}
                self.valid_values[file2_name][file2_column] = list(file1_values)
                
                # Construire un message détaillé avec les lignes et valeurs manquantes
                error_details = [
                    _("Ligne {0}: Valeur '{1}'").format(err["row"], err["value"])
                    for err in missing_values
                ]
                error_message = _("Certaines valeurs dans la colonne {0} de {1} n'existent pas dans la colonne {2} de {3}: {4}").format(
                    file2_column, file2_name, file1_column, file1_name, "; ".join(error_details)
                )
                
                return {
                    "status": "error",
                    "message": error_message,
                    "details": missing_values,
                    "valid_values": self.valid_values
                }
            
            return {
                "status": "success",
                "message": _("All values in {0} column of {1} exist in {2} column of {3}").format(
                    file2_column, file2_name, file1_column, file1_name
                ),
                "valid_values": self.valid_values
            }
            
        except Exception as e:
            logger.exception(f"Error in validate_cross_file_columns: {str(e)}")
            return {
                "status": "error",
                "message": _("Error validating cross-file columns: {0}").format(str(e)),
                "valid_values": self.valid_values
            }
    def process_import(self, files_data):
        try:
            files = self._collect_files(files_data)
            if not isinstance(files, dict):
                return files
                
            file_errors = self.service.handle_file_errors(files)
            if file_errors:
                logger.warning(f"File errors detected: {file_errors}")
                return self._create_error_response("file", file_errors, is_list=True)
            
            adjusted_mappings = self._adjust_mappings(files)
            if not isinstance(adjusted_mappings, dict):
                return adjusted_mappings
            
            prepared_tables = self._prepare_tables(files)
            if not isinstance(prepared_tables, dict):
                return prepared_tables
            
            validation_result = self._validate_csv_data(files, adjusted_mappings)
            if validation_result is not True:
                return validation_result  # Error response
            
            result = self._perform_import(files, prepared_tables, adjusted_mappings)
            if result["status"] == "success":
                frappe.db.commit()
                logger.info("Import completed successfully")
                fichier1_data_to_warehouse()
                fichier1_data_to_item()
                fichier1_data_to_material_request()
                fichier2_data_to_supplier()
                fichier3_data_to_request_for_quotation()
            
            return result
            
        except Exception as e:
            logger.exception(f"Unhandled exception in process_import: {str(e)}")
            return self._create_error_response("exception", _("Failed to process import: {0}").format(str(e)))
    
    def _collect_files(self, files_data):
        try:
            files = {}
            for input_name, file_id in files_data.items():
                file_doc = frappe.get_doc("File", file_id)
                if not file_doc:
                    logger.error(f"Invalid file ID: {file_id}")
                    return self._create_error_response("file", _("Invalid file ID: {0}").format(file_id))
                files[input_name] = file_doc
            return files
        except Exception as e:
            logger.exception(f"Error collecting files: {str(e)}")
            return self._create_error_response("file_processing", _("Error processing file data: {0}").format(str(e)))
    
    def _adjust_mappings(self, files):
        try:
            adjusted_mappings = self.service.adjust_column_mappings(self.column_mappings, files)
            if not adjusted_mappings:
                logger.error("No valid column mappings after adjustment")
                return self._create_error_response("mappings", _("No valid column mappings after adjustment"))
            return adjusted_mappings
        except Exception as e:
            logger.exception(f"Error adjusting mappings: {str(e)}")
            return self._create_error_response("mappings", _("Error adjusting column mappings: {0}").format(str(e)))
    
    def _prepare_tables(self, files):
        try:
            prepared_tables = self.service.prepare_tables(files, self.doctypes)
            if not prepared_tables:
                logger.error("No valid doctypes prepared for import")
                return self._create_error_response("tables", _("No valid doctypes prepared for import"))
            return prepared_tables
        except Exception as e:
            logger.exception(f"Error preparing tables: {str(e)}")
            return self._create_error_response("tables", _("Error preparing tables: {0}").format(str(e)))
    
    def _get_date_fields(self, doctype):
        """Get all date fields for a given doctype."""
        return [
            field.fieldname
            for field in frappe.get_meta(doctype).fields
            if field.fieldtype in ["Date", "Datetime"]
        ]
    
    def _convert_date_format(self, date_str):
        """Convert date from DD/MM/YYYY to YYYY-MM-DD."""
        try:
            if date_str and re.match(r'\d{2}/\d{2}/\d{4}', date_str):
                parsed_date = datetime.strptime(date_str, '%d/%m/%Y')
                return parsed_date.strftime('%Y-%m-%d')
            return date_str  # Return as is if format doesn't match
        except ValueError as e:
            logger.error(f"Invalid date format for {date_str}: {str(e)}")
            return None
    
    def _validate_csv_data(self, files, adjusted_mappings):
        try:
            validation_errors = []
            
            for input_name, file in files.items():
                doctype = self.doctypes.get(input_name)
                if not doctype:
                    continue
                
                date_fields = self._get_date_fields(doctype)
                
                mappings = adjusted_mappings.get(input_name, {})
                mapped_date_fields = [
                    csv_field
                    for csv_field, db_field in mappings.items()
                    if db_field in date_fields
                ]
                
                csv_data = self.service.read_csv_file(file, self.separator)
                
                # Validate numeric fields
                num_fields = self.numeric_fields.get(input_name, [])
                # Validate fields with valid value constraints
                valid_value_fields = self.valid_values.get(input_name, {})
                # Validate date fields with range constraints
                date_validations = self.date_validation.get(input_name, {})
                
                for row_index, row in enumerate(csv_data):
                    # Numeric validation
                    for field_name in num_fields:
                        if field_name in row:
                            value = row[field_name]
                            if value and not self._is_numeric(value):
                                error = {
                                    "row": row_index + 2,
                                    "field": field_name,
                                    "file": file.file_name,
                                    "input_name": input_name,
                                    "value": value,
                                    "message": _("La valeur '{0}' dans la colonne '{1}' à la ligne {2} du fichier '{3}' doit être un nombre").format(
                                        value, field_name, row_index + 2, file.file_name
                                    )
                                }
                                validation_errors.append(error)
                    
                    # Valid values validation
                    for field_name, valid_options in valid_value_fields.items():
                        if field_name in row:
                            value = row[field_name]
                            if value and value not in valid_options:
                                error = {
                                    "row": row_index + 2,
                                    "field": field_name,
                                    "file": file.file_name,
                                    "input_name": input_name,
                                    "value": value,
                                    "message": _("La valeur '{0}' dans la colonne '{1}' à la ligne {2} du fichier '{3}' doit être l'une des valeurs suivantes: {4}").format(
                                        value, field_name, row_index + 2, file.file_name, ", ".join(valid_options)
                                    )
                                }
                                validation_errors.append(error)
                    
                    # Date format validation
                    for csv_field in mapped_date_fields:
                        if csv_field in row:
                            date_value = row[csv_field]
                            if date_value:
                                converted_date = self._convert_date_format(date_value)
                                if converted_date is None:
                                    error = {
                                        "row": row_index + 2,
                                        "field": csv_field,
                                        "file": file.file_name,
                                        "input_name": input_name,
                                        "value": date_value,
                                        "message": _("Format de date invalide '{0}' à la ligne {1} du fichier '{2}'. Attendu: JJ/MM/AAAA").format(
                                            date_value, row_index + 2, file.file_name
                                        )
                                    }
                                    validation_errors.append(error)
                                else:
                                    # Date range validation
                                    if csv_field in date_validations:
                                        date_config = date_validations[csv_field]
                                        min_date = date_config.get("min_date")
                                        max_date = date_config.get("max_date")
                                        
                                        # Handle 'today' for max_date
                                        if max_date == "today":
                                            max_date = datetime.now().strftime('%Y-%m-%d')
                                        
                                        try:
                                            date_obj = datetime.strptime(converted_date, '%Y-%m-%d')
                                            if min_date:
                                                min_date_obj = datetime.strptime(min_date, '%Y-%m-%d')
                                                if date_obj < min_date_obj:
                                                    error = {
                                                        "row": row_index + 2,
                                                        "field": csv_field,
                                                        "file": file.file_name,
                                                        "input_name": input_name,
                                                        "value": date_value,
                                                        "message": _("La date '{0}' dans la colonne '{1}' à la ligne {2} du fichier '{3}' est antérieure à la date minimale autorisée ({4})").format(
                                                            date_value, csv_field, row_index + 2, file.file_name, min_date
                                                        )
                                                    }
                                                    validation_errors.append(error)
                                            if max_date:
                                                max_date_obj = datetime.strptime(max_date, '%Y-%m-%d')
                                                if date_obj > max_date_obj:
                                                    error = {
                                                        "row": row_index + 2,
                                                        "field": csv_field,
                                                        "file": file.file_name,
                                                        "input_name": input_name,
                                                        "value": date_value,
                                                        "message": _("La date '{0}' dans la colonne '{1}' à la ligne {2} du fichier '{3}' est postérieure à la date maximale autorisée ({4})").format(
                                                            date_value, csv_field, row_index + 2, file.file_name, max_date
                                                        )
                                                    }
                                                    validation_errors.append(error)
                                        except ValueError as e:
                                            logger.error(f"Error parsing date boundaries for {csv_field}: {str(e)}")
                                            error = {
                                                "row": row_index + 2,
                                                "field": csv_field,
                                                "file": file.file_name,
                                                "input_name": input_name,
                                                "value": date_value,
                                                "message": _("Erreur de validation des limites de date pour '{0}' à la ligne {1} du fichier '{2}': {3}").format(
                                                    date_value, row_index + 2, file.file_name, str(e)
                                                )
                                            }
                                            validation_errors.append(error)
            
            if validation_errors:
                logger.error(f"Data validation errors: {validation_errors}")
                return {
                    "status": "errors",
                    "data": None,
                    "errors": [{
                        "code": "validation_error",
                        "field": "data",
                        "message": _("Des erreurs de validation ont été détectées. Veuillez corriger les valeurs."),
                        "details": validation_errors
                    }]
                }
                
            return True
                
        except Exception as e:
            logger.exception(f"Error validating CSV data: {str(e)}")
            return self._create_error_response("validation", _("Error during data validation: {0}").format(str(e)))
        
                
    def _process_csv_data(self, csv_data, mapped_date_fields):
        """Process CSV data in memory, converting date fields."""
        try:
            processed_rows = []
            for row in csv_data:
                processed_row = row.copy()
                for csv_field in mapped_date_fields:
                    if csv_field in processed_row:
                        converted_date = self._convert_date_format(processed_row[csv_field])
                        if converted_date is None:
                            logger.error(f"Invalid date in row: {row}")
                            return None
                        processed_row[csv_field] = converted_date
                processed_rows.append(processed_row)
            return processed_rows
        except Exception as e:
            logger.exception(f"Error processing CSV data: {str(e)}")
            return None
    
    def _create_temp_csv_file(self, csv_data, original_file):
        """Create a temporary CSV file with processed data."""
        try:
            headers = list(csv_data[0].keys())
            unique_id = str(uuid.uuid4())[:8]
            temp_file_name = f"processed_{unique_id}_{original_file.file_name}"
            temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)
            
            with open(temp_file_path, "w", encoding="utf-8", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(csv_data)
            
            return temp_file_path
        except Exception as e:
            logger.exception(f"Error creating temporary CSV file: {str(e)}")
            return None
    
    def _create_file_like_object(self, original_file, temp_file_path):
        """Create a File-like object mimicking Frappe File document."""
        class FileLikeObject:
            def __init__(self, file_path, original_file):
                self.file_url = temp_file_path
                self.file_name = os.path.basename(temp_file_path)
                self.is_private = original_file.is_private
                self.attached_to_doctype = original_file.attached_to_doctype
                self.attached_to_name = original_file.attached_to_name
            
            def get_content(self):
                with open(self.file_url, "rb") as f:
                    return f.read()
        
        return FileLikeObject(temp_file_path, original_file)
    
    def _perform_import(self, files, prepared_tables, adjusted_mappings):
        try:
            processed_files = {}
            temp_files = []
            
            for input_name, file in files.items():
                # Get doctype and date fields
                doctype = self.doctypes.get(input_name)
                if not doctype:
                    continue
                date_fields = self._get_date_fields(doctype)
                
                # Get mappings for this input
                mappings = adjusted_mappings.get(input_name, {})
                mapped_date_fields = [
                    csv_field
                    for csv_field, db_field in mappings.items()
                    if db_field in date_fields
                ]
                
                # Read CSV data
                csv_data = self.service.read_csv_file(file, self.separator)
                logger.debug(f"Original CSV data for {input_name}: {csv_data[:2]}")
                
                # Process CSV data in memory
                processed_data = self._process_csv_data(csv_data, mapped_date_fields)
                if not processed_data:
                    return self._create_error_response(
                        "data_processing",
                        _("Échec du traitement des données CSV pour {0}").format(input_name)
                    )
                
                # Create a temporary CSV file
                temp_file_path = self._create_temp_csv_file(processed_data, file)
                if not temp_file_path:
                    return self._create_error_response(
                        "file_processing",
                        _("Échec de la création du fichier CSV temporaire pour {0}").format(input_name)
                    )
                
                temp_files.append(temp_file_path)
                
                # Create a File-like object
                file_like_obj = self._create_file_like_object(file, temp_file_path)
                processed_files[input_name] = file_like_obj
                logger.debug(f"Processed file for {input_name}: {file_like_obj.file_name}")
            
            # Perform import
            logger.debug("Starting import_files")
            result = self.service.import_files(processed_files, prepared_tables, adjusted_mappings, self.separator)
            logger.debug(f"Import result: {result}")
            
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file {temp_file}: {str(e)}")
            
            return result
            
        except Exception as e:
            # Clean up on failure
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file {temp_file}: {str(e)}")
            logger.exception(f"Error during import: {str(e)}")
            return self._create_error_response("import", _("Error during import process: {0}").format(str(e)))
    
    def _is_numeric(self, value):
        if value is None:
            return False
            
        value = str(value).strip()
        
        return bool(re.match(r'^-?\d+(\.\d+)?$', value))
    
    def _create_error_response(self, field, message, details=None, code=None, is_list=False):
        if is_list:
            return {
                "status": "errors",
                "data": None,
                "errors": [{"code": None, "field": field, "message": error} for error in message]
            }
            
        return {
            "status": "errors",
            "data": None,
            "errors": [{
                "code": code,
                "field": field,
                "message": message,
                "details": details
            }]
        }