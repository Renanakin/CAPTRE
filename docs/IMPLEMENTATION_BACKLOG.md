# Backlog de Implementacion V2

## Checkpoint proxima sesion
- Fecha checkpoint: 2026-05-13.
- Ultimo estado validado: API + worker en verde con 8 pruebas unitarias passing.
- Ultimo hito funcional: validacion tributaria/contable base + flujo de revision manual implementado.
- Ultima mejora validada en documento real: campo `Mes` corregido (factura de abril -> Mes=4).

Archivos tocados recientemente (referencia rapida):
- `apps/api/app/main.py`
- `apps/api/app/months.py`
- `tests/unit/test_documents_api.py`
- `tests/unit/test_worker_main.py`

Pendiente inmediato para continuar:
1. Metricas operativas por etapa (ingesta, process, rendicion).
2. Endpoint de dashboard operacional (tasas de REVIEW_REQUIRED, warnings, overrides).
3. Ampliar pruebas reales con lote extendido de `doc_pruebas` y reporte comparativo.

Comando de validacion rapido al retomar:
- `pnpm run test:unit`

## Estado de avance (2026-05-13)
- Punto 1 completado: Ingesta base + idempotencia + endpoint de consulta.
- Punto 2 completado: Pipeline de procesamiento por documento + mapeo de plantilla + warnings no bloqueantes.
- Punto 3 completado: Generacion de rendicion XLSX y endpoint de consulta de rendicion.
- Punto 4 completado: Worker inicial para procesar pendientes automaticamente.
- Punto 5 completado: Correlation ID de extremo a extremo en API y auditoria.
- Prueba real ejecutada con `doc_pruebas`: flujo E2E OK, pendiente precision OCR real.
- Parser PDF real integrado y re-prueba ejecutada: documentos pasaron a `COMPLETED`.
- Cierre beta v3 ejecutado con `doc_pruebas`: `warnings` de 30 a 1 en flujo real.
- Fase siguiente iniciada/completada (Sprint 9-10 base): validaciones tributarias y flujo de revision manual.

Resumen tecnico implementado:
- Endpoints disponibles: `POST /api/v1/documents/upload`, `GET /api/v1/documents/{id}`, `POST /api/v1/documents/{id}/process`, `POST /api/v1/documents/{id}/override`, `POST /api/v1/renditions/generate`, `GET /api/v1/renditions/{id}`.
- Politica vigente: campos faltantes se exportan en blanco y generan warning auditable.
- Pruebas unitarias vigentes: flujo upload -> process -> rendition OK.
- Evidencia de prueba real: ver `docs/REAL_TEST_REPORT_2026-05-13.md`.
- Mejora comprobada en prueba real: `warnings` de 30 a 23 y `REVIEW_REQUIRED` de 3/3 a 0/3.
- Mejora final comprobada en prueba real v3: `warnings` 23 -> 1 manteniendo 3/3 en `COMPLETED`.

## Beta Readiness (v3)
- Estado general beta: 10/10 para piloto controlado.
- Evidencia: `docs/REAL_TEST_REPORT_2026-05-13.md`.
- Riesgo residual: robustez estadistica en mayor volumen de plantillas/formatos (mitigable con ampliacion de dataset).

## Epic 1: Ingesta y Registro de Documentos

### US-101 Subir documento tributario
Estado: COMPLETADO (MVP)
Criterio:
- Given un archivo valido PDF/JPG/PNG
- When se envia a POST /api/v1/documents/upload
- Then se crea documento en estado RECEIVED con document_id unico

Tareas tecnicas:
- Endpoint upload + validacion de mime/tamano.
- Hash SHA-256 para idempotencia.
- Persistir metadata inicial en documents.
- Publicar job en cola.

### US-102 Idempotencia y duplicados
Estado: COMPLETADO (MVP)
Criterio:
- Given archivo previamente subido
- When se vuelve a cargar
- Then retorna mismo document_id o estado DUPLICATE sin reprocesar

Tareas tecnicas:
- Indice unico por tenant_id + document_hash.
- Politica configurable strict/relaxed.

## Epic 2: Pipeline OCR y Parsing

### US-201 Clasificacion documental
Estado: COMPLETADO (MVP simulado)
Criterio:
- Given documento recibido
- When corre el worker
- Then devuelve document_type, country_code, confidence

Tareas tecnicas:
- Servicio classifier con fallback.
- Guardar ClassificationResult y evidencia.

### US-202 Extraccion Chile
Criterio:
- Given boleta/factura chilena
- When se procesa
- Then extrae al menos numero, fecha, proveedor, rut, total, impuestos

Tareas tecnicas:
- Adapter Chile DTE/ticket.
- Normalizacion RUT y montos CLP.

### US-203 Extraccion internacional
Criterio:
- Given invoice/receipt EN o ES
- When se procesa
- Then extrae numero, fecha, tax_id, moneda, total

Tareas tecnicas:
- Adapter internacional base.
- Normalizacion de moneda y fechas.

## Epic 3: Mapeo a Plantilla de Rendicion

### US-301 Completar cabecera
Estado: COMPLETADO (MVP)
Campos:
- Responsable, Rut, Periodo, Monto a pagar, Fecha, Autorizado por.

Criterio:
- Given resultado normalizado
- When se genera rendicion
- Then completa los campos disponibles y deja en blanco los faltantes

Tareas tecnicas:
- Reglas de origen por campo (tributario/interno/derivado).
- Warning no bloqueante para faltantes.

### US-302 Completar detalle por fila
Estado: COMPLETADO (MVP)
Campos:
- Mes, Cuenta, Descripcion Cuenta, Fecha, Nro Boleta Factura, Descripcion del gasto, Concepto, Centro Costo, PROVEEDOR, RUT, Observaciones, Total.

Criterio:
- Given uno o varios documentos
- When se exporta XLSX
- Then cada fila se mapea por regla y nunca falla por campos vacios

Tareas tecnicas:
- Motor Template Mapping Engine.
- Exportador XLSX sobre plantilla 01 Rendicion de gastos 2025.

### US-303 Rescate maximo de datos tributarios
Estado: COMPLETADO (MVP)
Criterio:
- Given datos extra no mapeados a columnas
- When termina el procesamiento
- Then se guardan en extra_fields y audit_events

Tareas tecnicas:
- Schema JSONB extra_fields.
- Persistencia de raw_extraction con versionado.

## Epic 4: Reglas, Revision Manual y Auditoria

### US-401 Validacion contable/tributaria
Estado: COMPLETADO (MVP)
Criterio:
- Then valida subtotal + impuestos = total (cuando aplique)
- Then valida rut/tax_id con formato del pais

### US-402 Revision manual
Estado: COMPLETADO (MVP)
Criterio:
- Given confidence < umbral
- When finaliza parsing
- Then estado REVIEW_REQUIRED y tarea de revision

### US-403 Override y trazabilidad
Estado: COMPLETADO (MVP)
Criterio:
- Given usuario corrige un campo
- When guarda cambios
- Then se registra override con before/after y usuario

## Epic 5: Observabilidad, Seguridad y Rendimiento

### US-501 Observabilidad minima
Estado: COMPLETADO (MVP)
Tareas:
- Correlation ID extremo a extremo.
- Metricas: tiempo OCR, parsing, export, tasa de warnings.
- Dashboards y alertas base.

### US-502 Seguridad de entrada
Tareas:
- Limite de peso y tipo archivo.
- Sanitizacion de nombre.
- Escaneo antivirus opcional.

### US-503 Rendimiento objetivo
Tareas:
- p95 sync < 2s en endpoints de consulta.
- p95 async < 30s procesamiento estandar.

## Priorizacion de arranque (Sprint 1)
1. US-101
2. US-102
3. US-201
4. US-301
5. US-302

## Dependencias
- OCR provider configurado.
- Base de datos y Redis operativos.
- Plantilla XLSX oficial versionada en docs.
