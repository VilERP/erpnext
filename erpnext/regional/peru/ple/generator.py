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
    
    Args:
        company (str): Nombre de la empresa
        from_date (str/date): Fecha inicial
        to_date (str/date): Fecha final
    
    Returns:
        str: Contenido del archivo TXT con formato PLE 14.1
    """
    
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
    
    lines = []
    
    for idx, invoice in enumerate(invoices, start=1):
        # Cargar documento completo para obtener más detalles
        doc = frappe.get_doc("Sales Invoice", invoice.name)
        
        # CAMPO 1: Período (AAAAMMDD)
        period = doc.posting_date.strftime("%Y%m00")
        
        # CAMPO 2: Número correlativo (CUO)
        correlativo = str(idx).zfill(10)
        
        # CAMPO 3: Número correlativo del asiento contable (vacío por ahora)
        asiento = ""
        
        # CAMPO 4: Fecha de emisión
        fecha_emision = doc.posting_date.strftime("%d/%m/%Y")
        
        # CAMPO 5: Fecha de vencimiento (igual a emisión si no hay fecha de vencimiento)
        fecha_vencimiento = doc.due_date.strftime("%d/%m/%Y") if doc.due_date else fecha_emision
        
        # CAMPO 6: Tipo de comprobante (01=Factura, 03=Boleta, etc.)
        tipo_doc = doc.custom_sunat_doc_type or "01"
        
        # CAMPO 7: Serie del comprobante
        serie = doc.name.split("-")[0] if "-" in doc.name else ""
        
        # CAMPO 8: Número del comprobante
        numero = doc.name.split("-")[-1] if "-" in doc.name else doc.name
        
        # CAMPO 9: Número consolidado (vacío)
        consolidado = ""
        
        # CAMPO 10: Tipo de documento del cliente (6=RUC, 1=DNI, etc.)
        tipo_doc_cliente = "6" if doc.tax_id and len(doc.tax_id) == 11 else "1"
        
        # CAMPO 11: Número de documento del cliente
        doc_cliente = doc.tax_id or "00000000"
        
        # CAMPO 12: Apellidos y nombres / Razón social del cliente
        cliente = doc.customer_name or doc.customer
        
        # CAMPO 13: Valor exportación (0.00 si no aplica)
        valor_exportacion = "0.00"
        
        # CAMPO 14: Base imponible gravada
        base_imponible = f"{doc.base_total:.2f}"
        
        # CAMPO 15: Descuento (0.00 por ahora)
        descuento = "0.00"
        
        # CAMPO 16: IGV (18%)
        igv = f"{doc.total_taxes_and_charges:.2f}"
        
        # CAMPO 17: Descuento IGV (0.00)
        descuento_igv = "0.00"
        
        # CAMPO 18: Importe total sin IGV por operaciones exoneradas (0.00)
        exonerado = "0.00"
        
        # CAMPO 19: Importe total sin IGV por operaciones inafectas (0.00)
        inafecto = "0.00"
        
        # CAMPO 20: ISC (0.00)
        isc = "0.00"
        
        # CAMPO 21: Base imponible IVAP (0.00)
        ivap_base = "0.00"
        
        # CAMPO 22: IVAP (0.00)
        ivap = "0.00"
        
        # CAMPO 23: ICBPER (0.00)
        icbper = "0.00"
        
        # CAMPO 24: Otros tributos (0.00)
        otros = "0.00"
        
        # CAMPO 25: Importe total del comprobante
        total = f"{doc.grand_total:.2f}"
        
        # CAMPO 26: Código de moneda (PEN, USD, etc.)
        moneda = doc.currency or "PEN"
        
        # CAMPO 27: Tipo de cambio (1.000 si es PEN)
        tipo_cambio = "1.000"
        
        # CAMPO 28-34: Campos adicionales (vacíos por ahora)
        campos_adicionales = [""] * 7
        
        # CAMPO 35: Estado del comprobante (1=Aceptado, 2=Anulado, etc.)
        estado = "1"
        
        # Construir línea (separada por pipe |)
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
            *campos_adicionales,
            estado,
            ""  # Termina con pipe
        ])
        
        lines.append(line)
    
    # Unir todas las líneas con salto de línea
    content = "\n".join(lines)
    
    return content
