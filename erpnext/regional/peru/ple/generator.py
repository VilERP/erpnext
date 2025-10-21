# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Generador de nombres de archivos PLE según formato SUNAT

Formato: LERRRRRRRRRRRAAAAMMDDLLLLLLCCOIMG.TXT

Donde:
- LE: Identificador fijo "Libros Electrónicos"
- RRRRRRRRRRR: RUC (11 dígitos)
- AAAA: Año (4 dígitos)
- MM: Mes (2 dígitos, 00 si no aplica)
- DD: Día (2 dígitos, 00 si no aplica)
- LLLLLL: Código del libro (6 dígitos)
- CC: Código de oportunidad (2 dígitos)
- O: Indicador de operaciones (1=con operaciones, 0=sin operaciones)
- I: Indicador de contenido (1=con información, 0=sin información)
- M: Moneda (1=PEN, 0=USD)
- G: Generado por PLE (siempre 1)
"""

import frappe
from frappe import _
from datetime import datetime

# Códigos de libros PLE según SUNAT
LIBROS_PLE = {
    # Registro de Ventas
    "registro_ventas": "140100",           # 14.1
    
    # Libro Diario
    "libro_diario": "050100",              # 5.1
    "libro_diario_simplificado": "050300", # 5.3
    
    # Libro Mayor
    "libro_mayor": "060100",               # 6.1
    
    # Inventarios
    "kardex_fisico": "120100",             # 12.1 - Unidades físicas
    "kardex_valorizado": "130100",         # 13.1 - Valorizado
    
    # Caja y Bancos
    "caja_efectivo": "010100",             # 1.1
    "caja_cta_corriente": "010200",        # 1.2
    
    # Estados Financieros
    "balance_general": "030100",           # 3.1
    "estado_resultados": "032000",         # 3.20
    "flujo_efectivo": "031800",            # 3.18
    "balance_comprobacion": "031700",      # 3.17
    
    # Cuentas por cobrar/pagar
    "ctas_cobrar": "030300",               # 3.3 - Clientes (Cta 12)
    "ctas_pagar": "031200",                # 3.12 - Proveedores (Cta 42)
    
    # Activos
    "activos_fijos": "070100",             # 7.1
    
    # Registro de Compras (fuera de Anexo 2 pero requerido)
    "registro_compras": "080100",          # 8.1
}

# Códigos de oportunidad según SUNAT
OPORTUNIDAD = {
    "apertura": "01",           # Al inicio del ejercicio
    "cierre": "10",            # Al cierre del ejercicio o mes
    "mensual": "10",           # Presentación mensual
    "anual": "13",             # Presentación anual
}


def generate_ple_filename(company, libro, fecha, codigo_oportunidad="10", 
                         moneda="PEN", tiene_operaciones=True, tiene_informacion=True):
    """
    Genera nombre de archivo PLE según formato SUNAT
    
    Args:
        company (str): Nombre de la empresa en ERPNext
        libro (str): Código del libro (usar claves de LIBROS_PLE)
        fecha (datetime/str): Fecha del reporte
        codigo_oportunidad (str): Código de oportunidad (default: "10" = cierre mensual)
        moneda (str): "PEN" o "USD" (default: "PEN")
        tiene_operaciones (bool): True si hay operaciones (default: True)
        tiene_informacion (bool): True si hay información (default: True)
    
    Returns:
        str: Nombre del archivo PLE
        
    Raises:
        ValueError: Si faltan datos o formato incorrecto
    
    Example:
        >>> generate_ple_filename("Mi Empresa", "registro_ventas", "2024-10-20")
        'LE20123456789202410000001401011111.TXT'
    """
    
    # Validar y obtener RUC
    ruc = frappe.db.get_value("Company", company, "custom_sunat_ruc")
    if not ruc:
        frappe.throw(_("La empresa {0} no tiene RUC configurado").format(company))
    
    if len(ruc) != 11 or not ruc.isdigit():
        frappe.throw(_("El RUC debe tener 11 dígitos numéricos. RUC actual: {0}").format(ruc))
    
    # Validar y obtener código de libro
    if libro not in LIBROS_PLE:
        frappe.throw(_("Código de libro inválido: {0}. Use una de las claves: {1}").format(
            libro, ", ".join(LIBROS_PLE.keys())
        ))
    
    codigo_libro = LIBROS_PLE[libro]
    
    # Procesar fecha
    if isinstance(fecha, str):
        fecha = datetime.strptime(fecha, "%Y-%m-%d")
    
    anio = fecha.strftime("%Y")
    mes = fecha.strftime("%m")
    
    # Día: 00 para libros mensuales, DD para libros diarios
    # La mayoría son mensuales
    libros_diarios = ["libro_diario", "libro_diario_simplificado", "caja_efectivo"]
    if libro in libros_diarios:
        dia = fecha.strftime("%d")
    else:
        dia = "00"
    
    # Validar código de oportunidad
    if codigo_oportunidad not in OPORTUNIDAD.values():
        frappe.throw(_("Código de oportunidad inválido: {0}").format(codigo_oportunidad))
    
    # Indicadores
    indicador_operaciones = "1" if tiene_operaciones else "0"
    indicador_informacion = "1" if tiene_informacion else "0"
    indicador_moneda = "1" if moneda == "PEN" else "0"
    indicador_ple = "1"  # Siempre 1 (generado por PLE)
    
    # Construir nombre
    nombre = (
        "LE" +                          # Identificador fijo
        ruc +                           # RUC (11 dígitos)
        anio +                          # Año (4 dígitos)
        mes +                           # Mes (2 dígitos)
        dia +                           # Día (2 dígitos)
        codigo_libro +                  # Código libro (6 dígitos)
        codigo_oportunidad +            # Oportunidad (2 dígitos)
        indicador_operaciones +         # Operaciones (1 dígito)
        indicador_informacion +         # Información (1 dígito)
        indicador_moneda +              # Moneda (1 dígito)
        indicador_ple +                 # PLE (1 dígito)
        ".TXT"                          # Extensión
    )
    
    return nombre


def get_libro_info(libro_codigo):
    """
    Obtener información de un libro PLE
    
    Args:
        libro_codigo (str): Código del libro (ej: "registro_ventas")
    
    Returns:
        dict: {"codigo": "140100", "nombre": "Registro de Ventas", ...}
    """
    nombres = {
        "registro_ventas": "Registro de Ventas e Ingresos",
        "registro_compras": "Registro de Compras",
        "libro_diario": "Libro Diario",
        "libro_mayor": "Libro Mayor",
        "kardex_valorizado": "Inventario Permanente Valorizado",
        "kardex_fisico": "Inventario Permanente en Unidades Físicas",
        "balance_general": "Balance General",
        "estado_resultados": "Estado de Ganancias y Pérdidas",
    }
    
    return {
        "codigo": LIBROS_PLE.get(libro_codigo, "000000"),
        "nombre": nombres.get(libro_codigo, libro_codigo.replace("_", " ").title()),
        "codigo_sunat": libro_codigo
    }


def validar_nombre_ple(nombre_archivo):
    """
    Validar que un nombre de archivo cumple con formato PLE SUNAT
    
    Args:
        nombre_archivo (str): Nombre del archivo a validar
    
    Returns:
        dict: {"valido": True/False, "errores": [...]}
    """
    errores = []
    
    # Longitud total: 37 caracteres (34 + .TXT)
    if len(nombre_archivo) != 37:
        errores.append(f"Longitud incorrecta: {len(nombre_archivo)} (debe ser 37)")
    
    # Debe empezar con LE
    if not nombre_archivo.startswith("LE"):
        errores.append("Debe comenzar con 'LE'")
    
    # Debe terminar con .TXT
    if not nombre_archivo.endswith(".TXT"):
        errores.append("Debe terminar con '.TXT'")
    
    # RUC debe ser numérico (posiciones 2-13)
    ruc = nombre_archivo[2:13]
    if not ruc.isdigit():
        errores.append(f"RUC debe ser numérico: {ruc}")
    
    # Año debe ser numérico (posiciones 13-17)
    anio = nombre_archivo[13:17]
    if not anio.isdigit():
        errores.append(f"Año debe ser numérico: {anio}")
    
    return {
        "valido": len(errores) == 0,
        "errores": errores,
        "ruc": ruc if len(ruc) == 11 else None,
        "anio": anio if len(anio) == 4 else None,
        "mes": nombre_archivo[17:19] if len(nombre_archivo) > 19 else None,
    }


@frappe.whitelist()
def generar_nombre_ple_api(company, libro, fecha, codigo_oportunidad="10", moneda="PEN"):
    """
    API para generar nombre PLE desde frontend
    
    Args:
        company (str): Nombre de la empresa
        libro (str): Código del libro
        fecha (str): Fecha en formato YYYY-MM-DD
        codigo_oportunidad (str): Código de oportunidad (default: "10")
        moneda (str): "PEN" o "USD" (default: "PEN")
    
    Returns:
        dict: {"nombre": "LE...", "valido": True/False}
    """
    try:
        nombre = generate_ple_filename(company, libro, fecha, codigo_oportunidad, moneda)
        validacion = validar_nombre_ple(nombre)
        
        return {
            "success": True,
            "nombre": nombre,
            "validacion": validacion,
            "libro_info": get_libro_info(libro)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }



def generate_ple_14_1(company, from_date, to_date):
    """
    Generar contenido del archivo PLE 14.1 - Registro de Ventas
    Con validaciones completas y manejo de errores
    
    Args:
        company (str): Nombre de la empresa
        from_date (str/date): Fecha inicial
        to_date (str/date): Fecha final
    
    Returns:
        str: Contenido del archivo TXT con formato PLE 14.1
    """
    
    errors = []
    warnings = []
    
    # Obtener todas las facturas del período
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "company": company,
            "posting_date": ["between", [from_date, to_date]],
            "docstatus": 1  # Solo facturas enviadas
        },
        fields=[
            "name",
            "posting_date",
            "due_date",
            "custom_sunat_doc_type",
            "customer",
            "customer_name",
            "tax_id",
            "grand_total",
            "base_total",
            "total_taxes_and_charges",
            "currency"
        ],
        order_by="posting_date asc, name asc"
    )
    
    if not invoices:
        return ""  # Sin registros
    
    lines = []
    
    for idx, invoice in enumerate(invoices, start=1):
        try:
            # Cargar documento completo
            doc = frappe.get_doc("Sales Invoice", invoice.name)
            
            # VALIDACIONES
            validation_errors = validate_invoice_for_ple(doc, idx)
            if validation_errors:
                errors.extend(validation_errors)
                continue  # Saltar esta factura
            
            # CAMPO 1: Período (AAAAMMDD)
            period = doc.posting_date.strftime("%Y%m00")
            
            # CAMPO 2: Número correlativo (CUO)
            correlativo = str(idx).zfill(10)
            
            # CAMPO 3: Número correlativo del asiento contable
            asiento = "M" + str(idx).zfill(9)  # M + 9 dígitos
            
            # CAMPO 4: Fecha de emisión
            fecha_emision = doc.posting_date.strftime("%d/%m/%Y")
            
            # CAMPO 5: Fecha de vencimiento
            fecha_vencimiento = doc.due_date.strftime("%d/%m/%Y") if doc.due_date else fecha_emision
            
            # CAMPO 6: Tipo de comprobante
            tipo_doc = doc.custom_sunat_doc_type or "01"
            
            # CAMPO 7: Serie del comprobante
            serie = extract_serie(doc.name)
            
            # CAMPO 8: Número del comprobante
            numero = extract_numero(doc.name)
            
            # CAMPO 9: Número consolidado (vacío)
            consolidado = ""
            
            # CAMPO 10: Tipo de documento del cliente
            tipo_doc_cliente = get_customer_doc_type(doc.tax_id)
            
            # CAMPO 11: Número de documento del cliente
            doc_cliente = doc.tax_id or "00000000"
            
            # CAMPO 12: Apellidos y nombres / Razón social
            cliente = (doc.customer_name or doc.customer)[:100]  # Max 100 chars
            
            # CAMPO 13-25: Valores monetarios
            valor_exportacion = "0.00"
            base_imponible = f"{doc.base_total:.2f}"
            descuento = "0.00"
            igv = f"{doc.total_taxes_and_charges:.2f}"
            descuento_igv = "0.00"
            exonerado = "0.00"
            inafecto = "0.00"
            isc = "0.00"
            ivap_base = "0.00"
            ivap = "0.00"
            icbper = "0.00"
            otros = "0.00"
            total = f"{doc.grand_total:.2f}"
            
            # CAMPO 26: Código de moneda
            moneda = doc.currency or "PEN"
            
            # CAMPO 27: Tipo de cambio
            tipo_cambio = "1.000" if moneda == "PEN" else get_exchange_rate(doc.posting_date, moneda)
            
            # CAMPOS 28-34: Fechas y documentos modificados (vacíos por ahora)
            fecha_emision_mod = ""
            tipo_doc_mod = ""
            serie_mod = ""
            numero_mod = ""
            identificador_proy = ""
            error_tipo_1 = ""
            error_tipo_2 = ""
            
            # CAMPO 35: Estado
            estado = "1"  # 1=Aceptado, 2=Anulado, 8=Anulado por error tipo 1, 9=Anulado por error tipo 2
            
            # Construir línea
            line = "|".join([
                period,
                correlativo,
                asiento,
                fecha_emision,
                fecha_vencimiento,
                tipo_doc,
                serie,
                numero,
                consolidado,
                tipo_doc_cliente,
                doc_cliente,
                cliente,
                valor_exportacion,
                base_imponible,
                descuento,
                igv,
                descuento_igv,
                exonerado,
                inafecto,
                isc,
                ivap_base,
                ivap,
                icbper,
                otros,
                total,
                moneda,
                tipo_cambio,
                fecha_emision_mod,
                tipo_doc_mod,
                serie_mod,
                numero_mod,
                identificador_proy,
                error_tipo_1,
                error_tipo_2,
                estado,
                ""  # Termina con pipe
            ])
            
            lines.append(line)
            
        except Exception as e:
            error_msg = f"Invoice {invoice.name}: {str(e)}"
            errors.append(error_msg)
            frappe.log_error(error_msg, "PLE 14.1 Generation Error")
            continue
    
    # Registrar errores si los hay
    if errors:
        error_log = "\n".join(errors)
        frappe.log_error(f"PLE 14.1 Generation Errors:\n{error_log}", "PLE Errors")
        frappe.msgprint(
            _("Generated with {0} errors. Check Error Log for details.").format(len(errors)),
            indicator="orange"
        )
    
    # Unir todas las líneas
    content = "\n".join(lines)
    return content


def validate_invoice_for_ple(doc, line_number):
    """Validar que una factura tenga todos los datos necesarios para PLE"""
    errors = []
    
    # Validar tipo de documento SUNAT
    if not doc.custom_sunat_doc_type:
        errors.append(f"Line {line_number} - Invoice {doc.name}: Missing SUNAT Document Type")
    
    # Validar cliente tenga documento
    if not doc.tax_id:
        errors.append(f"Line {line_number} - Invoice {doc.name}: Customer {doc.customer} has no Tax ID")
    elif len(doc.tax_id) < 8:
        errors.append(f"Line {line_number} - Invoice {doc.name}: Invalid Tax ID length: {doc.tax_id}")
    
    # Validar que tenga nombre de cliente
    if not doc.customer_name and not doc.customer:
        errors.append(f"Line {line_number} - Invoice {doc.name}: Missing customer name")
    
    # Validar montos
    if doc.grand_total <= 0:
        errors.append(f"Line {line_number} - Invoice {doc.name}: Invalid grand_total: {doc.grand_total}")
    
    return errors


def extract_serie(invoice_name):
    """Extraer serie del nombre de factura"""
    if "-" in invoice_name:
        parts = invoice_name.split("-")
        # Formato típico: ACC-SINV-2025-00001
        if len(parts) >= 2:
            return "-".join(parts[:-1])  # Todo excepto el último
    return "S001"  # Serie por defecto


def extract_numero(invoice_name):
    """Extraer número del nombre de factura"""
    if "-" in invoice_name:
        return invoice_name.split("-")[-1]
    return invoice_name


def get_customer_doc_type(tax_id):
    """Determinar tipo de documento del cliente según longitud"""
    if not tax_id:
        return "0"  # Sin documento
    
    length = len(tax_id)
    if length == 11:
        return "6"  # RUC
    elif length == 8:
        return "1"  # DNI
    elif length == 12:
        return "4"  # Carnet de extranjería
    else:
        return "0"  # Otros


def get_exchange_rate(date, currency):
    """Obtener tipo de cambio para una fecha"""
    try:
        rate = frappe.db.get_value(
            "Currency Exchange",
            {"date": date, "from_currency": currency, "to_currency": "PEN"},
            "exchange_rate"
        )
        if rate:
            return f"{rate:.3f}"
    except:
        pass
    
    return "1.000"  # Default


def generate_ple_8_1(company, from_date, to_date):
    """
    Generar contenido del archivo PLE 8.1 - Registro de Compras
    
    Args:
        company (str): Nombre de la empresa
        from_date (str/date): Fecha inicial
        to_date (str/date): Fecha final
    
    Returns:
        str: Contenido del archivo TXT con formato PLE 8.1
    """
    
    # Obtener todas las facturas de compra del período
    invoices = frappe.get_all(
        "Purchase Invoice",
        filters={
            "company": company,
            "posting_date": ["between", [from_date, to_date]],
            "docstatus": 1
        },
        fields=[
            "name",
            "posting_date",
            "bill_date",
            "supplier",
            "supplier_name",
            "tax_id",
            "grand_total",
            "base_total",
            "total_taxes_and_charges",
            "currency"
        ],
        order_by="posting_date asc, name asc"
    )
    
    if not invoices:
        return ""
    
    lines = []
    
    for idx, invoice in enumerate(invoices, start=1):
        try:
            doc = frappe.get_doc("Purchase Invoice", invoice.name)
            
            # Validar datos mínimos
            if not doc.tax_id:
                continue  # Saltar si no tiene RUC del proveedor
            
            # CAMPO 1: Período
            period = doc.posting_date.strftime("%Y%m00")
            
            # CAMPO 2: Correlativo
            correlativo = str(idx).zfill(10)
            
            # CAMPO 3: Asiento contable
            asiento = "M" + str(idx).zfill(9)
            
            # CAMPO 4: Fecha de emisión (bill_date o posting_date)
            fecha_emision = (doc.bill_date or doc.posting_date).strftime("%d/%m/%Y")
            
            # CAMPO 5: Fecha de vencimiento
            fecha_vencimiento = doc.due_date.strftime("%d/%m/%Y") if doc.due_date else fecha_emision
            
            # CAMPO 6: Tipo de comprobante (01=Factura, etc)
            tipo_doc = "01"  # Por defecto factura
            
            # CAMPO 7: Serie
            serie = extract_serie(doc.name)
            
            # CAMPO 8: Año emisión DUA
            anio_dua = ""
            
            # CAMPO 9: Número
            numero = extract_numero(doc.name)
            
            # CAMPO 10: Número final (rango)
            numero_final = ""
            
            # CAMPO 11: Tipo documento proveedor
            tipo_doc_proveedor = get_customer_doc_type(doc.tax_id)
            
            # CAMPO 12: Número documento proveedor
            doc_proveedor = doc.tax_id or "00000000"
            
            # CAMPO 13: Razón social proveedor
            proveedor = (doc.supplier_name or doc.supplier)[:100]
            
            # CAMPOS 14-24: Valores monetarios
            base_imponible = f"{doc.base_total:.2f}"
            igv = f"{doc.total_taxes_and_charges:.2f}"
            total = f"{doc.grand_total:.2f}"
            
            # Campos vacíos
            otros_campos = ["0.00"] * 8  # Base no gravada, ISC, ICBPER, etc
            
            # CAMPO 25: Moneda
            moneda = doc.currency or "PEN"
            
            # CAMPO 26: Tipo cambio
            tipo_cambio = "1.000" if moneda == "PEN" else get_exchange_rate(doc.posting_date, moneda)
            
            # CAMPOS 27-42: Varios campos adicionales (mayoría vacíos)
            campos_adicionales = [""] * 16
            
            # CAMPO 43: Estado
            estado = "1"
            
            # Construir línea
            line = "|".join([
                period,
                correlativo,
                asiento,
                fecha_emision,
                fecha_vencimiento,
                tipo_doc,
                serie,
                anio_dua,
                numero,
                numero_final,
                tipo_doc_proveedor,
                doc_proveedor,
                proveedor,
                base_imponible,
                *otros_campos,
                igv,
                total,
                moneda,
                tipo_cambio,
                *campos_adicionales,
                estado,
                ""
            ])
            
            lines.append(line)
            
        except Exception as e:
            frappe.log_error(f"Error PLE 8.1 - Invoice {invoice.name}: {str(e)}", "PLE 8.1 Error")
            continue
    
    return "\n".join(lines)


def generate_ple_5_1(company, from_date, to_date):
    """
    Generar contenido del archivo PLE 5.1 - Libro Diario
    
    Args:
        company (str): Nombre de la empresa
        from_date (str/date): Fecha inicial
        to_date (str/date): Fecha final
    
    Returns:
        str: Contenido del archivo TXT con formato PLE 5.1
    """
    
    # Obtener todos los asientos contables del período
    gl_entries = frappe.get_all(
        "GL Entry",
        filters={
            "company": company,
            "posting_date": ["between", [from_date, to_date]],
            "is_cancelled": 0
        },
        fields=[
            "name",
            "posting_date",
            "account",
            "debit",
            "credit",
            "voucher_type",
            "voucher_no",
            "against",
            "remarks",
            "party_type",
            "party",
            "cost_center"
        ],
        order_by="posting_date asc, name asc"
    )
    
    if not gl_entries:
        return ""
    
    lines = []
    
    for idx, entry in enumerate(gl_entries, start=1):
        try:
            # CAMPO 1: Período
            period = entry.posting_date.strftime("%Y%m00")
            
            # CAMPO 2: Correlativo
            correlativo = str(idx).zfill(10)
            
            # CAMPO 3: Fecha de operación
            fecha_operacion = entry.posting_date.strftime("%d/%m/%Y")
            
            # CAMPO 4: Glosa
            glosa = (entry.remarks or entry.voucher_type or "")[:100]
            
            # CAMPO 5: Código de cuenta contable
            codigo_cuenta = entry.account or ""
            
            # CAMPO 6: Código de centro de costos
            centro_costos = entry.cost_center or ""
            
            # CAMPO 7: Código de moneda
            moneda = "PEN"  # Por defecto soles
            
            # CAMPO 8: Tipo de cambio
            tipo_cambio = "1.000"
            
            # CAMPO 9: Monto en moneda extranjera (vacío para PEN)
            monto_extranjero = ""
            
            # CAMPO 10: Debe
            debe = f"{entry.debit:.2f}" if entry.debit else "0.00"
            
            # CAMPO 11: Haber
            haber = f"{entry.credit:.2f}" if entry.credit else "0.00"
            
            # CAMPO 12: Número de comprobante
            numero_comprobante = entry.voucher_no or ""
            
            # CAMPO 13: Fecha de comprobante
            fecha_comprobante = entry.posting_date.strftime("%d/%m/%Y")
            
            # CAMPO 14: Código de operación
            codigo_operacion = "1"  # Por defecto operación normal
            
            # CAMPO 15: Estado
            estado = "1"
            
            # Construir línea
            line = "|".join([
                period,
                correlativo,
                fecha_operacion,
                glosa,
                codigo_cuenta,
                centro_costos,
                moneda,
                tipo_cambio,
                monto_extranjero,
                debe,
                haber,
                numero_comprobante,
                fecha_comprobante,
                codigo_operacion,
                estado,
                ""
            ])
            
            lines.append(line)
            
        except Exception as e:
            frappe.log_error(f"Error PLE 5.1 - GL Entry {entry.name}: {str(e)}", "PLE 5.1 Error")
            continue
    
    return "\n".join(lines)


def generate_ple_13_1(company, from_date, to_date):
    """
    Generar contenido del archivo PLE 13.1 - Kardex Valorizado
    
    Args:
        company (str): Nombre de la empresa
        from_date (str/date): Fecha inicial
        to_date (str/date): Fecha final
    
    Returns:
        str: Contenido del archivo TXT con formato PLE 13.1
    """
    
    # Obtener todos los movimientos de inventario del período
    stock_entries = frappe.get_all(
        "Stock Ledger Entry",
        filters={
            "company": company,
            "posting_date": ["between", [from_date, to_date]]
        },
        fields=[
            "name",
            "posting_date",
            "item_code",
            # "item_name",  # Campo no disponible en Stock Ledger Entry
            "warehouse",
            "actual_qty",
            "valuation_rate",
            "stock_value",
            "voucher_type",
            "voucher_no",
            "is_cancelled"
        ],
        order_by="posting_date asc, name asc"
    )
    
    if not stock_entries:
        return ""
    
    lines = []
    
    for idx, entry in enumerate(stock_entries, start=1):
        try:
            # Saltar entradas canceladas
            if entry.is_cancelled:
                continue
                
            # CAMPO 1: Período
            period = entry.posting_date.strftime("%Y%m00")
            
            # CAMPO 2: Correlativo
            correlativo = str(idx).zfill(10)
            
            # CAMPO 3: Fecha de operación
            fecha_operacion = entry.posting_date.strftime("%d/%m/%Y")
            
            # CAMPO 4: Código de producto
            codigo_producto = entry.item_code or ""
            
            # CAMPO 5: Descripción del producto
            descripcion_producto = (entry.item_code or "")[:100]  # Usar item_code como descripción
            
            # CAMPO 6: Código de almacén
            codigo_almacen = entry.warehouse or ""
            
            # CAMPO 7: Cantidad
            cantidad = f"{entry.actual_qty:.2f}" if entry.actual_qty else "0.00"
            
            # CAMPO 8: Precio unitario
            precio_unitario = f"{entry.valuation_rate:.2f}" if entry.valuation_rate else "0.00"
            
            # CAMPO 9: Valor total
            valor_total = f"{entry.stock_value:.2f}" if entry.stock_value else "0.00"
            
            # CAMPO 10: Tipo de operación
            tipo_operacion = "1" if entry.actual_qty > 0 else "2"  # 1=Entrada, 2=Salida
            
            # CAMPO 11: Número de comprobante
            numero_comprobante = entry.voucher_no or ""
            
            # CAMPO 12: Fecha de comprobante
            fecha_comprobante = entry.posting_date.strftime("%d/%m/%Y")
            
            # CAMPO 13: Código de operación
            codigo_operacion = "1"  # Por defecto operación normal
            
            # CAMPO 14: Estado
            estado = "1"
            
            # Construir línea
            line = "|".join([
                period,
                correlativo,
                fecha_operacion,
                codigo_producto,
                descripcion_producto,
                codigo_almacen,
                cantidad,
                precio_unitario,
                valor_total,
                tipo_operacion,
                numero_comprobante,
                fecha_comprobante,
                codigo_operacion,
                estado,
                ""
            ])
            
            lines.append(line)
            
        except Exception as e:
            frappe.log_error(f"Error PLE 13.1 - Stock Entry {entry.name}: {str(e)}", "PLE 13.1 Error")
            continue
    
    return "\n".join(lines)
