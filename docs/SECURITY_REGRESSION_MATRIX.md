# Security Regression Matrix

## Objetivo
Evitar reintroduccion de fallas de seguridad en autenticacion, autorizacion, uploads, CORS y salidas externas.

## Cobertura minima obligatoria
- Auth required en endpoints protegidos.
- RBAC por rol y aislamiento por tenant (`company_id`).
- Rotacion obligatoria de password bootstrap.
- Revocacion global de refresh tokens.
- CORS sin wildcard en runtime productivo.
- Upload hardening (mime/ext/firma).
- Allowlist de host para integraciones externas IA.
- Dashboard de seguridad solo admin.

## Casos de regresion (API)
1. Login bootstrap exige cambio de password.
2. Password debil rechazada en `change-password`.
3. Token refresh reutilizado/revocado retorna 401.
4. Usuario no admin no puede `revoke-all-refresh`.
5. Usuario no admin no puede `GET /security/dashboard`.
6. Upload con mime/ext mismatch retorna 415.
7. Upload con firma invalida retorna 422.
8. Acceso cross-company retorna 403.
9. Runtime prod rechaza `AUTH_ENABLED=false`.
10. Runtime prod rechaza CORS wildcard.

## Comandos canonicos
- `pnpm run test:security:matrix`
- `pnpm run test:security:gate`
- `pnpm run test:all`

## Gate policy
- Ningun hallazgo critico en SAST/dependencias/secrets scan.
- Ningun test de seguridad en rojo.
- Bloqueo de merge si falla cualquier gate de seguridad.
