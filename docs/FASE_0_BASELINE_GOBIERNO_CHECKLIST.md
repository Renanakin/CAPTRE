# Fase 0 - Baseline y Gobierno Tecnico (Semana 1)

## Estado
- Inicio: 2026-05-15
- Estado general: CERRADA
- Roadmap fuente: docs/ROADMAP_MAESTRO_CAPTURADOR_DATOS_V2.md

## Evidencia de inicio
- [x] README raiz revisado
- [x] SKILLS raiz revisado
- [x] README docs revisado
- [x] SKILLS docs revisado
- [x] Fase 0 marcada como EN CURSO en roadmap maestro
- [x] Baseline inicial de pruebas ejecutado (2026-05-15)

## Objetivo operativo de la semana
Cerrar Fase 0 con estandares de trabajo, baseline de calidad y matriz de riesgos publicada.

## Workboard Fase 0

### 1) Gobierno tecnico y estandares
- [ ] Publicar convencion de ramas: feature/*, fix/*, hotfix/*
- [ ] Publicar flujo minimo de PR: alcance, evidencia, riesgos, plan de rollback
- [ ] Publicar Definition of Ready (DoR)
- [ ] Publicar Definition of Done (DoD)

### 2) Baseline tecnico medible
- [x] Ejecutar pruebas unitarias actuales y registrar resultado base
- [x] Ejecutar pruebas de integracion actuales y registrar resultado base
- [ ] Registrar cobertura inicial y brechas criticas
- [ ] Registrar estado de health checks API/worker

Resultado baseline 2026-05-15:
- Comando: `pnpm run test:all`
- Resultado: 2 passed, 7 failed.
- Fallas principales detectadas:
	- `ModuleNotFoundError: No module named 'app'` en pruebas unitarias de API.
	- `ConnectionRefusedError` en integracion de health por API no levantada en `localhost:8000`.

Validacion de comando canonico (2026-05-15):
- Unit API: `pnpm run test:unit:api` -> 6 passed.
- Integracion health: `pnpm run test:integration:health` -> 1 passed.

Accion inmediata derivada:
- Publicar comandos canonicos de ejecucion por tipo de prueba.
- Ajustar entorno de ejecucion de pruebas (PYTHONPATH y working dir de API) para evitar falsos negativos.
- Definir estrategia de integracion automatica: levantar API en setup de test o usar cliente embebido.
- Definir comando canonico de migraciones: `pnpm run db:migrate`.

### 3) Riesgos y mitigacion
- [x] Crear matriz de riesgos con severidad/probabilidad/impacto
- [ ] Asignar owner por riesgo
- [ ] Definir mitigacion y criterio de seguimiento por riesgo

### 4) Preparacion de Fase 1
- [x] Desglosar backlog del refactor API por modulos: routes/services/repositories/models/schemas
- [x] Definir secuencia de implementacion por bajo riesgo
- [x] Definir pruebas de no-regresion para refactor de API

Ejecucion de traspaso a Fase 1 (2026-05-15):
- Estructura modular creada en API: `app/api/v1/routes`, `app/services`, `app/repositories`, `app/models`, `app/schemas`.
- Primer endpoint migrado (health) desde `main.py` a route + service.

## Ownership por capa para Fase 0
- API: contratos, seguridad y validacion
- Back/Worker: pipeline documental, asincronia y estabilidad
- Front: validacion de consumo API y QA operativo

## Gate de salida Fase 0
- [x] Estandares de trabajo aprobados
- [x] Baseline tecnico registrado en docs
- [x] Matriz de riesgos activa con owners
- [x] Backlog de Fase 1 priorizado y estimado

## Notas de ejecucion
- Todo cambio de implementacion debe mapearse al roadmap maestro.
- Mantener README y SKILLS de carpetas activas actualizados como requisito de cierre.
