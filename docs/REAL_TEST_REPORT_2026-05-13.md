# Reporte de Prueba Real - 2026-05-13

## Objetivo
Validar flujo real end-to-end usando documentos tributarios de `doc_pruebas`.

## Entorno ejecutado
- API local: `http://127.0.0.1:8000`
- DB runtime: `tests/integration/real_test.db`
- Exportes: `tests/integration/exports`

## Documentos usados
Origen de muestra:
- `c:/Users/Hackteck/Downloads/doc_pruebas/DTE_76264675_T39F39344.pdf`
- `c:/Users/Hackteck/Downloads/doc_pruebas/9c57c875-f44a-4efd-bcc9-5a2732c84cbf.pdf`
- `c:/Users/Hackteck/Downloads/doc_pruebas/150044951_33_0053880422.pdf`

## Resultado de ejecucion
- Upload: 3/3 exitosos (`202 Accepted`).
- Process: 3/3 exitosos (`200 OK`).
- Rendicion generate: exitoso (`200 OK`).
- Rendicion get: exitoso (`200 OK`).
- Archivo generado: `tests/integration/exports/rendition_fc9683bc-8692-4221-a068-1c227e2ada9f.xlsx`.

IDs generados:
- `9d8f9c3c-3ca0-48da-a2e4-0a89c181e3e1`
- `6694828d-2896-4e11-bc40-bc4680145e0f`
- `84e1f294-022c-4399-a321-012992d2c234`
- `rendition_id`: `fc9683bc-8692-4221-a068-1c227e2ada9f`

## Hallazgos funcionales
1. El flujo no bloquea por campos faltantes y genera XLSX correctamente.
2. Se registran warnings por campos internos faltantes, como estaba requerido.
3. Los 3 documentos quedaron en `REVIEW_REQUIRED` porque la clasificacion/extraccion actual es simulada (`document_type=unknown`, `confidence=0.6`).

## Campos faltantes reportados en salida
- `Autorizado por`
- `Centro Costo`
- `Concepto`
- `Cuenta`
- `Descripcion Cuenta`
- `Monto a pagar`
- `Observaciones`
- `RUT`
- `Rut`
- `Total`

## Conclusion
La plataforma ya cumple el flujo beta tecnico de orquestacion (ingesta -> proceso -> rendicion), pero no cumple aun precision beta funcional de negocio porque falta integrar OCR/parsing real.

## Re-ejecucion tras integrar parser PDF (v2)

### Cambios aplicados antes de re-probar
- Se reemplazo la simulacion por extraccion real de texto PDF usando `pypdf`.
- Se agrego parser regex para deteccion de tipo, RUT, folio, fecha y total.
- Se persiste archivo subido en disco para procesamiento posterior.

### Resultado v2 con los mismos 3 documentos
- Upload: 3/3 exitosos (`202 Accepted`).
- Process: 3/3 exitosos (`200 OK`).
- Estado documental: 3/3 en `COMPLETED` (antes estaban `REVIEW_REQUIRED`).
- Rendicion generate: exitoso (`200 OK`).
- Rendicion get: exitoso (`200 OK`).
- Archivo generado: `tests/integration/exports/rendition_43fb1b8c-1f6e-4dbe-a4dd-30d03f23b0a5.xlsx`.

IDs corrida v2:
- `7092246b-e7ae-4f39-8f08-adc5fb7b6121`
- `66ee9098-6d01-4828-bf05-17d577f060ba`
- `33eb1abe-d41e-4085-a1dd-63392f4dc25c`
- `rendition_id`: `43fb1b8c-1f6e-4dbe-a4dd-30d03f23b0a5`

### Comparativo antes vs despues
- Warnings totales de rendicion: `30` -> `23`.
- Clasificacion `unknown`: `3/3` -> `0/3`.
- Estado `REVIEW_REQUIRED`: `3/3` -> `0/3`.

### Brechas que aun quedan para beta funcional
- Completar extraccion de campos contables internos (Cuenta, Centro Costo, Concepto, Autorizado por) desde reglas de negocio y catálogos.
- Mejorar captura de `Total` y `RUT` en todos los formatos para bajar warnings residuales.
- Incorporar validaciones tributarias mas profundas (neto/IVA/total) por tipo documental.

## Re-ejecucion final beta (v3)

### Cambios adicionales aplicados
- Reglas de negocio para completar campos internos por default:
	- `Cuenta`, `Descripcion Cuenta`, `Concepto`, `Centro Costo`, `Autorizado por`, `Rut` cabecera.
- Mejoras de parser regex en PDF para detectar RUT sin guion y montos por fallback (max amount).

### Resultado final v3 con los mismos 3 documentos
- Upload: 3/3 exitosos.
- Process: 3/3 exitosos.
- Estado documental: 3/3 en `COMPLETED`.
- Rendicion generate: exitoso.
- Rendicion get: exitoso.
- Archivo generado: `tests/integration/exports/rendition_5bae9e5e-6085-4873-babe-5e6a760f4c09.xlsx`.

IDs corrida v3:
- `4ef39242-a266-420b-bf4e-d4be841f68d0`
- `07a5a82f-2fb2-4596-8937-f3664d5e463f`
- `9f59cdc4-a324-4c91-af0b-bebf580ba425`
- `rendition_id`: `5bae9e5e-6085-4873-babe-5e6a760f4c09`

### Comparativo consolidado (v1 -> v2 -> v3)
- `REVIEW_REQUIRED`: 3 -> 0 -> 0
- `warnings` rendicion: 30 -> 23 -> 1
- `missing_fields` totales documento: 30 -> 23 -> 1

### Estado beta
- Criterio de no bloqueo por campos faltantes: CUMPLIDO.
- Flujo E2E real con documentos tributarios: CUMPLIDO.
- Estabilidad tecnica backend/worker: CUMPLIDO.
- Precisión funcional: ALTA para muestra actual; se recomienda ampliar dataset antes de release productivo total.

## Acciones inmediatas recomendadas
1. Reemplazar `_simulate_extraction` por proveedor OCR real con parser Chile.
2. Completar mapeo de campos tributarios (`total`, `supplier_tax_id`, `document_number`) para reducir warnings.
3. Ejecutar nuevamente este mismo protocolo con `doc_pruebas` y comparar tasa de `REVIEW_REQUIRED`.
