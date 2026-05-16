# Security Release Hardening Checklist

## Pre-merge
- [ ] `pnpm run test:security:matrix` en verde.
- [ ] `pnpm run test:security:gate` en verde.
- [ ] Sin secretos embebidos en cambios.

## Pre-deploy
- [ ] `AUTH_ENABLED=true` en prod/staging.
- [ ] `SECURITY_JWT_SECRET` fuerte y vigente.
- [ ] `SECURITY_JWT_ROTATED_AT` actualizado.
- [ ] `CORS_ALLOW_ORIGINS` sin wildcard.
- [ ] `CORS_ALLOW_METHODS` y `CORS_ALLOW_HEADERS` explicitos.
- [ ] `AUTH_SEED_USERS=false` en prod/staging.
- [ ] `OLLAMA_ALLOWED_HOSTS` validado.

## Post-deploy
- [ ] Health/liveness/readiness OK.
- [ ] Dashboard seguridad sin picos anormales.
- [ ] Verificacion manual de RBAC y tenant isolation.

## Go/No-Go
- [ ] GO solo si todos los checks anteriores estan completos.
