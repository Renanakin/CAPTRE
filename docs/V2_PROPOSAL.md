# Propuesta V2 - Capturador Datos

## 1) Vision
Construir una plataforma productiva para procesamiento contable de documentos de gasto con soporte multi-moneda, alta trazabilidad y operacion segura a escala.

## 2) Alcance funcional
- Ingesta de PDF/imagen por API.
- OCR + parser por proveedor (plugin strategy).
- Extraccion de: proveedor, folio, fechas, moneda, subtotal, tax, total, amount_due.
- Conversion USD->CLP historica por fecha documento.
- Validacion contable configurable por perfil y pais.
- Persistencia dual (monto origen + monto CLP + metadata FX).
- Exportes CSV/XLSX y endpoints de consulta.
- Auditoria completa de decisiones de parsing y FX.
- Generacion de documento de salida basado en campos de plantilla Excel objetivo.
- Si un campo solicitado por la plantilla no existe en la extraccion, se deja en blanco.
- Campos en blanco por ausencia de dato no deben producir error ni rechazar el documento.

### 2.1 Requerimiento documental ampliado
El sistema V2 debe soportar de forma productiva:
- Boletas chilenas (boleta afecta/exenta, boleta electronica, tickets).
- Facturas chilenas (factura afecta/exenta, factura electronica).
- Documentacion internacional (invoices/receipts/credit notes) con variaciones de idioma, formato y moneda.

Campos minimos obligatorios para cobertura internacional:
- Emisor/receptor, tax id local (RUT/VAT/EIN cuando aplique), numero de documento.
- Fecha emision y fecha vencimiento.
- Moneda origen, subtotal, impuestos, total, monto a pagar.
- Pais origen, tipo documento normalizado y nivel de confianza de extraccion.

### 2.2 Campos de la plantilla de rendicion (segun imagen en docs)
Campos de cabecera a completar en documento de salida:
- Responsable
- Rut
- Periodo
- Monto a pagar
- Fecha
- Autorizado por

Campos de detalle (tabla) a completar por fila:
- Mes
- Cuenta
- Descripcion Cuenta
- Fecha
- Nro Boleta Factura
- Descripcion del gasto
- Concepto
- Centro Costo
- PROVEEDOR
- RUT
- Observaciones
- Total

Reglas de llenado para estos campos:
- Si el campo existe en la extraccion tributaria, se completa.
- Si no existe o no tiene confianza suficiente, se deja en blanco.
- Campo en blanco no genera error bloqueante ni rechazo de documento.
- El proceso debe generar siempre el archivo final de rendicion.

Nota funcional:
- Algunos campos son de uso interno (por ejemplo Cuenta, Centro Costo, Autorizado por) y pueden venir desde reglas de negocio, configuracion o carga manual.
- Campos propios del documento tributario deben priorizarse desde extraccion automatica.

### 2.3 Matriz de mapeo (plantilla -> origen -> fallback)
| Campo plantilla | Origen primario (documento tributario) | Fallback / regla si falta | Tipo |
|---|---|---|---|
| Responsable | No tributario (perfil usuario/solicitante) | Configuracion de usuario o vacio | Interno |
| Rut (cabecera) | No tributario (perfil usuario/empresa) | Configuracion de empresa o vacio | Interno |
| Periodo | Fecha emision del documento | `YYYY-MM` desde fecha proceso o vacio | Derivado |
| Monto a pagar | `amount_due` o `total` | Si no existe, vacio | Tributario |
| Fecha (cabecera) | Fecha de rendicion/proceso | Fecha actual del sistema o vacio | Interno |
| Autorizado por | Flujo de aprobacion interno | Vacio hasta aprobacion | Interno |
| Mes | Fecha emision (`issue_date`) | Mes derivado de fecha proceso o vacio | Derivado |
| Cuenta | No tributario (plan de cuentas) | Regla contable por proveedor/concepto o vacio | Interno |
| Descripcion Cuenta | No tributario (catalogo contable) | Segun Cuenta o vacio | Interno |
| Fecha (detalle) | `issue_date` | Fecha de recepcion o vacio | Tributario |
| Nro Boleta Factura | Folio/numero documento (`document_number`) | Correlativo interno temporal o vacio | Tributario |
| Descripcion del gasto | Glosa/descripcion de item o documento | Nombre proveedor + tipo doc o vacio | Tributario |
| Concepto | Clasificacion del gasto (regla/IA) | Categoria "Sin clasificar" o vacio | Derivado |
| Centro Costo | No tributario (ERP/regla interna) | Regla por responsable/proveedor o vacio | Interno |
| PROVEEDOR | Razon social emisor (`supplier_name`) | Nombre comercial detectado o vacio | Tributario |
| RUT (detalle) | RUT/VAT/EIN emisor (`supplier_tax_id`) | Normalizar formato local o vacio | Tributario |
| Observaciones | Notas del documento, warnings o comentarios usuario | Vacio | Mixto |
| Total | `total` | Si no existe, `amount_due`; si no, vacio | Tributario |

Reglas transversales de la matriz:
- Priorizar siempre dato tributario extraido antes de reglas internas.
- Si el dato existe pero la confianza es baja, marcar warning y permitir override manual.
- Ningun campo faltante bloquea la generacion del archivo de salida.
- Todo campo tributario no mapeado a columna se guarda en `extra_fields`.

## 3) Arquitectura propuesta
- API Layer (FastAPI): auth, idempotencia, endpoints de dominio.
- Orchestration Layer: cola + workers para OCR y enrichment.
- Domain Layer: reglas de negocio, validadores, conversion FX.
- Data Layer: PostgreSQL + Redis cache + object storage.
- Observability: logs estructurados, metricas, trazas, alertas.
- Security: JWT/service auth, secretos por vault, hardening de inputs.

## 4) Componentes V2
- `Document Intake Service`
- `OCR Extraction Service`
- `Provider Parser Engine`
- `Currency & FX Service`
- `Accounting Validation Engine`
- `Registration Service`
- `Export Service`
- `Audit & Evidence Service`
- `Monitoring & Alerting Stack`

## 5) Modelo de datos (resumen)
Tabla `documents`: metadatos documento, estado pipeline, hash/idempotencia.
Tabla `document_details`: campos monetarios origen + CLP + FX metadata.
Tabla `fx_rates`: cache de tasas por fecha/fuente.
Tabla `audit_events`: eventos de decisiones, errores, overrides.

## 6) Roadmap de desarrollo
- Fase 0: bootstrap repo, CI, quality gates, contenedores.
- Fase 1: ingestion + OCR baseline + clasificador documental (CL vs internacional).
- Fase 2: parsers especializados Chile (boletas/facturas) + validadores tributarios locales.
- Fase 3: parsers internacionales por region + normalizacion de campos globales.
- Fase 4: FX historico oficial + validadores contables por pais.
- Fase 5: exportes empresariales + panel operativo minimo.
- Fase 6: hardening productivo (SLO, seguridad, runbooks, DR).

## 6.1 Propuesta tecnica para cumplir el requerimiento
### A. Pipeline de extraccion por capas
1. Clasificacion documental:
- Detecta tipo (boleta/factura/otro) y pais probable.
- Salida: `document_type`, `country_code`, `confidence`.

2. OCR hibrido:
- Motor OCR principal con fallback para baja confianza.
- Normaliza bloques por layout (cabecera, totales, impuestos, items).

3. Parser por adaptadores:
- Adaptadores Chile: reglas RUT, IVA, folio, formatos DTE frecuentes.
- Adaptadores internacionales: reglas por region (LATAM, US, EU) con mapeo comun.

4. Normalizacion canonica:
- Convierte toda salida a contrato unico `ExtractionResult`.
- Mantiene evidencia (`raw_text`, `bbox`, `page`) para auditoria.

5. Validacion de negocio:
- Reglas por pais/tipo: consistencia subtotal + impuestos = total, fechas validas, moneda valida.
- Motor de excepciones para revision manual cuando confianza < umbral.

### B. Estrategia de datos y precision
- Dataset inicial etiquetado por categoria: boletas CL, facturas CL, internacionales.
- Metricas por categoria: precision de campos criticos, recall de deteccion de tipo, tasa de derivacion manual.
- Entrenamiento incremental: cada correccion manual retroalimenta reglas y prompts.

### C. Operacion y escalamiento
- Cola asincrona para OCR/parsing masivo.
- Idempotencia por hash documento y control de duplicados.
- Observabilidad por etapa (ingesta, OCR, parser, validacion, export) con trazabilidad completa.

### D. Regla de completitud de salida (Excel)
- El contrato de salida se define por encabezados de la plantilla Excel de rendicion.
- El proceso siempre intenta generar el documento final aunque existan campos no encontrados.
- Los campos no encontrados se persisten/exportan como valor vacio (blank/null segun formato).
- La ausencia de campos se registra como warning auditable, no como error bloqueante.

### E. Politica de rescate maximo tributario
- Todo dato detectable del documento tributario debe rescatarse, aunque no exista columna directa en la plantilla.
- Los datos extra se guardan en metadata estructurada (`raw_extraction`/`extra_fields`) para auditoria y uso futuro.
- Ejemplos de datos a rescatar adicionalmente: razon social emisor, giro, direccion, comuna, tipo DTE, folio, neto, exento, IVA, descuentos, propinas, medio de pago.

## 6.2 Entregables por etapa
- E1: Clasificador documental + contrato de datos comun.
- E2: Cobertura Chile (boletas/facturas) con validacion tributaria minima.
- E3: Cobertura internacional inicial (ES/EN, multimoneda).
- E4: Loop de mejora continua con QA documental y reglas avanzadas.

## 7) Calidad y seguridad obligatoria
- Lint/format/test en CI.
- Coverage objetivo >= 85%.
- SAST (bandit), dependencias (pip-audit), secrets scan.
- Contratos API versionados + pruebas de regresion por proveedor.

## 8) Criterios de exito
- Precision extraccion >= 95% en dataset validado.
- Error de conversion monetaria = 0 en casos UAT aprobados.
- Tiempos: p95 de validacion sync < 2s, procesamiento async p95 < 30s.
- Disponibilidad mensual API >= 99.9%.

Objetivos adicionales por cobertura:
- Chile (boletas/facturas): precision campos criticos >= 97%.
- Internacional: precision campos criticos >= 93% en fase inicial y >= 95% en fase madura.
- Tasa de documentos enviados a revision manual <= 15% en produccion inicial.

## 9) Riesgos clave y mitigacion
- Cambios de template proveedor -> parser por estrategia + tests de snapshot.
- Caida proveedor FX -> cache + fallback controlado + alertas.
- Ambiguedad de fechas -> ranking de fecha + evidencia auditada.

## 10) Entregables v2
- Backend API + workers productivos.
- Migraciones y contrato de datos estable.
- Observabilidad y seguridad operativas.
- Manual de operacion, rollout y rollback.
