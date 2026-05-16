# Sprint 1 - Taskboard de Arranque (2 semanas)

## Objetivo sprint
Dejar flujo minimo extremo a extremo: upload -> procesamiento -> mapeo plantilla -> export con campos faltantes en blanco.

## Estado actual (2026-05-13)
- Flujo extremo a extremo implementado en API.
- Worker inicial implementado para procesar documentos pendientes.
- Suite unitaria actual: 7 pruebas pasando.
- Prueba real final v3 con `doc_pruebas`: 3/3 COMPLETED y 1 warning total en rendicion.

## Cierre de sprint
- Estado: CERRADO
- Beta readiness para piloto controlado: 10/10

## Avance post-sprint (fase siguiente)
- Validacion tributaria/contable implementada en procesamiento.
- Bandeja de revision manual implementada (`/api/v1/reviews/pending`).
- Resolucion de revision implementada (`/api/v1/reviews/{document_id}/resolve`).
- Pruebas unitarias actuales: 8 passing.

## Checkpoint para retomar
- Retomar desde: metrica y monitoreo operativo (fase Sprint 9-10).
- Bloque siguiente: dashboard de salud funcional y calidad de extraccion.
- Validacion previa de arranque: correr suite unitaria y una corrida real con `doc_pruebas`.

## Historias incluidas
- US-101 Subir documento tributario
- US-102 Idempotencia y duplicados
- US-201 Clasificacion documental
- US-301 Completar cabecera
- US-302 Completar detalle por fila

## Tareas por rol

### Backend API
- Crear endpoint POST /documents/upload
- Crear endpoint GET /documents/{id}
- Validacion mime/tamano/hash
- Persistencia de documents
- Estado: COMPLETADO

### Backend Worker
- Consumidor de cola base
- Clasificador documental stub + interfaz proveedor
- Pipeline de estados PROCESSING/COMPLETED/FAILED
- Estado: COMPLETADO (MVP con polling de pendientes y llamada a /process)

### Mapping/Export
- Implementar Template Mapping Engine
- Resolver campos cabecera y detalle
- Export XLSX sobre plantilla oficial
- Warning no bloqueante por campo faltante
- Estado: COMPLETADO

### Data
- Migracion tablas documents, document_extractions, document_template_mapping, audit_events
- Indices de idempotencia
- Estado: COMPLETADO (migracion inicial)

### QA
- Set de pruebas smoke (upload, duplicate, export)
- Caso principal: campo faltante en blanco sin error
- Estado: COMPLETADO (unit tests de flujo y worker)

## Criterios de demo
- Se sube archivo y retorna document_id
- Documento llega a COMPLETED
- Se genera XLSX con datos mapeados
- Campo faltante queda en blanco y warning registrado
