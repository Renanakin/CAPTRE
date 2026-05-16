# capturador_datos_v2

Repositorio principal del sistema de captura, validacion y rendicion contable.

Capas oficiales del proyecto:
- Front: `apps/front`
- Back: `apps/back`
- API: `apps/api`

Documento rector:
- `docs/ROADMAP_MAESTRO_CAPTURADOR_DATOS_V2.md`

Norma de trabajo:
- Cada carpeta activa debe mantener `README.md` y `SKILLS.md` actualizados.
- Todo desarrollo debe mapearse a una fase del roadmap maestro.

## Estandar obligatorio de ejecucion
- Todo comando operativo del repositorio debe ejecutarse via `pnpm`.
- Scripts oficiales disponibles en la raiz del proyecto (`package.json`):
	- `pnpm run deps:install`
	- `pnpm run front:dev`
	- `pnpm run api:dev`
	- `pnpm run worker:dev`
	- `pnpm run db:migrate`
	- `pnpm run test:unit`
	- `pnpm run test:unit:back`
	- `pnpm run test:integration:health`
	- `pnpm run test:all`
	- `pnpm run qa:real-go-nogo`

## Integracion Ollama (Fase 7)
- Variables de entorno:
	- `OLLAMA_ENABLED`
	- `OLLAMA_API`
	- `OLLAMA_MODEL`
	- `OLLAMA_TIMEOUT_SECONDS`
	- `OLLAMA_RETRY_COUNT`
	- `OLLAMA_BACKOFF_SECONDS`
	- `OLLAMA_REQUIRE_MODEL_AVAILABLE`
- Endpoints utiles para diagnostico:
	- `GET /api/tags`
	- `POST /api/generate`
	- `POST /api/chat`

Comportamiento de resiliencia:
- Verifica que el modelo configurado exista en `GET /api/tags` antes de inferir.
- Reintenta llamadas a `POST /api/generate` con backoff incremental.
- Si Ollama no esta disponible, el pipeline sigue con fallback regex/OCR sin bloqueo.

## Seguridad Fase 8
- Autenticacion JWT y refresh token:
	- `POST /api/v1/auth/login`
	- `POST /api/v1/auth/refresh`
	- `GET /api/v1/auth/me`
- RBAC aplicado a rutas de documentos/reviews/renditions.
- Aislamiento estricto por `company_id` (tenant) en acceso a documentos y rendiciones.
- Endpoints de observabilidad productiva:
	- `GET /api/v1/health`
	- `GET /api/v1/liveness`
	- `GET /api/v1/readiness`
