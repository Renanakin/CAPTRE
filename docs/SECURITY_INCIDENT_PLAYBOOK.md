# Security Incident Playbook

## Alcance
Respuesta a incidentes de autenticacion, secretos, acceso no autorizado, y exposicion de datos.

## Severidades
- SEV-1: acceso no autorizado confirmado o exfiltracion.
- SEV-2: intento activo con impacto potencial alto.
- SEV-3: hallazgo controlado sin impacto directo.

## Flujo operativo
1. Detectar: alerta de dashboard o gate CI.
2. Contener: revocar refresh tokens global (`POST /api/v1/auth/revoke-all-refresh`), rotar secreto JWT, aislar endpoints si aplica.
3. Investigar: revisar `audit_events` de seguridad por ventana horaria.
4. Erradicar: corregir configuracion/codigo raiz.
5. Recuperar: desplegar parche y monitorear indicadores.
6. Postmortem: documentar causa raiz, acciones y mejoras preventivas.

## Acciones de contencion inmediata
- Forzar rotacion de `SECURITY_JWT_SECRET`.
- Invalidar tokens activos.
- Confirmar `AUTH_ENABLED=true` en entorno afectado.
- Validar CORS y allowlist de salidas externas.

## Evidencias minimas
- Timeline del incidente.
- Eventos de seguridad relevantes.
- Impacto tecnico y de negocio.
- Acciones ejecutadas y estado final.
