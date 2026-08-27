# Module 03 — Asset Management & Intelligence

## Purpose
The Asset Management module establishes the foundational "Asset Intelligence" layer for the Cyber Risk Quantification Platform. It provides a system of record for all organizational devices, applications, and resources, tracking their configurations, ownership, criticality, and internet exposure.

> [!IMPORTANT]
> **Asset Criticality is NOT Cyber Risk.**
> 
> The Asset Criticality score (0-100) reflects the business importance of the asset in isolation. It does not measure the likelihood or financial impact of a cyber incident. 
> 
> **Workflow**: Asset Criticality → Future Risk Engine → Cyber Risk → Financial Risk

## Asset Lifecycle
Assets move through the following statuses:
1. **Active**: Operating normally in the environment.
2. **Maintenance**: Temporarily offline or under configuration changes.
3. **Inactive**: Stopped or suspended but still retained.
4. **Retired**: Safely decommissioned. 
   - We prefer **logical retirement** (`POST /api/v1/assets/{id}/retire`) over physical deletion (`DELETE`) to preserve historical risk and telemetry records linked to the asset.

## Asset Model Fields
| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `organization_id` | UUID | Multi-tenant organization grouping |
| `name` | String | Human readable asset name |
| `asset_type` | Enum | E.g., `server`, `database`, `application`, `network_device` |
| `environment` | Enum | `production`, `staging`, `development`, `testing` |
| `criticality` | Integer | Scale of 0-100 measuring isolated business importance |
| `business_value` | Float | Monetary estimate of the asset's value |
| `owner`, `department` | String | Ownership and organizational mapping |
| `hostname`, `ip_address` | String | Network identifiers (uniqueness enforced per org) |
| `internet_exposed` | Boolean | True if the asset is reachable from the public internet |

## Criticality Model
Criticality visually maps to the following tiers in the UI:
- **0–20**: Very Low
- **21–40**: Low
- **41–60**: Medium
- **61–80**: High
- **81–100**: Critical

## API Endpoints
- `GET /api/v1/assets/` - Search, filter, and paginate assets.
- `POST /api/v1/assets/` - Create a new asset.
- `GET /api/v1/assets/{id}` - Retrieve detailed asset information.
- `PUT /api/v1/assets/{id}` - Update asset attributes.
- `POST /api/v1/assets/{id}/retire` - Safely mark an asset as retired.
- `GET /api/v1/assets/{id}/posture` - Retrieve aggregated counts (vulns, telemetry).
- `GET /api/v1/assets/{id}/vulnerabilities` - Retrieve paginated vulnerabilities.
- `GET /api/v1/assets/{id}/telemetry` - Retrieve paginated telemetry.

## Search and Filter Behavior
The API uses parameter-driven querying. `search` performs case-insensitive wildcard matches (`ilike`) on `name`, `hostname`, `owner`, `department`, and `technology`.
Filters (e.g., `environment=production`, `criticality_min=80`) run against indexed columns where possible to ensure performance at scale.

## Security Considerations
- **Validation**: Strict Pydantic parsing enforces constraints (e.g. CVSS 0-10, Criticality 0-100) and formats (e.g., Hostname regex, IPv4/IPv6).
- **Injection Prevention**: The API utilizes SQLAlchemy parametrized queries. Sorting parameters are explicitly allowlisted (e.g., `sort_by` must be exactly `name`, `criticality`, etc).

## Future Integration
The asset intelligence gathered by this module (Criticality, Business Value, Environment, Internet Exposure) will be directly ingested by the **Risk Engine (Module 05/06)** to contextualize vulnerabilities and telemetry, dynamically producing actionable Financial Risk scores.
