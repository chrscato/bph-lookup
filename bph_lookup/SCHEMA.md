# BPH Lookup Database Schema

## Table: state
- `state_code` (PK): 2-char state code (e.g., 'CA', 'NY')
- `state_name`: Full state name
- `effective_date`: Date record became effective
- `expiration_date`: Date record expires (nullable)
- `has_regions`: Boolean, if state uses sub-regions for rates
- `data_source`, `data_url`, `notes`: Source and meta info

## Table: region
- `region_id` (PK): Auto-increment ID
- `state_code` (FK): Links to `state`
- `region_type`: e.g., 'Geographic', 'Carrier'
- `region_code`, `region_name`: Codes and display names
- UNIQUE (state_code, region_type, region_code)

## Table: procedure_code
- `procedure_code` (PK): CPT/HCPCS code
- `description`: Long description of procedure
- `code_type`: E.g., CPT/HCPCS/DRG
- `category`, `subcategory`: For analytics/grouping

## Table: fee_schedule
- `id` (PK): Auto
- `state_code` (FK): State
- `schedule_type`: e.g., Physician, Hospital
- `effective_date`, `expiration_date`, `conversion_factor`, `notes`

## Table: fee_schedule_rate
- `id` (PK): Auto
- `fee_schedule_id` (FK)
- `procedure_code` (FK)
- `modifier`, `region_id` (FK), `rate`, `rate_unit`, etc.
- UNIQUE (fee_schedule_id, procedure_code, modifier, region_id)

...  
*(Continue for all tables per your schema!)*  