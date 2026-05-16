# Roadmap Maestro - capturador_datos_v2

## Objetivo
Convertir el MVP actual en una plataforma productiva de rendiciones contables con 3 capas activas:
- Front: interfaz operativa para carga, revision y rendiciones.
- Back: orquestacion de negocio, procesamiento documental, OCR, reglas y workers.
- API: contratos REST, seguridad, auditoria, integracion y exposicion publica.

## Arquitectura objetivo
- Capa Front: `apps/front`
- Capa Back: `apps/back`
- Capa API: `apps/api`
- Componentes de soporte: `apps/worker`, `libs/common`, `infra`, `migrations`, `tests`

## Plugins, agentes y skills operativos

### Estandar obligatorio de ejecucion
- Todos los comandos operativos del repositorio se ejecutan via `pnpm` desde la raiz.
- Scripts base obligatorios:
  - `pnpm run api:dev`
  - `pnpm run test:unit`
  - `pnpm run test:integration:health`
  - `pnpm run test:all`

### Plugins priorizados
- Browser: validacion funcional E2E de frontend y pruebas sobre localhost.
- GitHub (cuando aplique): gestion de issues, PR y seguimiento de entregas.
- Spreadsheets (opcional): verificacion estructural de salida XLSX.

### Agentes por tipo de trabajo
- `worker`:
  - Implementacion de features, refactor, pruebas, migraciones.
- `explorer`:
  - Analisis rapido de codigo, contratos y riesgos antes de cambios.

### Skills base que se adoptan en TODO el proyecto
- `agent-governance`: coordinacion de trabajo multiagente y ownership claro.
- `security-best-practices`: hardening de API, manejo de archivos y JWT.
- `refactor`: refactor incremental sin romper contratos.
- `pytest-coverage`: estrategia de tests y cobertura.
- `frontend-responsive-design-standards`: calidad UI responsive.
- `playwright`: pruebas funcionales y smoke tests de frontend.
- `create-implementation-plan`: planes por sprint ejecutables.

## Fases del roadmap

## Fase 0 - Baseline y gobierno tecnico (Semana 1)
Objetivo: ordenar el proyecto para escalar sin deuda accidental.

Estado: CERRADA (2026-05-15)

Arranque ejecutado:
- Lectura y alineacion de lineamientos en README/SKILLS de raiz y docs.
- Activacion de checklist operativo de Fase 0 en `docs/FASE_0_BASELINE_GOBIERNO_CHECKLIST.md`.
- Matriz de riesgos inicial activa en `docs/FASE_0_MATRIZ_RIESGOS.md`.

Resultado esperado de cierre de Fase 0:
- Baseline tecnico documentado y medible.
- Reglas de trabajo estandarizadas para las capas Front/Back/API.
- Riesgos tecnicos priorizados con mitigaciones y owner.

Resultado de cierre alcanzado:
- Baseline de pruebas ejecutado y validado con comando canonico por contexto.
- Checklist operativo activo: `docs/FASE_0_BASELINE_GOBIERNO_CHECKLIST.md`.
- Matriz de riesgos inicial activa: `docs/FASE_0_MATRIZ_RIESGOS.md`.

Entregables:
- Estructura por capas oficial (`front/back/api`) y lineamientos en README/SKILLS.
- Convenciones de ramas, commits, revision y definicion de done.
- Matriz de riesgos tecnicos y metricas de calidad.

Asignacion:
- Agente principal: `explorer` (levantamiento) + `worker` (estandarizacion).
- Skills: `agent-governance`, `create-implementation-plan`, `refactor`.

## Fase 1 - API/Backend estable y modular (Semanas 2-4)
Objetivo: separar responsabilidades y robustecer base tecnica.

Estado: CERRADA (2026-05-15)

Arranque ejecutado:
- Se habilito estructura modular explicita en API: `routes`, `services`, `repositories`, `models`, `schemas`.
- Primer endpoint migrado a arquitectura por capas: `GET /api/v1/health` ahora via router (`app/api/v1/routes/health.py`) y service (`app/services/health_service.py`).

Resultado de cierre alcanzado:
- `apps/api/app/main.py` quedo como ensamblador (middleware + include_router).
- Endpoints de documentos migrados a router dedicado: `app/api/v1/routes/documents.py`.
- Endpoints de revision migrados a router dedicado: `app/api/v1/routes/reviews.py`.
- Endpoints de rendiciones migrados a router dedicado: `app/api/v1/routes/renditions.py`.
- Logica de negocio consolidada en `app/services/document_service.py`.
- Persistencia y bootstrap de esquema SQL movidos a `app/repositories/document_repository.py`.
- Contratos de request movidos a `app/schemas/documents.py`.
- Pruebas de validacion de cierre:
  - Unit API: 6 passed.
  - Unit worker: 2 passed.
  - Integration health: 1 passed.

Entregables:
- Refactor de `apps/api/app/main.py` a capas:
  - routes
  - services
  - repositories
  - models
  - schemas
- Estandarizacion de estados documentales.
- Endpoints minimos faltantes de documentos/reviews/renditions.
- Logs estructurados y manejo unificado de errores.

Asignacion:
- Agente principal: `worker`.
- Skills: `refactor`, `security-best-practices`, `pytest-coverage`.

## Fase 2 - Persistencia productiva y cola real (Semanas 5-7)
Objetivo: pasar de SQLite/polling a stack productivo.

Estado: CERRADA (2026-05-15)

Resultado de cierre alcanzado:
- Persistencia migrada a SQLAlchemy con compatibilidad SQLite/PostgreSQL en `apps/api/app/repositories/document_repository.py`.
- Migraciones Alembic funcionales en `apps/api/alembic` (revision inicial `20260515_01`).
- Scripts pnpm de base de datos y ejecución:
  - `pnpm run db:migrate`
  - `pnpm run worker:dev`
- Integración de cola Redis real:
  - Encolado de documentos al subir archivo (`app/core/queue.py`).
  - Consumo en worker desde Redis (`REDIS_QUEUE_NAME=document-processing`).
- Worker desacoplado de llamadas HTTP internas:
  - El worker ejecuta procesamiento invocando servicio de dominio directamente (sin POST interno a API).
- Configuración productiva declarada en `docker-compose.yml`:
  - `DATABASE_URL` PostgreSQL.
  - `REDIS_URL` y nombre de cola.

Evidencia de validación:
- `pnpm run db:migrate` ejecutado con éxito.
- `pnpm run test:all` en verde (unit API + unit worker + integration health).

Entregables:
- SQLAlchemy + Alembic.
- PostgreSQL como DB principal.
- Redis + cola real (RQ o Celery) para procesamiento asincrono.
- Worker desacoplado de llamadas HTTP internas.

Asignacion:
- Agente principal: `worker`.
- Skills: `refactor`, `pytest-coverage`, `security-best-practices`.

## Fase 3 - Revision manual completa (Semanas 8-9)
Objetivo: cerrar flujo operativo para contadores.

Estado: CERRADA (2026-05-15)

Resultado de cierre alcanzado:
- Endpoints completos de revisión implementados:
  - `GET /api/v1/reviews/pending`
  - `GET /api/v1/reviews/{document_id}` (detalle)
  - `POST /api/v1/reviews/{document_id}/overrides`
  - `POST /api/v1/reviews/{document_id}/approve`
  - `POST /api/v1/reviews/{document_id}/reject`
  - `POST /api/v1/reviews/{document_id}/resolve` (compatibilidad)
- Trazabilidad completa de revisión incorporada en `review_tasks`:
  - `reviewer_id`, `decision`, `resolution_reason`, `resolved_at`.
- Registro detallado de warnings y cambios manuales disponible en detalle de revisión:
  - warnings de documento/revisión
  - historial de cambios manuales desde `audit_events`.

Evidencia de validación:
- `pnpm run test:all` en verde.
- Suite API actualizada a 7 pruebas unitarias passing (incluye flujo de detalle/overrides/reject).

Entregables:
- Endpoints completos de revision:
  - pending
  - detalle
  - approve
  - reject
  - overrides
- Trazabilidad de revisor, fecha y motivo.
- Registro detallado de warnings y cambios manuales.

Asignacion:
- Agente principal: `worker`.
- Skills: `security-best-practices`, `pytest-coverage`.

## Fase 4 - Rendiciones enterprise (Semanas 10-11)
Objetivo: salida Excel confiable para operacion real.

Estado: CERRADA (2026-05-15)

Resultado de cierre alcanzado:
- Generador XLSX consolidado por filtros operativo:
  - `POST /api/v1/renditions/generate/by-filter` con filtros por `tenant_id`, `period`, `responsible`, `center_cost`.
- Descarga de rendiciones implementada:
  - `GET /api/v1/renditions/{rendition_id}/download`.
- Versionado de plantilla persistido por rendicion (`template_version` en tabla `renditions`).
- Auditoria por documento incluido en rendicion:
  - Evento `RENDITION_ITEM_INCLUDED` registrado por documento durante la generacion.
- Endpoint de inspeccion de detalle de rendicion:
  - `GET /api/v1/renditions/{rendition_id}/items`.

Evidencia de validación:
- `pnpm run test:all` en verde.
- Pruebas unitarias de API ampliadas para flujo enterprise de rendiciones.

Entregables:
- Generador XLSX consolidado por filtros (empresa, periodo, usuario, centro de costo).
- Descarga de rendiciones y versionado de plantilla.
- Auditoria por documento incluido en rendicion.

Asignacion:
- Agente principal: `worker`.
- Skills: `pytest-coverage`, `refactor`.
- Plugin recomendado: `Spreadsheets` para validacion de estructura.

## Fase 5 - Frontend operativo (Semanas 12-15)
Objetivo: habilitar uso diario por perfiles de negocio.

Estado: CERRADA (2026-05-15)

Arranque ejecutado:
- SPA operativa implementada en `apps/front`.
- Flujo de pantallas habilitado:
  - Login
  - Dashboard
  - Carga documental
  - Listado y detalle de documentos
  - Bandeja de revision
  - Rendiciones e historial
- Integracion activa con API V1 para upload, reviews y renditions.
- Ejecucion estandarizada via pnpm: `pnpm run front:dev`.

Evidencia de validación:
- Frontend levantado localmente en `http://127.0.0.1:5173` mediante `pnpm run front:dev`.
- Backend y API sin regresiones: `pnpm run test:all` en verde.

Entregables:
- Frontend en `apps/front` con pantallas:
  - Login
  - Dashboard
  - Carga documental
  - Listado y detalle
  - Bandeja de revision
  - Rendiciones e historial
- Integracion contra API versionada.

Asignacion:
- Agente principal: `worker`.
- Skills: `frontend-responsive-design-standards`, `playwright`, `security-best-practices`.
- Plugin prioritario: `Browser` para QA funcional en localhost.

## Fase 6 - OCR avanzado (Semanas 16-18)
Objetivo: soportar escaneados e imagenes con alta robustez.

Estado: CERRADA (2026-05-15)

Resultado de cierre alcanzado:
- Pipeline OCR implementado en `apps/back/app/ocr_pipeline.py`.
- Preprocesamiento de imagen incorporado:
  - correccion de orientacion
  - escala de grises
  - mejora de contraste
  - reduccion de ruido
  - autocontraste
  - recorte de contenido
- Integracion de OCR al flujo de extraccion API:
  - consumo desde `apps/api/app/services/document_service.py`
  - fallback seguro para PDF/imagen cuando OCR no esta disponible.
- Metricas de confianza OCR por documento incorporadas en `extra_fields`:
  - `ocr_confidence`
  - `ocr_metrics` (engine, char_count, word_count, mean_word_confidence, preprocess_steps)
- Configuracion de despliegue preparada para OCR compartido en contenedores:
  - `BACK_CODE_PATH` en API y worker
  - inclusion de `apps/back` en Dockerfile API/worker.

Evidencia de validación:
- `pnpm run test:all` en verde.
- Pruebas unitarias nuevas de pipeline OCR en `tests/unit/test_back_ocr_pipeline.py`.

Validacion GO/NO-GO con documentos reales (actualizacion 2026-05-15):
- Dataset real: carpeta `facturas pagos ia`.
- Ejecucion: `python scripts/run_real_docs_go_nogo.py`.
- Resultado: GO.
- Metricas alcanzadas:
  - output_generated_rate: 1.0
  - review_rate: 0.0
  - chile_precision_proxy: 0.9895
  - international_precision_proxy: 1.0
- Evidencia: `docs/REAL_GO_NOGO_REPORT_2026-05-15.json` y `docs/REAL_GO_NOGO_REPORT_2026-05-15.md`.

Entregables:
- Pipeline OCR en `apps/back` (Tesseract o PaddleOCR).
- Preprocesamiento de imagen (orientacion, contraste, ruido, recorte).
- Metricas de confianza OCR por documento.

Asignacion:
- Agente principal: `worker`.
- Skills: `refactor`, `pytest-coverage`.

## Fase 7 - Extraccion IA y reglas inteligentes (Semanas 19-22)
Objetivo: reducir revision manual y subir precision.

Estado: CERRADA (2026-05-16)

Avance implementado en esta iteracion:
- Modulo inteligente en `apps/back/app/intelligent_extraction.py`:
  - validacion de payloads via Pydantic
  - comparador de candidatos (`regex` y `ai`)
  - score unificado con señal OCR
  - politica de enrutamiento por empresa (`min_confidence_auto_approve` y reglas por tipo documental)
- Integracion en API (`apps/api/app/services/document_service.py`):
  - consumo del modulo inteligente durante `process_document`
  - decision de enrutamiento incorporada al estado final (`COMPLETED` vs `REVIEW_REQUIRED`)
  - trazabilidad de comparacion guardada en `extra_fields.intelligent_routing`
- Pruebas unitarias nuevas:
  - `tests/unit/test_back_intelligent_extraction.py`
  - `tests/unit/test_back_ollama_adapter.py`
- Adaptador Ollama implementado en `apps/back/app/ollama_adapter.py`:
  - consumo de `POST /api/generate`
  - prompt de extraccion JSON estricto
  - parser robusto de bloque JSON en respuesta
  - fallback no bloqueante ante timeout/error
- Integracion efectiva de candidato IA en API:
  - `apps/api/app/services/document_service.py` ahora envia `ai_candidate` al comparador inteligente.
  - trazabilidad de proveedor/modelo seleccionados en `extra_fields.intelligent_routing.selected_candidate_meta`.
- Reglas contables configurables por empresa implementadas:
  - `required_fields_by_country` para forzar revision si faltan campos criticos por pais.
  - `allowed_currencies_by_country` para detectar moneda invalida por pais y enrutar a revision.
  - banderas de validacion expuestas en `extra_fields.intelligent_routing.validation_flags`.
- Validacion con dataset real mantenida en GO:
  - `output_generated_rate=1.0`
  - `review_rate=0.0`
  - `chile_precision_proxy=0.9895`
  - `international_precision_proxy=1.0`

Evidencia de cierre:
- `pnpm run test:all` en verde:
  - unit API: 8 passed
  - unit worker: 2 passed
  - unit back: 11 passed
  - integration health: 1 passed
- `pnpm run qa:real-go-nogo` en verde con dataset real `facturas pagos ia`.
- Reporte actualizado: `docs/REAL_GO_NOGO_REPORT_2026-05-15.json` y `docs/REAL_GO_NOGO_REPORT_2026-05-15.md`.

Entregables:
- Adaptador LLM para extraccion JSON validada con Pydantic.
- Comparador de resultados Regex vs OCR vs IA.
- Score unificado de confianza y politica de enrutamiento.
- Reglas contables configurables por empresa.

Asignacion:
- Agente principal: `worker` + `explorer` para evaluacion tecnica.
- Skills: `security-best-practices`, `pytest-coverage`, `create-implementation-plan`.

## Fase 8 - Seguridad, multiempresa y operacion comercial (Semanas 23-26)
Objetivo: dejar plataforma lista para clientes reales.

Estado: CERRADA (2026-05-16)

Avance implementado en esta iteracion:
- Autenticacion JWT + refresh token:
  - `POST /api/v1/auth/login`
  - `POST /api/v1/auth/refresh`
  - `GET /api/v1/auth/me`
- RBAC aplicado a endpoints criticos de documentos/reviews/renditions (roles: admin, contador, ejecutivo, auditor).
- Aislamiento por `company_id` (tenant) en acceso a documentos y rendiciones.
- Endpoints de observabilidad productiva agregados:
  - `GET /api/v1/liveness`
  - `GET /api/v1/readiness`
- Hardening de uploads:
  - sanitizacion de nombre de archivo
  - validacion de extensiones permitidas

Evidencia de cierre:
- `pnpm run test:all` en verde:
  - unit API: 13 passed
  - unit worker: 2 passed
  - unit back: 11 passed
  - integration health: 1 passed
- Pruebas nuevas/extendidas de seguridad Fase 8:
  - `tests/unit/test_auth_api.py`
  - cobertura de login/me/refresh
  - cobertura de 403 por rol insuficiente
  - cobertura de 403 por acceso cruzado de empresa
  - cobertura de bypass admin multiempresa
- `pnpm run qa:real-go-nogo` en verde con dataset real `facturas pagos ia`:
  - output_generated_rate: 1.0
  - review_rate: 0.0
  - chile_precision_proxy: 0.9895
  - international_precision_proxy: 1.0
- Reporte actualizado:
  - `docs/REAL_GO_NOGO_REPORT_2026-05-15.json`
  - `docs/REAL_GO_NOGO_REPORT_2026-05-15.md`

Entregables:
- JWT + refresh token + RBAC (Admin/Contador/Ejecutivo/Auditor).
- Aislamiento estricto por `company_id`.
- Observabilidad: metricas, alertas, health/readiness/liveness productivos.
- Hardening de uploads y politicas de retencion/auditoria.

Asignacion:
- Agente principal: `worker`.
- Skills: `security-best-practices`, `pytest-coverage`.

## Metricas de exito por fase
- Cobertura tests critica backend/API >= 80%.
- Error rate de procesamiento < 2% en lote validado.
- % documentos enviados a revision manual con tendencia descendente.
- Tiempo promedio de generacion de rendicion dentro de SLA acordado.
- Trazabilidad completa por documento y usuario en auditoria.

## Mapa de ownership por capas
- Front (`apps/front`): UX, flujos de negocio, integracion API, pruebas UI.
- Back (`apps/back` + `apps/worker`): procesamiento documental, OCR, reglas, colas.
- API (`apps/api`): contratos, seguridad, validacion, trazabilidad, exportacion.

## Orden de ejecucion recomendado
1. Fase 0
2. Fase 1
3. Fase 2
4. Fase 3
5. Fase 4
6. Fase 5
7. Fase 6
8. Fase 7
9. Fase 8

## Roadmap por fases - Remediacion integral de seguridad y robustez (post Fase 8)

Objetivo: ejecutar todo lo senalado en el analisis (autenticacion, secretos, hardening, pruebas de seguridad y control operativo) con ownership experto por fase.

### Fase 9 - Contencion critica (Semana 1)
Objetivo: eliminar ventanas de exposicion inmediata en autenticacion y secretos.

Estado: CERRADA (2026-05-16)

Resultado de cierre alcanzado:
- Runtime productivo protegido: la API bloquea arranque si `AUTH_ENABLED=false` en `ENV=prod|production|staging`.
- Runtime productivo protegido: la API bloquea arranque si `SECURITY_JWT_SECRET` es debil/default o menor a longitud minima.
- Runtime productivo protegido: la API bloquea arranque si `DEFAULT_SEED_PASSWORD` mantiene valores inseguros.
- Revocacion masiva de refresh tokens implementada via endpoint admin `POST /api/v1/auth/revoke-all-refresh`.

Evidencia de validacion:
- Pruebas unitarias API en verde: `pnpm run test:unit:api` -> 17 passed.
- Cobertura nueva en `tests/unit/test_auth_api.py` para:
  - rechazo en prod con auth deshabilitada,
  - rechazo en prod con secreto JWT debil,
  - control RBAC y revocacion masiva de refresh tokens.

Entregables:
- Forzar `AUTH_ENABLED=true` en entornos productivos y bloquear startup cuando no cumpla.
- Eliminar defaults inseguros para `SECURITY_JWT_SECRET` y `DEFAULT_SEED_PASSWORD` en runtime productivo.
- Rotacion de secretos JWT y revocacion de sesiones/tokens vigentes.
- Perfil de despliegue sin exposicion publica innecesaria de DB/Redis.

DoD:
- No existe arranque en prod con auth desactivada.
- No existen secretos por defecto en despliegue.
- Evidence pack de rotacion y revocacion completado.

Asignacion experta:
- Agente principal: `Analizador Seguridad de Codigo`.
- Agente implementador: `worker`.
- Agente QA: `explorer`.
- Skills: `security-best-practices`, `security-review`, `agent-governance`.

### Fase 10 - Refuerzo criptografico y credenciales (Semanas 2-3)
Objetivo: migrar de controles minimos a controles resistentes a ataque.

Estado: CERRADA (2026-05-16)

Resultado de cierre alcanzado:
- Migracion de hashing implementada a bcrypt (`bcrypt$...`) con estrategia progresiva desde hash legado SHA-256 + salt.
- Upgrade automatico de hash legado a bcrypt en login exitoso.
- Rotacion obligatoria de password para cuentas bootstrap: login devuelve `403 Password change required` hasta cambio exitoso.
- Endpoint de cambio de password implementado: `POST /api/v1/auth/change-password` con politica de complejidad.
- Seed de usuarios deshabilitado en entornos `prod|production|staging` y controlado por `AUTH_SEED_USERS` en dev/test/local.
- Politica de rotacion de secreto JWT aplicada en runtime productivo (`SECURITY_JWT_ROTATED_AT`, `SECURITY_JWT_MAX_AGE_DAYS`).

Evidencia de validacion:
- `pnpm run test:unit:api` en verde: 19 passed.
- `pnpm run test:all` en verde:
  - unit API: 19 passed
  - unit worker: 2 passed
  - unit back: 11 passed
  - integration health: 1 passed
- Cobertura nueva en `tests/unit/test_auth_api.py` para:
  - rotacion obligatoria bootstrap,
  - rechazo de password debil,
  - upgrade de hash legado a bcrypt,
  - revocacion y politicas runtime productivas.

Entregables:
- Migracion de hashing de password a Argon2id o bcrypt con estrategia progresiva.
- Deshabilitar seed de usuarios por defecto fuera de test/local.
- Politica de password inicial segura y rotacion obligatoria en primer login para cuentas bootstrap.
- Validadores de fortaleza y politicas de expiracion/rotacion en secretos criticos.

DoD:
- 100% de cuentas activas con hash fuerte.
- Bootstrap inseguro deshabilitado en entornos no dev.
- Politicas de credenciales auditables y verificadas por pruebas.

Asignacion experta:
- Agente principal: `Analizador Seguridad de Codigo`.
- Agente apoyo: `Analizador Integral de Codigo`.
- Agente implementador: `worker`.
- Skills: `security-review`, `refactor`, `review-and-refactor`.

### Fase 11 - Hardening de superficie de ataque (Semanas 4-5)
Objetivo: reducir riesgo en API, archivos y configuracion de borde.

Estado: CERRADA (2026-05-16)

Resultado de cierre alcanzado:
- CORS endurecido por entorno con listas explicitas de `origins`, `methods` y `headers`.
- Guardas productivas para CORS sin wildcard (`*`) en runtime `prod|production|staging`.
- Cabeceras HTTP de seguridad incorporadas en middleware:
  - `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, `Content-Security-Policy`, `Strict-Transport-Security` (solo prod-like).
- Hardening de uploads reforzado:
  - validacion mime/ext,
  - validacion por firma binaria,
  - bloqueo por mismatch,
  - trazabilidad de bloqueos en `audit_events` (`DOCUMENT_UPLOAD_BLOCKED`),
  - cuarentena opcional (`UPLOAD_QUARANTINE_ENABLED`, `UPLOAD_QUARANTINE_DIR`).
- Salidas externas de IA restringidas por allowlist de hosts (`OLLAMA_ALLOWED_HOSTS`).

Evidencia de validacion:
- `pnpm run test:all` en verde:
  - unit API: 24 passed
  - unit worker: 2 passed
  - unit back: 12 passed
  - integration health: 1 passed
- Cobertura nueva en tests:
  - `tests/unit/test_documents_api.py` (headers y validaciones upload),
  - `tests/unit/test_auth_api.py` (bloqueo CORS wildcard en prod),
  - `tests/unit/test_back_ollama_adapter.py` (bloqueo endpoint no permitido).

Entregables:
- Endurecimiento CORS por entorno (metodos/headers/origenes explicitos en prod).
- Reglas estrictas para uploads (mime, extension, tamano, sanitizacion, trazabilidad y cuarentena opcional).
- Endurecimiento de cabeceras HTTP y politicas de error handling sin filtracion sensible.
- Validacion de conexiones salientes controladas (allowlist interna para integraciones IA/OCR).

DoD:
- CORS productivo sin comodines operativos.
- Upload hardening con controles de bypass validados.
- No hay exposicion de detalles sensibles en respuestas de error.

Asignacion experta:
- Agente principal: `Analizador Seguridad de Codigo`.
- Agente apoyo: `Analizador Performance Sistema` (impacto de controles en latencia).
- Agente implementador: `worker`.
- Skills: `security-best-practices`, `security-review`, `pytest-coverage`.

### Fase 12 - QA de seguridad y regresion (Semanas 6-7)
Objetivo: institucionalizar pruebas para evitar reintroduccion de fallas.

Estado: CERRADA (2026-05-16)

Resultado de cierre alcanzado:
- Matriz de regresion de seguridad integrada en suite unitaria API.
- Comandos operativos agregados:
  - `pnpm run test:security:matrix`
  - `pnpm run test:security:gate`
- Gate de seguridad implementado en `scripts/security_gate.py`:
  - SAST (`bandit`)
  - auditoria de dependencias (`pip-audit`)
  - escaneo de secretos (reglas de patrones).
- Politica de excepciones de vulnerabilidades versionada en `docs/SECURITY_DEPENDENCY_ALLOWLIST.json`.
- Pipeline CI de seguridad agregado en `.github/workflows/security-gates.yml`.

Evidencia de validacion:
- `pnpm run test:unit:api` en verde (24 passed).
- `pnpm run test:all` en verde.
- `pnpm run test:security:matrix` en verde (24 passed).
- `pnpm run test:security:gate` en verde (SAST/deps/secrets scan).
- Workflow de gates de seguridad listo para PR/push en rama principal.

Entregables:
- Suite de pruebas de seguridad en API (auth required, roles, tenant isolation, token misuse, defaults inseguros).
- Cobertura de casos negativos para upload, refresh token y acceso cross-company.
- Gates de CI para SAST, secrets scan y auditoria de dependencias.
- Matriz de regresion de seguridad integrada en pipeline.

DoD:
- Pipeline bloquea cambios con hallazgos criticos de seguridad.
- Casos negativos criticos con cobertura estable y sin flakiness.
- Reporte de seguridad por build disponible para auditoria.

Asignacion experta:
- Agente principal: `Analizador Pruebas y Cobertura`.
- Agente apoyo: `Analizador Seguridad de Codigo`.
- Agente implementador: `worker`.
- Skills: `pytest-coverage`, `security-review`, `codebase-cleanup-deps-audit`.

### Fase 13 - Operacion, observabilidad y compliance (Semanas 8-9)
Objetivo: sostener seguridad en operacion continua con evidencia objetiva.

Estado: CERRADA (2026-05-16)

Resultado de cierre alcanzado:
- Dashboard operativo de seguridad implementado:
  - `GET /api/v1/security/dashboard?hours=24` (solo admin).
- Instrumentacion de eventos de seguridad en `audit_events`:
  - login fallido,
  - token invalido/faltante,
  - refresh fallido,
  - accesos denegados RBAC,
  - revocacion masiva de refresh,
  - cambios de password.
- Artefactos operativos publicados:
  - playbook de respuesta a incidentes,
  - checklist de hardening por release,
  - plantilla de informe mensual de riesgo residual,
  - matriz de regresion de seguridad.

Evidencia de validacion:
- Pruebas nuevas en `tests/unit/test_auth_api.py` para dashboard admin y restricciones RBAC.
- `pnpm run test:all` en verde tras la instrumentacion operativa.

Entregables:
- Dashboard operativo de seguridad (intentos fallidos, rechazos RBAC, tokens revocados, eventos criticos).
- Alertas y playbooks de respuesta a incidente para auth/secrets/exposicion.
- Checklist de hardening por release y validacion pre go-live.
- Informe ejecutivo mensual de riesgo residual y tendencia.

DoD:
- Monitoreo de seguridad activo con alertas accionables.
- Playbooks ensayados al menos una vez por trimestre.
- Go-live gate formal con evidencia tecnica y de negocio.

Asignacion experta:
- Agente principal: `Orquestador Analisis de Codigo`.
- Agentes especialistas por dominio: `Analizador Seguridad de Codigo`, `Analizador Pruebas y Cobertura`, `Analizador Performance Sistema`.
- Agente implementador: `worker`.
- Skills: `agent-governance`, `create-implementation-plan`, `security-best-practices`.

## Matriz de agentes y skills por fase

| Fase | Dominio principal | Agente lider | Agentes de apoyo | Skills recomendados |
| --- | --- | --- | --- | --- |
| 9 | Contencion critica | Analizador Seguridad de Codigo | worker, explorer | security-best-practices, security-review, agent-governance |
| 10 | Criptografia y credenciales | Analizador Seguridad de Codigo | Analizador Integral de Codigo, worker | security-review, refactor, review-and-refactor |
| 11 | Hardening API/upload/red | Analizador Seguridad de Codigo | Analizador Performance Sistema, worker | security-best-practices, security-review, pytest-coverage |
| 12 | QA seguridad y regresion | Analizador Pruebas y Cobertura | Analizador Seguridad de Codigo, worker | pytest-coverage, security-review, codebase-cleanup-deps-audit |
| 13 | Operacion y compliance | Orquestador Analisis de Codigo | Analizador Seguridad de Codigo, Analizador Pruebas y Cobertura, Analizador Performance Sistema, worker | agent-governance, create-implementation-plan, security-best-practices |

## Secuencia de ejecucion recomendada (post Fase 8)
1. Fase 9
2. Fase 10
3. Fase 11
4. Fase 12
5. Fase 13
