# Roadmap V2 (12 semanas)

## Objetivo principal
Habilitar lectura confiable de boletas y facturas en Chile, junto con documentacion internacional, bajo un pipeline unico y auditable.

## Sprint 1-2
- Scaffold tecnico, CI/CD, observabilidad base.
- Endpoint `POST /documents/upload` + persistencia inicial.
- Definicion de taxonomia documental (boleta/factura/chile/internacional).
- Construccion de dataset inicial etiquetado y baseline de metricas.

## Sprint 3-4
- OCR + parser OpenAI/GitHub + pruebas unitarias.
- Clasificador de tipo documental y pais con score de confianza.
- Parser CLP Google Play sin regresion.

## Sprint 5-6
- Servicio FX historico oficial + cache.
- Parsers especializados Chile: boleta y factura.
- Reglas tributarias base Chile: RUT, IVA, folio, consistencia totales.

## Sprint 7-8
- Registro contable completo + export CSV/XLSX.
- Auditoria de decisiones y errores.
- Parsers internacionales v1 (EN/ES, invoices/receipts).
- Normalizacion de campos globales (tax id, due date, currency, totals).
- Mapeo por encabezados de plantilla Excel de rendicion (documento de salida oficial).
- Politica no bloqueante para campos faltantes: celdas vacias + warning.
- Implementacion de mapeo explicito para campos de cabecera y detalle de la plantilla.
- Persistencia de campos tributarios adicionales fuera de plantilla en metadata estructurada.

## Sprint 9-10
- Seguridad, hardening, performance tuning.
- Pruebas integracion y carga.
- Flujo de excepcion y revision manual para baja confianza.
- Retroalimentacion automatica de correcciones para mejorar precision.

## Sprint 11-12
- UAT negocio, checklist release, go-live.
- Plan de soporte hypercare.
- QA final por cobertura: Chile e internacional.
- Definicion de backlog post go-live por pais/proveedor prioritario.

## KPI de salida por bloque
- Fin Sprint 4: clasificacion documental >= 95% accuracy en dataset interno.
- Fin Sprint 6: precision campos criticos Chile >= 97%.
- Fin Sprint 8: precision campos criticos internacional >= 93%.
- Fin Sprint 12: tasa de revision manual <= 15% y estabilidad operacional >= 99.9%.
- KPI de exportacion: 100% de documentos procesados deben generar archivo de salida aunque existan campos faltantes.
- KPI de rescate: >= 98% de los campos tributarios detectables deben quedar registrados en salida o metadata.
