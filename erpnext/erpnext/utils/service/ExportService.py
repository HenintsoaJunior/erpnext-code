import frappe
import csv
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExportService:
    
    def validate_doctype(self, doctype):
        exists = frappe.db.exists("DocType", doctype)
        logger.info(f"Validating doctype, doctype: {doctype}, exists: {exists}")
        
        if not exists:
            logger.error(f"DocType validation failed, doctype: {doctype}")
            return False
        return True
    
    def get_doctype_fields(self, doctype):
        meta = frappe.get_meta(doctype)
        fields = [field.fieldname for field in meta.fields if not field.hidden]
        logger.info(f"Retrieved fields for doctype: {doctype}, fieldsCount: {len(fields)}")
        return fields
    
    def prepare_file_name(self, doctype, custom_file_name=None):
        if custom_file_name:
            file_name = custom_file_name
            if not file_name.endswith('.csv'):
                file_name += '.csv'
        else:
            file_name = f"{doctype.lower().replace(' ', '_')}_export.csv"
        
        logger.info(f"File name prepared: {file_name}")
        return file_name
    
    def fetch_data(self, doctype, filters=None, fields=None):
        if not fields:
            fields = self.get_doctype_fields(doctype)
        
        data = frappe.get_all(
            doctype,
            filters=filters,
            fields=fields
        )
        
        logger.info(f"Data fetched for doctype: {doctype}, rowCount: {len(data)}, filters: {filters}")
        return data, fields
    
    def generate_csv(self, data, headers, delimiter=","):
        csv_file = io.StringIO()
        csv_writer = csv.writer(csv_file, delimiter=delimiter)
        
        # Write headers
        csv_writer.writerow(headers)
        logger.info(f"CSV headers written: {headers}")
        
        # Write data rows
        rows_written = 0
        for row in data:
            csv_writer.writerow([row.get(field, '') for field in headers])
            rows_written += 1
        
        logger.info(f"CSV data rows written, count: {rows_written}")
        return csv_file.getvalue()
    
    def create_file_doc(self, file_name, file_content, is_private=0):
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "content": file_content,
            "is_private": is_private
        })
        file_doc.insert()
        logger.info(f"File created in ERPNext, fileUrl: {file_doc.file_url}")
        return file_doc
    
    def export_to_csv(self, doctype, filters=None, fields=None, file_name=None, delimiter=",", is_private=0):
        logger.info(f"Starting export process, doctype: {doctype}, filters: {filters}, fieldsCount: {len(fields) if fields else 'all'}")
        
        try:
            # Validate doctype
            if not self.validate_doctype(doctype):
                return {
                    "status": "error",
                    "message": f"Le DocType {doctype} n'existe pas",
                    "file_url": None,
                    "csv_content": None
                }
            
            # Prepare file name
            file_name = self.prepare_file_name(doctype, file_name)
            
            # Fetch data
            data, actual_fields = self.fetch_data(doctype, filters, fields)
            
            if not data:
                logger.warning(f"No data found for export, doctype: {doctype}, filters: {filters}")
                return {
                    "status": "warning",
                    "message": f"Aucune donnée à exporter pour {doctype} avec les filtres appliqués",
                    "file_url": None,
                    "csv_content": None
                }
            
            # Generate CSV content
            headers = list(data[0].keys()) if fields is None else fields
            csv_content = self.generate_csv(data, headers, delimiter)
            
            # Create file document
            file_doc = self.create_file_doc(file_name, csv_content, is_private)
            
            return {
                "status": "success",
                "message": f"Export réussi. {len(data)} enregistrements exportés dans {file_name}",
                "file_url": file_doc.file_url,
                "file_name": file_name,
                "record_count": len(data),
                "doctype": doctype,
                "csv_content": csv_content  # Added for direct download
            }
            
        except Exception as e:
            logger.error(f"Export failed with exception, doctype: {doctype}, error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Échec de l'exportation: {str(e)}",
                "file_url": None,
                "csv_content": None
            }
    
    def bulk_export(self, export_config):
        logger.info(f"Starting bulk export process, configCount: {len(export_config)}")
        results = []
        
        for config in export_config:
            doctype = config.get('doctype')
            if not doctype:
                logger.error("Missing doctype in export configuration")
                results.append({
                    "status": "error",
                    "message": "Configuration d'exportation invalide: doctype manquant",
                    "file_url": None
                })
                continue
                
            logger.info(f"Processing export for doctype: {doctype}")
            result = self.export_to_csv(
                doctype=doctype,
                filters=config.get('filters'),
                fields=config.get('fields'),
                file_name=config.get('file_name'),
                delimiter=config.get('delimiter', ','),
                is_private=config.get('is_private', 0)
            )
            
            results.append({
                "doctype": doctype,
                "result": result
            })
        
        # Summarize results
        success_count = sum(1 for r in results if r['result']['status'] == 'success')
        error_count = len(results) - success_count
        
        logger.info(f"Bulk export completed, successCount: {success_count}, errorCount: {error_count}")
        
        return {
            "status": "completed",
            "message": f"{success_count} exports réussis, {error_count} échecs",
            "details": results
        }
    
    def export_joined_doctypes(self, primary_config, related_configs):
        try:
            primary_doctype = primary_config.get("doctype")
            primary_filters = primary_config.get("filters", {})
            primary_fields = primary_config.get("fields", [])
            file_name = primary_config.get("file_name", f"{primary_doctype.lower()}_joined_export.csv")
            delimiter = primary_config.get("delimiter", ",")
            is_private = primary_config.get("is_private", 0)
            
            logger.info(f"Starting joined doctypes export with primary doctype: {primary_doctype}")
            
            # Validate primary doctype
            if not self.validate_doctype(primary_doctype):
                return {
                    "status": "error",
                    "message": f"Le DocType primaire {primary_doctype} n'existe pas",
                    "file_url": None,
                    "csv_content": None
                }
            
            # Get primary data
            primary_data, _ = self.fetch_data(primary_doctype, primary_filters, primary_fields)
            
            if not primary_data:
                return {
                    "status": "warning",
                    "message": f"Aucune donnée à exporter pour le doctype primaire {primary_doctype} avec les filtres appliqués",
                    "file_url": None,
                    "csv_content": None
                }
            
            # Prepare the combined data structure
            combined_data = []
            all_headers = primary_fields.copy()
            
            # Process each primary record
            for primary_record in primary_data:
                combined_record = {field: primary_record.get(field, '') for field in primary_fields}
                
                # Process related doctypes
                for related_config in related_configs:
                    related_doctype = related_config.get("doctype")
                    join_field = related_config.get("join_field")
                    related_fields = related_config.get("fields", [])
                    related_filters = related_config.get("filters", {}).copy()  # Make a copy to not modify the original
                    
                    # Validate related doctype
                    if not self.validate_doctype(related_doctype):
                        logger.warning(f"Related DocType {related_doctype} does not exist, skipping")
                        continue
                    
                    # Add join field filter
                    if join_field and join_field in primary_record:
                        join_value = primary_record.get(join_field)
                        if join_value:
                            related_filters[join_field] = join_value
                    
                    # Fetch related data
                    related_data, _ = self.fetch_data(related_doctype, related_filters, related_fields)
                    
                    # Add prefix to field names to avoid collisions
                    prefixed_fields = [f"{related_doctype}.{field}" for field in related_fields]
                    
                    # Update headers
                    for field in prefixed_fields:
                        if field not in all_headers:
                            all_headers.append(field)
                    
                    # If there's related data, add it to the combined record
                    if related_data:
                        for field_idx, field in enumerate(related_fields):
                            prefixed_field = prefixed_fields[field_idx]
                            combined_record[prefixed_field] = related_data[0].get(field, '')
                    else:
                        # Add empty values for related fields
                        for prefixed_field in prefixed_fields:
                            combined_record[prefixed_field] = ''
                
                combined_data.append(combined_record)
            
            # Generate CSV with combined data
            csv_content = self.generate_csv(combined_data, all_headers, delimiter)
            
            # Create file doc
            file_doc = self.create_file_doc(file_name, csv_content, is_private)
            
            return {
                "status": "success",
                "message": f"Export joint réussi. {len(combined_data)} enregistrements exportés dans {file_name}",
                "file_url": file_doc.file_url,
                "file_name": file_name,
                "record_count": len(combined_data),
                "doctype": primary_doctype,
                "csv_content": csv_content
            }
            
        except Exception as e:
            logger.error(f"Joined export failed with exception: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Échec de l'exportation jointe: {str(e)}",
                "file_url": None,
                "csv_content": None
            }
            
    def export_multi_doctype(self, config):
        """Handle multi-doctype export with primary and related doctypes"""
        try:
            primary_doctype = config.get("primary_doctype")
            primary_filters = config.get("primary_filters", {})
            primary_fields = config.get("primary_fields", [])
            related_doctypes = config.get("related_doctypes", [])
            file_name = config.get("file_name", f"{primary_doctype.lower()}_multi_export.csv")
            delimiter = config.get("delimiter", ",")
            is_private = config.get("is_private", 0)
            
            logger.info(f"Starting multi-doctype export with primary doctype: {primary_doctype}")
            
            # Validate primary doctype
            if not self.validate_doctype(primary_doctype):
                return {
                    "status": "error",
                    "message": f"Primary DocType {primary_doctype} does not exist",
                    "file_url": None,
                    "csv_content": None
                }
            
            # Get primary data
            primary_data, _ = self.fetch_data(primary_doctype, primary_filters, primary_fields)
            
            if not primary_data:
                return {
                    "status": "warning",
                    "message": f"No data found for primary doctype {primary_doctype} with applied filters",
                    "file_url": None,
                    "csv_content": None
                }
            
            # Prepare joined data using existing functionality
            primary_config = {
                "doctype": primary_doctype,
                "filters": primary_filters,
                "fields": primary_fields,
                "file_name": file_name,
                "delimiter": delimiter,
                "is_private": is_private
            }
            
            result = self.export_joined_doctypes(primary_config, related_doctypes)
            return result
            
        except Exception as e:
            logger.error(f"Multi-doctype export failed with error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Error in multi-doctype export: {str(e)}",
                "file_url": None,
                "csv_content": None
            }