# Roadmap Front AAA - CAPTRE

## 1. Proposito

Este documento propone la preparacion y posterior desarrollo de un frontend AAA para CAPTRE, orientado a convertir la SPA operativa actual en una consola productiva de operaciones contables, revision documental, OCR/IA, rendiciones, auditoria y observabilidad.

El alcance de este documento es solo planificacion: fases, skills, agentes, criterios de decision y mockup integral. No autoriza por si mismo cambios de implementacion en `apps/front`.

## 2. Contexto de partida

CAPTRE ya declara tres capas activas: Front, Back y API. El frontend debe sostener la operacion diaria de carga, revision y rendiciones, mientras que Back/API exponen procesamiento documental, seguridad, auditoria, OCR, reglas, workers e integraciones.

Estado actual observado del front:

- SPA estatica en `apps/front`.
- Pantallas existentes: login, dashboard, carga documental, listado/detalle, revision y rendiciones.
- Ejecucion local via `pnpm run front:dev`.
- Integracion inicial con API V1.
- Estado de documentos principalmente local/en memoria durante la sesion.
- Salidas tecnicas en JSON/pre para algunos flujos.

Brecha principal: el front ya habilita operacion basica, pero no tiene todavia nivel visual, arquitectura, experiencia por rol, navegacion, trazabilidad, observabilidad y ergonomia de revision necesarias para un producto final comercial.

## 3. Vision AAA

Construir una **FinOps Intelligence Console** para CAPTRE:

- Apariencia premium, sobria y confiable para clientes reales.
- Operacion documental de alto volumen.
- Revision inteligente asistida por OCR, IA y reglas contables.
- Rendiciones guiadas tipo estudio/wizard.
- Experiencia multiempresa, por rol y con permisos.
- Observabilidad productiva para soporte y operacion.
- Base tecnica testeable, escalable y preparada para evolucion.

## 4. Principios de producto

1. **Operacion antes que decoracion:** cada mejora visual debe reducir friccion operativa.
2. **Datos entendibles, no JSON crudo:** la UI debe transformar respuestas tecnicas en decisiones accionables.
3. **Confianza y trazabilidad:** todo documento debe mostrar origen, estado, score, reglas, responsable e historial.
4. **Multiempresa desde el diseno:** empresa activa, roles y permisos visibles en toda la app.
5. **Revision asistida:** el usuario debe entender por que un documento fue enviado a revision y que accion se recomienda.
6. **QA desde el primer sprint:** cada fase debe incluir validacion visual, funcional y responsive.
7. **Migracion incremental:** evitar big bang; mantener flujos actuales funcionales mientras se reemplaza la UI.

## 5. Stack tecnico recomendado

### 5.1 Base frontend

- Vite.
- React.
- TypeScript.
- React Router.
- TanStack Query.
- React Hook Form.
- Zod.
- Tailwind CSS o CSS Modules con design tokens.
- shadcn/ui o componentes propios equivalentes.

### 5.2 Calidad y pruebas

- Playwright para smoke/E2E.
- Vitest para pruebas unitarias de UI y utilidades.
- Testing Library para componentes.
- ESLint.
- Prettier.
- Lighthouse/manual performance pass.
- Axe/manual accessibility pass.

### 5.3 Contratos e integracion

- API client centralizado.
- Tipos por modulo.
- Schemas Zod para normalizar respuestas criticas.
- Manejo global de errores.
- Manejo global de sesion y refresh token.
- Variables de entorno para API base.

## 6. Skills que se ocuparan

| Skill | Uso previsto | Fases principales |
| --- | --- | --- |
| `agent-governance` | Definir ownership por modulo, coordinar agentes y evitar conflictos. | 0 a 8 |
| `create-implementation-plan` | Convertir este roadmap en tareas ejecutables por sprint. | 0, 1 |
| `frontend-responsive-design-standards` | Garantizar layout responsive, accesibilidad visual y patrones UI consistentes. | 1 a 8 |
| `refactor` | Migrar la SPA actual sin romper flujos existentes. | 1, 2, 3 |
| `security-best-practices` | Integrar JWT, refresh, RBAC, permisos, proteccion de rutas y datos multiempresa. | 2, 3, 8 |
| `playwright` | Crear smoke tests, flujos E2E y validacion en localhost. | 1 a 8 |
| `pytest-coverage` | Validar que cambios de contrato no rompan API/back cuando se requiera. | 3 a 8 |

## 7. Agentes que se ocuparan

| Agente | Responsabilidad | Cuándo participa |
| --- | --- | --- |
| `explorer` | Levantar contratos API, endpoints reales, riesgos, dependencias y estado del front antes de tocar codigo. | Preparacion y auditorias por fase. |
| `worker` | Implementar features, refactors, componentes, pruebas y documentacion. | Desarrollo de cada fase. |
| Agente principal | Coordinar plan, revisar integracion, validar criterios de done, preparar commits/PR. | Todo el ciclo. |

### 7.1 Estrategia multiagente propuesta

- Un `explorer` por paquete de analisis independiente: contratos API, seguridad/RBAC, UI actual, pruebas existentes.
- Un `worker` por area de implementacion con ownership claro:
  - Layout/design system.
  - Auth/RBAC.
  - Documentos/carga.
  - Revision.
  - Rendiciones.
  - Observabilidad/QA.
- Ningun agente debe revertir trabajo de otro; cada worker trabaja sobre un set de archivos definido.

## 8. Fases de preparacion y desarrollo

## Fase 0 - Discovery, alcance y decision GO/NO-GO

**Objetivo:** confirmar que la migracion AAA aplica, cerrar alcance y convertir este documento en backlog ejecutable.

**Actividades:**

- Revisar `apps/front` completo.
- Inventariar endpoints disponibles en API.
- Confirmar contratos de auth, documentos, reviews, renditions y observabilidad.
- Identificar gaps de API que bloqueen UI productiva.
- Definir si se hara migracion incremental o reemplazo total.
- Definir criterios de exito visual y funcional.

**Skills:**

- `agent-governance`.
- `create-implementation-plan`.
- `frontend-responsive-design-standards`.

**Agentes:**

- `explorer`: analisis de front actual y contratos.
- Agente principal: consolidacion y decision GO/NO-GO.

**Entregables:**

- Backlog por fases.
- Mapa de endpoints.
- Matriz de riesgos.
- Decision GO/NO-GO.

**Criterio de cierre:**

- Existe acuerdo sobre stack, alcance, pantallas, permisos y fases.

## Fase 1 - Fundacion tecnica del nuevo front

**Objetivo:** crear una base productiva para evolucionar el front sin deuda estructural.

**Actividades:**

- Migrar a Vite + React + TypeScript.
- Configurar router.
- Configurar query client.
- Configurar estructura `src/features` y `src/shared`.
- Crear API client base.
- Crear variables de entorno.
- Configurar lint, format y tests base.
- Mantener funcionalidad minima equivalente al front actual.

**Skills:**

- `refactor`.
- `frontend-responsive-design-standards`.
- `playwright`.

**Agentes:**

- `worker`: scaffolding y migracion base.
- `explorer`: revisar riesgos de compatibilidad.

**Entregables:**

- App React/TS corriendo via `pnpm run front:dev`.
- Rutas base.
- API client.
- Smoke test inicial.

**Criterio de cierre:**

- La app levanta, navega y puede conectarse a API base sin romper scripts existentes.

## Fase 2 - Design system AAA y app shell

**Objetivo:** establecer la identidad visual y los componentes reutilizables de la consola.

**Actividades:**

- Definir tokens: color, tipografia, spacing, radius, sombras, z-index.
- Crear layout principal: sidebar, topbar, breadcrumbs, content area.
- Crear componentes base:
  - Button.
  - Card.
  - Badge.
  - Input.
  - Select.
  - Table.
  - Modal.
  - Drawer.
  - Tabs.
  - Toast.
  - EmptyState.
  - Skeleton.
  - StatusPill.
  - MetricCard.
- Crear estados visuales: loading, error, empty, success, warning.
- Crear modo responsive.

**Skills:**

- `frontend-responsive-design-standards`.
- `playwright`.
- `refactor`.

**Agentes:**

- `worker`: design system y layout.
- Agente principal: revision de consistencia visual.

**Entregables:**

- Design system minimo viable.
- App shell enterprise.
- Mock visual implementado con datos fake.

**Criterio de cierre:**

- Todas las pantallas futuras pueden construirse con componentes base, sin CSS ad hoc desordenado.

## Fase 3 - Autenticacion, sesion y RBAC

**Objetivo:** alinear la UI con seguridad productiva.

**Actividades:**

- Login real contra API.
- Manejo de access token y refresh token.
- Perfil de usuario.
- Empresa activa.
- Guards por ruta.
- Menu filtrado por rol.
- Pantallas `forbidden`, `session-expired`, `not-found`.
- Logout seguro.

**Skills:**

- `security-best-practices`.
- `frontend-responsive-design-standards`.
- `playwright`.

**Agentes:**

- `explorer`: confirmar contratos auth/RBAC.
- `worker`: implementacion auth.

**Entregables:**

- Flujo de login productivo.
- Proteccion de rutas.
- Sesion persistente controlada.
- Pruebas smoke de login/logout.

**Criterio de cierre:**

- Un usuario solo ve rutas y acciones permitidas por su rol y empresa.

## Fase 4 - Dashboard ejecutivo y operacional

**Objetivo:** convertir el inicio en un centro de control real.

**Actividades:**

- KPIs de documentos, revisiones, rendiciones y confianza.
- Funnel documental.
- Alertas operativas.
- Actividad reciente.
- Estado de servicios principales.
- Acciones rapidas.

**Skills:**

- `frontend-responsive-design-standards`.
- `playwright`.
- `pytest-coverage` si requiere validar endpoints.

**Agentes:**

- `worker`: dashboard.
- `explorer`: endpoints de metricas o estrategias fallback.

**Entregables:**

- Dashboard responsive.
- KPIs conectados a API o adaptadores temporales.
- Empty/loading/error states.

**Criterio de cierre:**

- El dashboard permite entender el estado operacional en menos de 30 segundos.

## Fase 5 - Centro documental y carga avanzada

**Objetivo:** profesionalizar carga, busqueda y gestion documental.

**Actividades:**

- Drag & drop.
- Carga multiple.
- Progreso por archivo.
- Validaciones previas.
- Tabla documental con filtros.
- Busqueda y ordenamiento.
- Acciones masivas.
- Drawer de detalle rapido.
- Vista detalle completa.

**Skills:**

- `frontend-responsive-design-standards`.
- `security-best-practices`.
- `playwright`.

**Agentes:**

- `worker`: modulo upload/documentos.
- `explorer`: contratos de documentos y descarga/preview.

**Entregables:**

- Centro documental productivo.
- Carga avanzada.
- Detalle documental con datos normalizados.

**Criterio de cierre:**

- Un operador puede cargar, encontrar, revisar estado y abrir detalle de documentos sin ver JSON crudo.

## Fase 6 - Revision inteligente asistida

**Objetivo:** transformar la revision manual en una experiencia de decision asistida.

**Actividades:**

- Bandeja priorizada por severidad.
- Detalle de motivos de revision.
- Comparacion OCR/IA/reglas/valor final.
- Overrides editables.
- Aprobar, rechazar, corregir y aprobar.
- Comentarios.
- Timeline.
- SLA visual.

**Skills:**

- `frontend-responsive-design-standards`.
- `security-best-practices`.
- `playwright`.

**Agentes:**

- `worker`: modulo reviews.
- `explorer`: contratos de pending/detail/approve/reject/overrides.

**Entregables:**

- Bandeja de revision AAA.
- Panel de decision.
- Pruebas E2E de aprobar/rechazar.

**Criterio de cierre:**

- El usuario entiende por que revisa un documento y puede resolverlo con trazabilidad completa.

## Fase 7 - Rendition Studio

**Objetivo:** convertir las rendiciones en un flujo guiado, validado y auditable.

**Actividades:**

- Wizard de nueva rendicion:
  1. Periodo y empresa.
  2. Filtros.
  3. Preview de documentos.
  4. Validaciones.
  5. Generacion y descarga.
- Historial de rendiciones.
- Detalle de rendicion.
- Warnings antes de generar.
- Descarga XLSX.
- Regeneracion controlada si aplica.

**Skills:**

- `frontend-responsive-design-standards`.
- `security-best-practices`.
- `playwright`.
- `pytest-coverage` si se ajustan contratos.

**Agentes:**

- `worker`: modulo renditions.
- `explorer`: contratos de generacion, detalle y descarga.

**Entregables:**

- Rendition Studio.
- Historial y detalle.
- E2E de generar y descargar.

**Criterio de cierre:**

- Un usuario puede generar una rendicion confiable con preview y validaciones antes de descargar.

## Fase 8 - Auditoria, observabilidad y QA final

**Objetivo:** dejar el front listo para operacion comercial y soporte.

**Actividades:**

- Panel de observabilidad:
  - health.
  - liveness.
  - readiness.
  - API.
  - worker.
  - OCR/IA si existen senales.
- Auditoria de acciones.
- Registro visual por documento/rendicion.
- Suite Playwright final.
- Checks responsive.
- Checks accesibilidad.
- Documentacion de operacion.
- Checklist GO/NO-GO.

**Skills:**

- `playwright`.
- `frontend-responsive-design-standards`.
- `security-best-practices`.
- `pytest-coverage`.

**Agentes:**

- `worker`: observabilidad y tests.
- `explorer`: validacion de riesgos residuales.
- Agente principal: cierre QA y PR final.

**Entregables:**

- Observability Center.
- Audit Center.
- Pruebas E2E criticas.
- Documentacion final.

**Criterio de cierre:**

- Front validado funcionalmente, responsive, con rutas protegidas, sin flujos criticos rotos y con evidencia QA.

## 9. Mockup del front completo

> Mockup conceptual en texto. Sirve para validar estructura, jerarquia y flujos antes de disenar o implementar UI final.

## 9.1 App shell global

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ CAPTRE Intelligence Console                         Empresa: ACME SpA ▾  Usuario: Ana ▾     │
│ Buscar documento, proveedor, rendicion...                                   ● API OK ● IA OK │
├───────────────┬──────────────────────────────────────────────────────────────────────────────┤
│ Navegacion    │ Breadcrumb: Inicio / Dashboard                                                │
│               │                                                                              │
│ ▸ Dashboard   │ ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐        │
│ ▸ Documentos  │ │ Docs procesados    │ │ Pendientes revision │ │ Confianza promedio │        │
│   - Todos     │ │ 1.248              │ │ 17                 │ │ 96.4%              │        │
│   - Carga     │ └────────────────────┘ └────────────────────┘ └────────────────────┘        │
│ ▸ Revision    │                                                                              │
│ ▸ Rendiciones │ ┌──────────────────────────────────────┐ ┌──────────────────────────────┐   │
│ ▸ Auditoria   │ │ Funnel documental                    │ │ Alertas criticas              │   │
│ ▸ Observab.   │ │ Cargado > OCR > IA > Revision > XLSX │ │ 3 baja confianza              │   │
│ ▸ Config      │ │ ████████████████████                 │ │ 2 moneda no permitida         │   │
│               │ └──────────────────────────────────────┘ └──────────────────────────────┘   │
└───────────────┴──────────────────────────────────────────────────────────────────────────────┘
```

## 9.2 Login productivo

```text
┌────────────────────────────────────────────────────────────┐
│                    CAPTRE                                  │
│       Captura, validacion y rendicion contable             │
│                                                            │
│  Email                                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ contabilidad@empresa.cl                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  Password                                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ •••••••••••••••                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  [ Entrar ]                           Recuperar acceso     │
│                                                            │
│  Estado: API disponible · Ambiente: Produccion             │
└────────────────────────────────────────────────────────────┘
```

## 9.3 Dashboard

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ Dashboard operacional                                                        Periodo 2026-05 │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│ │ Cargados     │ │ Procesados   │ │ En revision  │ │ Aprobados    │ │ Rendiciones  │       │
│ │ 312          │ │ 289          │ │ 17           │ │ 261          │ │ 24           │       │
│ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
│                                                                                              │
│ ┌───────────────────────────────────────────┐ ┌──────────────────────────────────────────┐  │
│ │ Flujo documental                          │ │ Riesgos operativos                       │  │
│ │ Recibido █████████████████████ 312        │ │ ⚠ 7 documentos con baja confianza        │  │
│ │ OCR      ████████████████████  301        │ │ ⚠ 2 proveedores nuevos                   │  │
│ │ IA       ███████████████████   289        │ │ ⚠ 3 campos tributarios faltantes         │  │
│ │ Aprobado █████████████████     261        │ │ [Ver bandeja de revision]                │  │
│ └───────────────────────────────────────────┘ └──────────────────────────────────────────┘  │
│                                                                                              │
│ ┌────────────────────────────────────────────────────────────────────────────────────────┐   │
│ │ Ultimos documentos criticos                                                           │   │
│ │ ID        Proveedor        Total        Confianza        Estado          Accion         │   │
│ │ DOC-901   ACME Ltda        $980.000     72%              Revision        Abrir          │   │
│ │ DOC-899   Global Inc       USD 120      81%              Warning         Abrir          │   │
│ └────────────────────────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 9.4 Centro documental

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ Documentos                                                     [Carga documental] [Exportar] │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Filtros: Periodo ▾ Estado ▾ Responsable ▾ Centro costo ▾ Confianza ▾ Buscar...              │
│                                                                                              │
│ ┌────────────────────────────────────────────────────────────────────────────────────────┐   │
│ │ Archivo       Proveedor      Fecha       Total       Conf.   Estado       Acciones      │   │
│ │ factura.pdf   ACME SpA       16/05/26    $120.000    98%     Aprobado     Ver · Rendir  │   │
│ │ boleta.jpg    Demo Ltda      15/05/26    $45.900     73%     Revision     Revisar       │   │
│ │ invoice.pdf   Global Inc     15/05/26    USD 88      89%     Warning      Ver           │   │
│ └────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                              │
│ Paginacion: 1 2 3 ... 40                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 9.5 Carga documental avanzada

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ Carga documental                                                                              │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────────────────────────────────────────┐   │
│ │ Arrastra PDFs o imagenes aqui                                                         │   │
│ │ Formatos permitidos: PDF, PNG, JPG · Max 25MB por archivo                              │   │
│ │ [Seleccionar archivos]                                                                 │   │
│ └────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                              │
│ Metadatos comunes                                                                             │
│ Periodo [2026-05]  Responsable [Ana]  Centro costo [FINANZAS]  Tipo [Gasto]                  │
│                                                                                              │
│ Cola de carga                                                                                 │
│ ┌────────────────────────────────────────────────────────────────────────────────────────┐   │
│ │ factura_001.pdf     Subido       OCR completo      IA completo      Confianza 98%       │   │
│ │ factura_002.pdf     Procesando   OCR 45%           IA pendiente     ...                 │   │
│ │ boleta_003.jpg      Error        Extension OK      Reintentar       [Reintentar]        │   │
│ └────────────────────────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 9.6 Detalle documental inteligente

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ Documento DOC-901                                  Estado: Revision · Confianza global: 72%  │
├──────────────────────────────────────┬───────────────────────────────────────────────────────┤
│ Preview                              │ Datos extraidos                                      │
│ ┌──────────────────────────────────┐ │ Proveedor      [ACME SpA                    ]        │
│ │                                  │ │ RUT/Tax ID     [76.123.456-7                ]        │
│ │        PDF / Imagen              │ │ Fecha          [2026-05-16                  ]        │
│ │                                  │ │ Total          [$980.000                    ]        │
│ │                                  │ │ Moneda         [CLP                         ]        │
│ └──────────────────────────────────┘ │ Centro costo   [FINANZAS                    ]        │
│                                      │ [Guardar cambios] [Aprobar] [Rechazar]              │
├──────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ Texto OCR                            │ Validaciones                                         │
│ "Factura electronica..."            │ ⚠ Confianza OCR baja en total                        │
│                                      │ ✓ Moneda permitida                                   │
│                                      │ ⚠ Proveedor requiere confirmacion                    │
├──────────────────────────────────────┴───────────────────────────────────────────────────────┤
│ Timeline: Cargado → OCR → IA → Regla contable → Revision pendiente                           │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 9.7 Bandeja de revision

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ Revision inteligente                                      Prioridad: Alta ▾  Asignado a mi ▾ │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌───────────────────────────────┐ ┌──────────────────────────────────────────────────────┐  │
│ │ Cola de revision              │ │ Decision asistida                                    │  │
│ │                               │ │ DOC-901 · factura_901.pdf                            │  │
│ │ 🔴 DOC-901 72% Monto alto     │ │                                                      │  │
│ │ 🟠 DOC-899 81% Moneda USD     │ │ Motivos:                                             │  │
│ │ 🟡 DOC-870 88% Campo faltante │ │ 1. Confianza OCR baja en total                       │  │
│ │                               │ │ 2. Proveedor requiere confirmacion                   │  │
│ │                               │ │ 3. Regla contable pide revision manual               │  │
│ └───────────────────────────────┘ │                                                      │  │
│                                   │ Recomendacion: Corregir proveedor y aprobar          │  │
│                                   │                                                      │  │
│                                   │ [Corregir campos] [Aprobar] [Rechazar] [Escalar]     │  │
│                                   └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 9.8 Rendition Studio

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ Nueva rendicion                                                                               │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Paso 1 Periodo → Paso 2 Filtros → Paso 3 Preview → Paso 4 Validacion → Paso 5 Descargar       │
│                                                                                              │
│ Paso 3: Preview de documentos incluidos                                                       │
│ ┌────────────────────────────────────────────────────────────────────────────────────────┐   │
│ │ 184 documentos encontrados · Total CLP $24.880.900 · 3 warnings                         │   │
│ │                                                                                        │   │
│ │ DOC-102  ACME SpA      $120.000    Aprobado       Incluido                             │   │
│ │ DOC-103  Demo Ltda     $80.000     Aprobado       Incluido                             │   │
│ │ DOC-104  Global Inc    USD 88      Warning        Revisar antes de generar              │   │
│ └────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                              │
│ [Volver]                                           [Validar rendicion]                       │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 9.9 Historial de rendiciones

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ Rendiciones                                                                  [Nueva]         │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Periodo ▾ Responsable ▾ Centro costo ▾ Estado ▾ Buscar...                                     │
│                                                                                              │
│ ID              Periodo    Docs    Warnings    Estado       Generada por    Acciones          │
│ REND-2026-05-A  2026-05    184     3           Generada     Ana             Ver · Descargar   │
│ REND-2026-04-B  2026-04    221     0           Descargada   Carlos          Ver · Descargar   │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 9.10 Auditoria

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ Auditoria                                                                                     │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Filtros: Usuario ▾ Accion ▾ Documento/Rendicion ▾ Fecha desde/hasta                           │
│                                                                                              │
│ Fecha                 Usuario       Accion                 Recurso            Empresa         │
│ 2026-05-16 10:42      ana@acme      DOCUMENT_APPROVED      DOC-901            ACME SpA        │
│ 2026-05-16 10:50      ana@acme      RENDITION_GENERATED    REND-2026-05-A     ACME SpA        │
│ 2026-05-16 11:03      auditor@acme  DOCUMENT_VIEWED        DOC-899            ACME SpA        │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 9.11 Observabilidad

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ Observabilidad                                                                                │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                         │
│ │ API          │ │ DB           │ │ Worker       │ │ OCR/IA       │                         │
│ │ OK 42ms      │ │ OK           │ │ OK           │ │ Degradado    │                         │
│ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘                         │
│                                                                                              │
│ Checks                                                                                        │
│ ✓ /health       OK                                                                            │
│ ✓ /liveness     OK                                                                            │
│ ✓ /readiness    OK                                                                            │
│ ⚠ Ollama        Timeout intermitente                                                          │
│                                                                                              │
│ [Copiar diagnostico] [Reintentar checks]                                                       │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 9.12 Configuracion

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ Configuracion                                                                                 │
├──────────────────────┬───────────────────────────────────────────────────────────────────────┤
│ Secciones            │ Empresas                                                              │
│ ▸ Empresas           │ ┌──────────────────────────────────────────────────────────────────┐  │
│ ▸ Usuarios           │ │ ACME SpA      Activa      CLP      Reglas: Chile v1              │  │
│ ▸ Roles              │ │ Demo Ltda     Activa      CLP      Reglas: Chile v1              │  │
│ ▸ Reglas contables   │ └──────────────────────────────────────────────────────────────────┘  │
│ ▸ Plantillas XLSX    │                                                                       │
└──────────────────────┴───────────────────────────────────────────────────────────────────────┘
```

## 9.13 Responsive mobile

```text
┌──────────────────────────────┐
│ CAPTRE        Empresa ▾  ☰   │
├──────────────────────────────┤
│ Buscar...                    │
│                              │
│ Docs procesados              │
│ ┌──────────────────────────┐ │
│ │ 1.248                    │ │
│ └──────────────────────────┘ │
│                              │
│ Pendientes revision          │
│ ┌──────────────────────────┐ │
│ │ 17                       │ │
│ └──────────────────────────┘ │
│                              │
│ Acciones rapidas             │
│ [Cargar] [Revisar] [Rendir]  │
└──────────────────────────────┘
```

## 10. Mapa de rutas propuesto

```text
/login
/select-company
/dashboard
/documents
/documents/upload
/documents/:documentId
/reviews
/reviews/:documentId
/renditions
/renditions/new
/renditions/:renditionId
/audit
/observability
/settings/companies
/settings/users
/settings/roles
/settings/accounting-rules
/settings/templates
/forbidden
/session-expired
/not-found
```

## 11. Estructura de carpetas propuesta

```text
apps/front
├── src
│   ├── app
│   │   ├── router.tsx
│   │   ├── providers.tsx
│   │   └── app-shell.tsx
│   ├── features
│   │   ├── auth
│   │   ├── dashboard
│   │   ├── documents
│   │   ├── upload
│   │   ├── reviews
│   │   ├── renditions
│   │   ├── audit
│   │   ├── observability
│   │   └── settings
│   ├── shared
│   │   ├── api
│   │   ├── components
│   │   ├── hooks
│   │   ├── schemas
│   │   ├── styles
│   │   └── utils
│   ├── test
│   └── main.tsx
├── e2e
├── public
├── package.json
├── vite.config.ts
├── tsconfig.json
└── playwright.config.ts
```

## 12. Criterios GO/NO-GO antes de implementar

### GO si se cumple

- Hay aprobacion del stack propuesto o una variante equivalente.
- Se acepta migracion incremental desde la SPA actual.
- Estan claros los endpoints de auth/documentos/reviews/renditions/observabilidad.
- Se define prioridad de modulos para el primer corte.
- Se acepta incorporar pruebas Playwright desde el inicio.

### NO-GO temporal si ocurre

- No hay acuerdo sobre autenticacion real y RBAC en front.
- No existen contratos API suficientes para listar documentos/rendiciones de forma persistente.
- Se exige solo maquillar CSS sin resolver arquitectura.
- No se aprueba una estrategia minima de QA.

## 13. Primer corte recomendado

Para obtener valor rapido sin esperar todo el rediseño:

1. Fundacion React/TS.
2. App shell AAA.
3. Login real.
4. Dashboard con datos basicos.
5. Centro documental con tabla y detalle.
6. Carga documental mejorada.
7. Smoke tests.

Este corte ya permitiria mostrar una version comercialmente presentable, aunque revision avanzada, Rendition Studio y observabilidad queden para cortes posteriores.

## 14. Definicion de done global

- Front levanta con comando oficial desde raiz.
- Pantallas principales son responsive.
- No hay JSON crudo como experiencia principal de usuario final.
- Rutas criticas protegidas por sesion y rol.
- Acciones criticas tienen feedback visual.
- Errores API son legibles para usuario operativo.
- Hay smoke tests Playwright para login, dashboard, carga, revision y rendicion.
- README de `apps/front` queda actualizado.
- Cambios se mapean al roadmap maestro del proyecto.

## 15. Avance implementado - Primer corte estatico AAA (2026-05-16)

Estado: COMPLETADO.

Este avance transforma la SPA estatica existente en una primera version de consola AAA manteniendo la ejecucion sin dependencias externas. La decision reduce riesgo y permite validar experiencia, navegacion y flujos antes de aprobar la migracion completa a Vite + React + TypeScript.

### Alcance completado

- App shell enterprise con sidebar, topbar, breadcrumb, busqueda global, usuario, rol y empresa activa.
- Login real contra API con soporte de access/refresh token y modo demo para validacion visual.
- RBAC visual por rol `admin`, `contador`, `ejecutivo` y `auditor`.
- Dashboard operacional con KPIs, pipeline documental, riesgos y actividad reciente.
- Centro documental con filtros, tabla, detalle, export CSV y reprocesamiento.
- Carga documental avanzada con drag & drop, carga multiple, validacion y cola por archivo.
- Revision inteligente con cola, detalle, approve/reject y overrides.
- Rendition Studio con wizard visual, preview, generacion por filtro, historial y descarga autenticada.
- Auditoria local para acciones de usuario.
- Observabilidad con checks de health, liveness y readiness.
- Configuracion inicial con API base, empresa, rol y rutas permitidas.
- Documentacion actualizada en `apps/front/README.md`.

### Skills efectivamente aplicadas

- `frontend-responsive-design-standards`: layout responsive, app shell, cards, tablas, estados y mobile menu.
- `security-best-practices`: login real, tokens, refresh, RBAC visual y aislamiento por empresa activa.
- `refactor`: reemplazo incremental de la SPA sin cambiar el comando oficial de ejecucion.
- `playwright`: queda pendiente como suite formal; este corte deja estructura funcional lista para smoke tests.

### Agentes / responsabilidades ejecutadas

- Agente principal:
  - Reviso lineamientos del proyecto.
  - Implemento el primer corte funcional.
  - Documento el avance.
  - Ejecuto checks locales.

### Limitaciones conocidas

- Todavia no se migra a React/TypeScript; esa migracion queda para la siguiente fase aprobada.
- No existe endpoint de listado documental persistente en el contrato revisado; el centro documental combina estado local con respuestas de acciones disponibles.
- No existe endpoint de listado historico de rendiciones en el contrato revisado; el historial se mantiene localmente para esta iteracion.
- La auditoria de UI es local hasta que exista contrato API persistente.
- El preview real de PDF/imagen queda pendiente de un endpoint seguro de descarga/original.

### Siguiente fase recomendada

1. Validar visualmente la consola con usuarios del proyecto.
2. Confirmar si se aprueba migracion a Vite + React + TypeScript.
3. Agregar endpoints faltantes de listados persistentes si se requiere operacion multiusuario real.
4. Implementar Playwright smoke tests sobre login, dashboard, upload, review, renditions y observability.
