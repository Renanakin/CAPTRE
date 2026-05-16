# Plan de QA y Criterios de Aceptacion

## Objetivo
Validar que la plataforma genere rendiciones correctas sin bloquear por campos faltantes y rescate la mayor cantidad posible de datos tributarios.

## Casos criticos funcionales

### QA-001 Campo faltante no bloquea
- Dado un documento sin Centro Costo
- Cuando se procesa y exporta
- Entonces Centro Costo queda en blanco
- Y se registra warning MISSING_FIELD
- Y el archivo de rendicion se genera exitosamente

### QA-002 Boleta chilena completa
- Dado boleta chilena legible
- Entonces extrae RUT, proveedor, folio, fecha, total
- Y completa Nro Boleta Factura, PROVEEDOR, RUT, Fecha, Total

### QA-003 Factura chilena con IVA
- Entonces valida consistencia neto + IVA = total (si aplica)
- Y registra warning si hay inconsistencia

### QA-004 Documento internacional EN
- Dado invoice en ingles
- Entonces clasifica country_code y document_type
- Y mapea campos globales a plantilla

### QA-005 Datos extra tributarios
- Dado documento con campos no presentes en plantilla
- Entonces guarda esos datos en extra_fields
- Y quedan trazables en auditoria

### QA-006 Duplicado por hash
- Dado carga repetida del mismo archivo
- Entonces no reprocesa innecesariamente
- Y responde estado duplicate esperado

### QA-007 Baja confianza
- Dado confidence < umbral
- Entonces estado REVIEW_REQUIRED
- Y permite override manual

## Casos no funcionales

### NFR-001 Rendimiento
- Procesamiento async p95 < 30s con lote de referencia

### NFR-002 Disponibilidad
- API mensual >= 99.9% (medicion productiva)

### NFR-003 Trazabilidad
- Cada request con correlation_id en logs

## Dataset minimo para pruebas
- 30 boletas chilenas (variadas)
- 30 facturas chilenas (afecta/exenta)
- 30 documentos internacionales EN/ES
- 10 casos de baja calidad de imagen
- 10 casos con campos internos faltantes

## Criterio de salida a produccion
- Precision campos criticos Chile >= 97%
- Precision campos criticos internacional >= 93% inicial
- 100% de archivos con salida generada aunque falten campos
- <= 15% documentos derivados a revision manual en operacion inicial
