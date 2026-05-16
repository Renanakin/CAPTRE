# Especificacion de Modelo de Datos V2

## Tabla documents
- id UUID PK
- tenant_id VARCHAR(64) NOT NULL
- document_hash CHAR(64) NOT NULL
- file_name VARCHAR(255) NOT NULL
- mime_type VARCHAR(64) NOT NULL
- source_channel VARCHAR(32) DEFAULT 'api'
- status VARCHAR(32) NOT NULL
- created_at TIMESTAMP NOT NULL
- updated_at TIMESTAMP NOT NULL

Indices:
- UNIQUE (tenant_id, document_hash)
- INDEX (tenant_id, status)

## Tabla document_extractions
- id UUID PK
- document_id UUID FK documents(id)
- provider VARCHAR(64) NOT NULL
- document_type VARCHAR(32)
- country_code VARCHAR(8)
- confidence NUMERIC(5,4)
- extraction JSONB NOT NULL
- raw_extraction JSONB
- extra_fields JSONB
- created_at TIMESTAMP NOT NULL

Indices:
- INDEX (document_id)
- INDEX (country_code, document_type)

## Tabla document_financials
- id UUID PK
- document_id UUID FK documents(id)
- currency CHAR(3)
- subtotal NUMERIC(18,2)
- tax NUMERIC(18,2)
- total NUMERIC(18,2)
- amount_due NUMERIC(18,2)
- fx_rate NUMERIC(18,6)
- total_clp NUMERIC(18,2)
- fx_source VARCHAR(64)
- fx_date DATE
- created_at TIMESTAMP NOT NULL

## Tabla document_template_mapping
- id UUID PK
- document_id UUID FK documents(id)
- header_fields JSONB NOT NULL
- detail_fields JSONB NOT NULL
- missing_fields JSONB NOT NULL
- warnings_count INT NOT NULL DEFAULT 0
- created_at TIMESTAMP NOT NULL

Uso:
- header_fields: Responsable, Rut, Periodo, Monto a pagar, Fecha, Autorizado por
- detail_fields: Mes, Cuenta, Descripcion Cuenta, Fecha, Nro Boleta Factura, Descripcion del gasto, Concepto, Centro Costo, PROVEEDOR, RUT, Observaciones, Total

## Tabla renditions
- id UUID PK
- tenant_id VARCHAR(64) NOT NULL
- period VARCHAR(7) NOT NULL
- template_version VARCHAR(64) NOT NULL
- file_url TEXT
- status VARCHAR(32) NOT NULL
- warnings_count INT NOT NULL DEFAULT 0
- generated_at TIMESTAMP
- created_at TIMESTAMP NOT NULL

## Tabla rendition_items
- id UUID PK
- rendition_id UUID FK renditions(id)
- document_id UUID FK documents(id)
- row_number INT NOT NULL
- fields JSONB NOT NULL
- warnings JSONB

## Tabla audit_events
- id UUID PK
- entity_type VARCHAR(32) NOT NULL
- entity_id UUID NOT NULL
- event_type VARCHAR(64) NOT NULL
- payload JSONB NOT NULL
- actor_id VARCHAR(64)
- created_at TIMESTAMP NOT NULL

Eventos sugeridos:
- DOCUMENT_RECEIVED
- DOCUMENT_CLASSIFIED
- EXTRACTION_COMPLETED
- MAPPING_WITH_WARNINGS
- REVIEW_REQUIRED
- OVERRIDE_APPLIED
- RENDITION_GENERATED
