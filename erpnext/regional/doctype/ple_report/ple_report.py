# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime
from erpnext.regional.peru.ple.generator import generate_ple_14_1, generate_ple_8_1


class PLEReport(Document):
    def validate(self):
        """Validaciones antes de guardar"""
        self.validate_dates()
        self.validate_company_ruc()
        self.validate_period()
        
        # Auto-generar el nombre del archivo si no existe
        if not self.file_name:
            self.file_name = self.generate_file_name()
    
    def validate_dates(self):
        """Validar que las fechas sean correctas"""
        if self.from_date and self.to_date:
            # Convertir strings a date
            from frappe.utils import getdate
            from_date = getdate(self.from_date)
            to_date = getdate(self.to_date)
            
            if from_date > to_date:
                frappe.throw(_("From Date cannot be greater than To Date"))
    
    def validate_company_ruc(self):
        """Validar que la compañía tenga RUC configurado"""
        if not self.company:
            return
        
        ruc = frappe.db.get_value("Company", self.company, "tax_id")
        
        if not ruc:
            frappe.throw(_("Company does not have RUC configured"))
        
        if len(ruc) != 11 or not ruc.isdigit():
            frappe.throw(_("RUC must be 11 numeric digits"))
    
    def validate_period(self):
        """Validar que el período sea válido"""
        if self.period_year:
            current_year = datetime.now().year
            if self.period_year < 2000 or self.period_year > current_year + 1:
                frappe.throw(_("Invalid period year"))
    
    def generate_file_name(self):
        """Generar nombre de archivo según formato SUNAT"""
        company_doc = frappe.get_doc("Company", self.company)
        ruc = company_doc.tax_id or "00000000000"
        
        year = str(self.period_year)
        month = str(self.period_month).zfill(2)
        day = "00"
        
        if self.report_type == "14.1 - Registro de Ventas":
            libro = "140100"
        elif self.report_type == "8.1 - Registro de Compras":
            libro = "080100"
        else:
            libro = "000000"
        
        file_name = f"LE{ruc}{year}{month}{day}{libro}00111.TXT"
        return file_name
    
    @frappe.whitelist()
    def generate_ple_file(self):
        """Generar el contenido del archivo PLE"""
        try:
            if self.report_type == "14.1 - Registro de Ventas":
                content = generate_ple_14_1(
                    company=self.company,
                    from_date=self.from_date,
                    to_date=self.to_date
                )
            elif self.report_type == "8.1 - Registro de Compras":
                content = generate_ple_8_1(
                    company=self.company,
                    from_date=self.from_date,
                    to_date=self.to_date
                )
            else:
                frappe.throw(_("Report type not implemented yet"))
            
            # Guardar contenido
            self.file_content = content
            self.total_records = len(content.split('\n')) if content else 0
            self.generation_date = datetime.now()
            self.status = "Generated"
            
            self.db_set('file_content', content)
            self.db_set('total_records', self.total_records)
            self.db_set('generation_date', self.generation_date)
            self.db_set('status', 'Generated')
            
            frappe.msgprint(_("PLE file generated successfully"), indicator="green")
            
            return {
                "success": True,
                "records": self.total_records,
                "file_name": self.file_name
            }
            
        except Exception as e:
            frappe.log_error(f"Error generating PLE: {str(e)}", "PLE Error")
            frappe.throw(_("Error generating PLE file: {0}").format(str(e)))
