# Contratos API V2

## Convenciones
- Base path: /api/v1
- JSON UTF-8
- Trazabilidad: header X-Correlation-Id opcional
- Auth: Bearer JWT (placeholder inicial)
- Cabeceras de seguridad de respuesta:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: no-referrer`
  - `Permissions-Policy: camera=(), microphone=(), geolocation=()`
  - `Content-Security-Policy: default-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'`

## Seguridad y autenticacion
- Header requerido cuando `AUTH_ENABLED=true`:
  - `Authorization: Bearer <access_token>`
- Guardas de runtime productivo (`ENV=prod|production|staging`):
  - API no inicia si `AUTH_ENABLED=false`.
  - API no inicia si `SECURITY_JWT_SECRET` es default/debil.
  - API no inicia si `DEFAULT_SEED_PASSWORD` usa valor inseguro.
- Endpoints de autenticacion:
  - `POST /auth/login`
  - `POST /auth/change-password`
  - `POST /auth/refresh`
  - `GET /auth/me`
  - `POST /auth/revoke-all-refresh` (solo `admin`)

## Observabilidad de seguridad
- Endpoint dashboard (solo admin):
  - `GET /security/dashboard?hours=24`

Response 200:
{
  "window_hours": 24,
  "total_events": 8,
  "events": {
    "AUTH_LOGIN_FAILED": 2,
    "AUTH_ACCESS_DENIED": 3,
    "AUTH_REFRESH_REVOKE_ALL": 1
  }
}

### POST /auth/login
Request:
{
  "username": "admin",
  "password": "change_me_123"
}

Response 200:
{
  "access_token": "jwt",
  "refresh_token": "jwt",
  "expires_in": 1800
}

Errores:
- 401 credenciales invalidas
- 403 `Password change required` para cuentas bootstrap con rotacion pendiente

### POST /auth/change-password
Rotacion de password para primer login de cuentas bootstrap y cambios voluntarios.

Request:
{
  "username": "admin",
  "current_password": "change_me_123",
  "new_password": "Admin-StrongP@ss1"
}

Response 200:
{
  "password_changed": true
}

Reglas:
- Minimo 12 caracteres.
- Debe incluir mayuscula, minuscula, numero y simbolo.
- Debe ser distinta al password actual.

Errores:
- 400 password no cumple politica
- 401 credenciales invalidas

### POST /auth/refresh
Request:
{
  "refresh_token": "jwt"
}

Response 200:
{
  "access_token": "jwt",
  "refresh_token": "jwt",
  "expires_in": 1800
}

Errores:
- 401 refresh token invalido, expirado o revocado

### GET /auth/me
Response 200:
{
  "user_id": "uuid",
  "username": "contador",
  "role": "contador",
  "company_id": "real-go-nogo"
}

Errores:
- 401 falta bearer token o token invalido

### POST /auth/revoke-all-refresh
Revoke global de refresh tokens activos (operacion de contencion).

Headers:
- `Authorization: Bearer <access_token_admin>`

Response 200:
{
  "revoked_count": 42
}

Errores:
- 401 token faltante/invalido
- 403 rol sin permisos

## Matriz RBAC y aislamiento por empresa
- Regla base:
  - `admin` puede operar cualquier `tenant_id`.
  - `contador`, `ejecutivo`, `auditor` solo pueden operar su `company_id`.
- Errores esperados:
  - 403 `Insufficient permissions` para rol no autorizado.
  - 403 `Cross-company access denied` para acceso cruzado.

Permisos por modulo:
- documents:
  - upload/get/process: `admin`, `contador`, `ejecutivo`
  - override: `admin`, `contador`
- reviews:
  - pending/detail/overrides/approve/reject/resolve: `admin`, `contador`, `auditor`
- renditions:
  - generate/generate-by-filter/get/items/download: `admin`, `contador`, `ejecutivo`

## Health operacional
- `GET /health`: salud general de API.
- `GET /liveness`: liveness probe para orquestadores.
- `GET /readiness`: readiness probe con chequeos de dependencias (DB/Redis).

## POST /documents/upload
Sube documento y encola procesamiento.

Request (multipart/form-data):
- file: binary (required)
- tenant_id: string (required)
- responsible: string (optional)
- period: string YYYY-MM (optional)
- center_cost: string (optional)

Response 202:
{
  "document_id": "uuid",
  "status": "RECEIVED",
  "duplicate": false,
  "warnings": []
}

Errores:
- 400 formato invalido
- 413 archivo excede limite
- 415 mime no soportado
- 415 mismatch entre mime y extension
- 422 firma de archivo invalida o inconsistente (cuarentena opcional)

## GET /documents/{document_id}
Obtiene estado de pipeline y resultado resumido.

Response 200:
{
  "document_id": "uuid",
  "status": "RECEIVED|PROCESSING|REVIEW_REQUIRED|COMPLETED|FAILED",
  "classification": {
    "document_type": "receipt|invoice|credit_note|unknown",
    "country_code": "CL|US|...",
    "confidence": 0.96
  },
  "extraction": {
    "supplier_name": "...",
    "supplier_tax_id": "...",
    "document_number": "...",
    "issue_date": "2026-05-01",
    "currency": "CLP",
    "total": 73974
  },
  "warnings": ["MISSING_CENTER_COST"],
  "review_required": false
}

## POST /documents/{document_id}/override
Permite correccion manual de campos.

Request:
{
  "fields": {
    "supplier_tax_id": "76850000-8",
    "center_cost": "ADM-001"
  },
  "reason": "Correccion validada por contabilidad"
}

Response 200:
{
  "document_id": "uuid",
  "status": "COMPLETED",
  "overrides_applied": 2
}

## POST /renditions/generate
Genera archivo de rendicion desde un lote.

Request:
{
  "tenant_id": "acme",
  "period": "2026-05",
  "document_ids": ["uuid1", "uuid2"],
  "template_version": "01-rendicion-gastos-2025"
}

Regla clave:
- Campos faltantes en plantilla se exportan en blanco y generan warning.
- No es causal de error bloqueante.

Response 200:
{
  "rendition_id": "uuid",
  "file_url": "https://.../rendition.xlsx",
  "warnings_count": 3,
  "status": "GENERATED"
}

## GET /renditions/{rendition_id}
Response 200:
{
  "rendition_id": "uuid",
  "status": "GENERATED",
  "file_url": "https://.../rendition.xlsx",
  "summary": {
    "rows": 24,
    "warnings": 3,
    "missing_fields": ["Centro Costo", "Cuenta"]
  }
}

## POST /renditions/generate/by-filter
Genera archivo de rendicion usando filtros operativos.

Request:
{
  "tenant_id": "acme",
  "period": "2026-05",
  "responsible": "Ana",
  "center_cost": "FINANZAS",
  "template_version": "01-rendicion-gastos-2025"
}

Response 200:
{
  "rendition_id": "uuid",
  "file_url": "https://.../rendition.xlsx",
  "warnings_count": 3,
  "status": "GENERATED"
}

## GET /renditions/{rendition_id}/items
Lista detalle por documento incluido en la rendicion.

## GET /renditions/{rendition_id}/download
Descarga directa del archivo XLSX generado.

## Modelo de warning recomendado
{
  "code": "MISSING_FIELD",
  "field": "Centro Costo",
  "severity": "warning",
  "message": "No se detecto valor para el campo; se exporta en blanco"
}
