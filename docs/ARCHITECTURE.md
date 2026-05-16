# Arquitectura V2

## Contexto
Sistema de captura de documentos y validacion contable multi-moneda.

## Estilo arquitectonico
- Modular monolith en V2 inicial.
- Preparado para evolucionar a servicios separados (OCR/FX/export).

## Capa de inteligencia documental
- `Document Classifier`: identifica tipo de documento y pais probable.
- `OCR Orchestrator`: ejecuta OCR principal con fallback por baja confianza.
- `Parser Adapters`: adaptadores por pais/tipo (Chile e internacional).
- `Normalization Engine`: convierte salidas heterogeneas a contrato canonico.
- `Validation Engine`: reglas contables y tributarias por pais/tipo.
- `Manual Review Gateway`: deriva excepciones de baja confianza con evidencia.
- `Template Mapping Engine`: mapea `ExtractionResult` a encabezados de plantilla Excel.
- `Graceful Export Policy`: para campos ausentes escribe valor vacio y emite warning.

## Diagrama logico
1. Cliente sube documento a API.
2. API persiste metadata y publica job.
3. Worker clasifica documento (tipo + pais).
4. Worker ejecuta OCR + parser adapter (Chile o internacional).
5. Normalizacion genera `ExtractionResult` canonico con evidencia.
6. Servicio FX resuelve tasa historica.
7. Reglas contables/tributarias validan consistencia.
8. Registro contable y export disponible.
9. Eventos y metricas quedan auditados.

## Contratos internos
- `ExtractionResult`
- `FxResolution`
- `ValidationResult`
- `RegistrationResult`
- `ClassificationResult`
- `ReviewTask`

## Mapeo a plantilla de rendicion
Cabecera destino:
- Responsable, Rut, Periodo, Monto a pagar, Fecha, Autorizado por.

Detalle destino por fila:
- Mes, Cuenta, Descripcion Cuenta, Fecha, Nro Boleta Factura, Descripcion del gasto, Concepto, Centro Costo, PROVEEDOR, RUT, Observaciones, Total.

Politica de exportacion:
- Campo no disponible en extraccion: se exporta en blanco.
- Campo en blanco: warning auditable, no error bloqueante.
- Campos tributarios sin columna directa: se almacenan en `extra_fields` para trazabilidad.

## Cobertura inicial recomendada
- Chile:
	- Boleta electronica y ticket.
	- Factura afecta/exenta y factura electronica.
- Internacional:
	- Invoice/receipt en EN/ES.
	- Monedas USD/EUR/GBP/CLP como base inicial.

## NFRs
- Seguridad: validacion de archivos, limite de tamano, antivirus opcional.
- Rendimiento: colas y procesamiento batch.
- Trazabilidad: correlation_id por flujo.
- Operabilidad: health checks, readiness, liveness.
- Robustez funcional: ausencia de campos opcionales/no detectados no bloquea la generacion del documento de salida.
