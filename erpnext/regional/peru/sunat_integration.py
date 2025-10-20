import frappe
from frappe import _
import hashlib
from pyqrcode import create as qrcreate
from datetime import datetime

def send_to_sunat(sales_invoice):
    doc = frappe.get_doc("Sales Invoice", sales_invoice)
    try:
        hash_code = generate_sunat_hash(doc)
        qr_code = generate_sunat_qr(doc, hash_code)
        frappe.db.set_value("Sales Invoice", sales_invoice, "custom_sunat_hash_code", hash_code)
        frappe.db.set_value("Sales Invoice", sales_invoice, "custom_sunat_qr_code", qr_code)
        frappe.db.set_value("Sales Invoice", sales_invoice, "custom_sunat_doc_state", "Enviado")
        frappe.db.set_value("Sales Invoice", sales_invoice, "custom_sunat_transaction_date", datetime.now())
        frappe.db.commit()
        return {"success": True, "hash_code": hash_code}
    except Exception as e:
        frappe.log_error(f"Error SUNAT: {str(e)}")
        return {"success": False, "error": str(e)}

def generate_sunat_hash(doc):
    data_string = f"{doc.company}{doc.name}{doc.posting_date}{doc.grand_total}{doc.customer}"
    hash_object = hashlib.sha256(data_string.encode())
    return hash_object.hexdigest()[:16].upper()

def generate_sunat_qr(doc, hash_code):
    qr_data = f"{doc.company}|{doc.custom_sunat_doc_type}|{doc.name}|{doc.posting_date}|{doc.grand_total}|{hash_code}"
    qr = qrcreate(qr_data)
    img_str = qr.png_as_base64_str(scale=6)
    return f"data:image/png;base64,{img_str}"

@frappe.whitelist()
def send_to_sunat_api(sales_invoice):
    return send_to_sunat(sales_invoice)

@frappe.whitelist()
def check_sunat_status_api(sales_invoice):
    doc = frappe.get_doc("Sales Invoice", sales_invoice)
    return {"status": doc.custom_sunat_doc_state}
