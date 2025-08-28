# Webhook Lead Ingestion Service

This FastAPI service accepts webhook payloads for lead ingestion from various providers (Wix, Typeform, Meta, etc.) and stores them in a PostgreSQL database.

## Features

- **Multi-tenant support**: Each webhook can specify a tenant ID
- **Provider flexibility**: Supports multiple lead providers
- **Comprehensive data capture**: Stores lead information, consent data, UTM tracking, and metadata
- **Backward compatibility**: Maintains support for legacy webhook formats
- **Structured payload**: New webhook format with standardized structure

## New Webhook Payload Format

The service now accepts a standardized webhook payload format:

```json
{
  "event_id": "<provider GUID or computed hash>",
  "tenant_id": "calm-dental",
  "provider": "wix|typeform|meta|...",
  "event_type": "lead.submitted",
  "occurred_at": "2025-08-27T15:30:00Z",
  "source_ids": {
    "form_id": "abc123",
    "page_url": "https://example.com/contact"
  },
  "payload_v": 1,
  "payload": {
    "lead": {
      "first_name": "Jane",
      "last_name": "Doe",
      "email": "jane@example.com",
      "phone": "+12025550123",
      "message": "Interested in veneers",
      "consent": {
        "marketing": true,
        "terms": true
      },
      "utm": {
        "source": "wix",
        "medium": "form",
        "campaign": "veneers",
        "term": "dental veneers",
        "content": "landing-page"
      },
      "submitted_at": "2025-08-27T15:30:00Z",
      "ip": "203.0.113.10"
    }
  }
}
```

## API Endpoints

### POST `/v1/webhooks/{tenant}/{provider}`

Accepts webhook payloads for lead ingestion.

**Parameters:**
- `tenant`: Tenant identifier (e.g., "calm-dental")
- `provider`: Lead provider (e.g., "wix", "typeform", "meta")

**Response:**
```json
{
  "ok": true,
  "id": 123,
  "correlation_id": "uuid-string"
}
```

## Database Schema

The `Leads` table includes the following fields:

### Webhook Metadata
- `event_id`: Unique identifier for the webhook event
- `tenant_id`: Tenant identifier
- `provider`: Lead provider name
- `event_type`: Type of event (e.g., "lead.submitted")
- `occurred_at`: When the event occurred
- `payload_version`: Version of the payload format
- `source_ids`: JSON object with source identifiers

### Lead Information
- `first_name`: Lead's first name
- `last_name`: Lead's last name
- `full_name`: Computed full name
- `email`: Lead's email address
- `phone_number`: Lead's phone number
- `message`: Lead's message or inquiry
- `page_url`: URL where the lead was captured
- `ip_address`: Lead's IP address
- `submitted_at`: When the lead was submitted

### Consent & Compliance
- `marketing_consent`: Marketing consent flag
- `terms_consent`: Terms and conditions consent flag

### UTM Tracking
- `utm_source`: UTM source parameter
- `utm_medium`: UTM medium parameter
- `utm_campaign`: UTM campaign parameter
- `utm_term`: UTM term parameter
- `utm_content`: UTM content parameter

### Legacy Fields (for backward compatibility)
- `source`: Maps to provider
- `source_lead_id`: Maps to source_ids.form_id
- `ad_id`: Advertisement ID
- `appointment_id`: Appointment ID

### System Fields
- `meta_data`: Full webhook payload as JSON
- `created_on`: Record creation timestamp
- `updated_on`: Record update timestamp

## Setup Instructions

### 1. Install Dependencies

```bash
pip install fastapi sqlalchemy psycopg2-binary uvicorn
```

### 2. Configure Database

Update the database URL in `db.py`:

```python
DATABASE_URL = "postgresql://username:password@localhost:5432/database_name"
```

### 3. Initialize Database

For new installations:
```bash
python init_db.py
```

For existing installations (migration):
```bash
python migrate_db.py
```

### 4. Run the Service

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Test the Service

```bash
python test_webhook.py
```

## Migration from Legacy Format

If you have an existing database with the old schema, run the migration script:

```bash
python migrate_db.py
```

This will:
1. Add new columns to the existing table
2. Preserve all existing data
3. Set default values for new fields
4. Generate event IDs for legacy records

## Backward Compatibility

The service maintains full backward compatibility with the legacy webhook format. Legacy payloads will be automatically converted and stored with appropriate default values.

## Testing

Use the provided test script to verify both new and legacy webhook formats:

```bash
python test_webhook.py
```

This will test:
- New standardized webhook format
- Legacy webhook format compatibility
- Database storage and retrieval

## Security Considerations

- All webhook payloads are validated before processing
- IP addresses are captured for audit purposes
- Consent flags are properly stored for HIPAA/GDPR compliance
- Full payload is preserved in `meta_data` for audit trails
