# Plan de Ejecucion de Desarrollo V2

## Objetivo
Dejar operativo un flujo productivo para leer boletas/facturas Chile y documentos internacionales, generando la plantilla de rendicion con politica no bloqueante de campos faltantes.

## Alcance de implementacion (MVP Productivo)
- Ingesta de archivos por API (PDF, JPG, PNG).
- Clasificacion documental (tipo + pais + confianza).
- OCR y parsing tributario (Chile + internacional base EN/ES).
- Normalizacion a contrato canonico.
- Mapeo a plantilla de rendicion de gastos.
- Export XLSX con campos faltantes en blanco.
- Persistencia de campos extra tributarios en metadata.
- Flujo de revision manual para baja confianza.
- Auditoria completa y observabilidad minima.

## Supuestos
- Se mantiene arquitectura modular monolith en V2.
- PostgreSQL como fuente de verdad.
- Cola asincrona con Redis.
- OCR LLM configurable por proveedor.

## Orden de construccion recomendado
1. Esquema de datos + migraciones base.
2. Contratos API + validaciones de entrada.
3. Pipeline worker: clasificacion -> OCR -> parser -> normalizacion.
4. Motor de mapeo a plantilla + export XLSX.
5. Reglas contables/tributarias + warnings.
6. Revision manual + overrides.
7. Observabilidad + hardening + pruebas de carga.

## Equipo minimo sugerido
- 1 Tech Lead Backend.
- 2 Backend Engineers (API + Worker).
- 1 Data/OCR Engineer.
- 1 QA Engineer.
- 1 Product/Analyst part-time.

## Definition of Ready (DoR)
- Historia con criterio Given/When/Then.
- Campos de entrada/salida definidos.
- Dependencias externas identificadas.
- Estrategia de test definida.

## Definition of Done (DoD)
- Codigo mergeado con CI verde.
- Tests unitarios/integracion pasando.
- Logging estructurado y metricas minimas.
- Documentacion actualizada.
- Criterios funcionales verificados en QA.

## Cadencia sugerida (12 semanas)
- Semana 1-2: Base tecnica y contratos.
- Semana 3-4: OCR/parsing baseline.
- Semana 5-6: Cobertura Chile completa.
- Semana 7-8: Internacional + plantilla completa.
- Semana 9-10: Seguridad y performance.
- Semana 11-12: UAT, release y hypercare.

## Riesgos criticos y mitigacion
- Variabilidad alta de templates: parser adaptativo + snapshots.
- Baja precision OCR en imagenes malas: fallback OCR + revision manual.
- Falta de campos internos: defaults + tablas de configuracion + warnings.
- Dependencia externa FX/OCR: cache + circuit breaker + reintentos.

## Entregables para inicio inmediato
- Backlog ejecutable: ver docs/IMPLEMENTATION_BACKLOG.md.
- Contratos API: ver docs/API_CONTRACTS.md.
- Modelo de datos: ver docs/DATA_MODEL_SPEC.md.
- QA/aceptacion: ver docs/QA_ACCEPTANCE_TEST_PLAN.md.
