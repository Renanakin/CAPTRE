# apps/front

Carpeta activa del proyecto capturador_datos_v2.

Referencias:
- Roadmap maestro: `docs/ROADMAP_MAESTRO_CAPTURADOR_DATOS_V2.md`
- Roadmap Front AAA: `docs/ROADMAP_FRONT_AAA_CAPTRE.md`
- Estandar global: `README.md` y `SKILLS.md` de la raiz.

Responsabilidad principal:
- Mantener codigo, pruebas y documentacion alineados a la fase vigente.

## Frontend operativo (Fase 5)
Pantallas disponibles en la SPA original:
- Login
- Dashboard
- Carga documental
- Listado y detalle de documentos
- Bandeja de revision
- Rendiciones e historial

Ejecucion:
- Desde raiz: `pnpm run front:dev`
- URL local: `http://127.0.0.1:5173`

## Avance Front AAA (2026-05-16)

Estado: IMPLEMENTACION INICIAL COMPLETADA.

Este avance aplica el primer corte del roadmap Front AAA sin cambiar aun a un build tool con dependencias externas. Se mantiene la ejecucion estatica oficial para reducir riesgo operacional y dejar una consola visualmente validable antes de una migracion React/TypeScript.

### Modulos implementados

- App shell enterprise:
  - Sidebar de navegacion.
  - Topbar con breadcrumb, busqueda, usuario, rol, empresa y acciones.
  - Layout responsive con menu movil.
- Login productivo:
  - Login real contra `POST /api/v1/auth/login`.
  - Lectura de perfil con `GET /api/v1/auth/me`.
  - Persistencia de access/refresh token.
  - Refresh token automatico ante `401`.
  - Modo demo para validar UI cuando API no esta disponible.
- RBAC visual:
  - Rutas visibles segun rol `admin`, `contador`, `ejecutivo` y `auditor`.
  - Bloqueo visual de rutas no permitidas.
- Dashboard operacional:
  - KPIs de cargados, procesados, pendientes y rendiciones.
  - Pipeline documental.
  - Alertas criticas.
  - Ultimos documentos con acciones.
- Centro documental:
  - Tabla con filtros por texto y estado.
  - Exportacion CSV local.
  - Detalle documental con datos normalizados y JSON tecnico como soporte secundario.
  - Accion de reprocesamiento via `POST /api/v1/documents/{document_id}/process`.
- Carga documental avanzada:
  - Drag & drop.
  - Carga multiple.
  - Validacion de formato.
  - Cola por archivo.
  - Integracion con `POST /api/v1/documents/upload`.
- Revision inteligente:
  - Cola de pendientes desde `GET /api/v1/reviews/pending`.
  - Detalle desde `GET /api/v1/reviews/{document_id}`.
  - Acciones `approve`, `reject` y `overrides`.
- Rendition Studio:
  - Wizard visual.
  - Preview local de documentos candidatos.
  - Generacion por filtro via `POST /api/v1/renditions/generate/by-filter`.
  - Historial local de rendiciones y descarga autenticada.
- Auditoria:
  - Registro local de acciones operativas relevantes.
- Observabilidad:
  - Checks contra `/health`, `/liveness` y `/readiness`.
  - Diagnostico copiable desde la consola.
- Configuracion:
  - Vista inicial de empresa, rol, API base y rutas permitidas.

### Decisiones tecnicas del avance

- Se preserva el servidor estatico actual (`python -m http.server 5173`) para evitar incorporar dependencias antes de la aprobacion final del roadmap.
- La consola usa JavaScript modular sin framework en este corte.
- La estructura visual y funcional queda preparada para migrar a Vite + React + TypeScript en la siguiente fase si se aprueba.
- Donde la API aun no expone listados persistentes completos, la UI usa estado local persistido en `localStorage` y datos de endpoints disponibles.

### Pendientes recomendados

- Migrar a Vite + React + TypeScript.
- Crear suite Playwright formal.
- Agregar endpoints API de listado documental y listado de rendiciones si no existen.
- Reemplazar auditoria local por auditoria persistida en API cuando el contrato este disponible.
- Incorporar preview real de PDF/imagen si API expone descarga segura de originales.
