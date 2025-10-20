# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# Constantes SUNAT para PLE

# Tablas SUNAT más comunes
TABLA_10_TIPO_COMPROBANTE = {
    "00": "Otros",
    "01": "Factura",
    "03": "Boleta de Venta",
    "07": "Nota de Crédito",
    "08": "Nota de Débito",
    "09": "Guía de Remisión Remitente",
    "12": "Ticket de Máquina Registradora",
    "13": "Documento emitido por bancos",
    "14": "Recibo por servicios públicos",
}

TABLA_2_TIPO_DOCUMENTO_IDENTIDAD = {
    "0": "OTROS",
    "1": "DNI",
    "4": "CARNET DE EXTRANJERIA",
    "6": "RUC",
    "7": "PASAPORTE",
    "A": "CEDULA DIPLOMATICA",
}

# Estado del comprobante
ESTADO_COMPROBANTE = {
    "0": "Anulado/Extornado",
    "1": "Vigente - Incide en saldos",
    "2": "Anulado - No incide en saldos",
    "8": "Anulado - Error en registro",
    "9": "Ajustes/Regularizaciones",
}
