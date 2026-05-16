# Fase 0 - Matriz de Riesgos Tecnicos Inicial

Fecha de apertura: 2026-05-15
Estado: ACTIVA

## Escala usada
- Severidad: Alta / Media / Baja
- Probabilidad: Alta / Media / Baja
- Impacto: Alto / Medio / Bajo

## Riesgos

| ID | Riesgo | Evidencia | Severidad | Probabilidad | Impacto | Mitigacion inicial | Owner propuesto | Estado |
|---|---|---|---|---|---|---|---|---|
| R-001 | Pruebas unitarias API fallan por resolucion de modulos | `ModuleNotFoundError: No module named 'app'` en tests unitarios ejecutados desde raiz | Alta | Alta | Alto | Estandarizar PYTHONPATH y punto de ejecucion de tests de API; comando canonico via `pnpm`: `pnpm run test:unit:api` | API | Mitigado |
| R-002 | Pruebas de integracion dependen de API externa no levantada | `ConnectionRefusedError` en `localhost:8000` en test health | Alta | Alta | Alto | Definir bootstrap de API para tests de integracion o mock de infraestructura; integracion validada con API local y estrategia de arranque temporal | API + QA | Mitigado |
| R-003 | Baseline de cobertura no disponible para priorizar deuda | No hay reporte de cobertura inicial registrado en docs | Media | Media | Medio | Incorporar ejecucion con cobertura y publicar reporte base en docs | QA | Abierto |
| R-004 | Criterios de rama/PR/DoR/DoD aun no formalizados | Checklist Fase 0 sin cierre en gobierno | Media | Media | Medio | Publicar convenciones y exigirlas en todo PR nuevo | Tech Lead | Abierto |

## Criterio de seguimiento semanal
- Revisar riesgos en checkpoint de cierre semanal.
- Riesgo con severidad Alta solo puede pasar a mitigado con evidencia verificable.

## Criterio de cierre Fase 0 (riesgos)
- Riesgos Alta con plan de mitigacion activo y owner confirmado.
- Riesgos Media con fecha objetivo y evidencia de avance.
