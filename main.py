# main.py
from fastapi import FastAPI, Request, HTTPException
from starlette.responses import JSONResponse
import json, uuid
from datetime import datetime
from typing import Optional

from db import SessionLocal
from models import Lead

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Webhook Lead Ingestion Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "webhook-ingestion"}

@app.get("/v1/webhooks/{tenant}/{provider}")
async def check_webhook(tenant: str, provider: str):
    return {"message": f"Webhook is alive for tenant={tenant}, provider={provider}"}


@app.post("/v1/webhooks/{tenant}/{provider}")
async def ingest(tenant: str, provider: str, request: Request):
    raw = await request.body()
    body = json.loads(raw)

    db = SessionLocal()

    try:
        # Handle new webhook payload format
        if "payload" in body and "lead" in body["payload"]:
            # New format with structured payload
            webhook_data = body
            lead_data = webhook_data["payload"]["lead"]
            
            # Extract webhook metadata
            event_id = webhook_data.get("event_id")
            tenant_id = webhook_data.get("tenant_id", tenant)
            provider_name = webhook_data.get("provider", provider)
            event_type = webhook_data.get("event_type", "lead.submitted")
            occurred_at_str = webhook_data.get("occurred_at")
            payload_version = webhook_data.get("payload_v", 1)
            source_ids = webhook_data.get("source_ids", {})
            
            # Parse occurred_at timestamp
            occurred_at = None
            if occurred_at_str:
                try:
                    occurred_at = datetime.fromisoformat(occurred_at_str.replace('Z', '+00:00'))
                except ValueError:
                    occurred_at = datetime.utcnow()
            else:
                occurred_at = datetime.utcnow()
            
            # Parse submitted_at timestamp
            submitted_at = None
            submitted_at_str = lead_data.get("submitted_at")
            if submitted_at_str:
                try:
                    submitted_at = datetime.fromisoformat(submitted_at_str.replace('Z', '+00:00'))
                except ValueError:
                    submitted_at = occurred_at
            else:
                submitted_at = occurred_at
            
            # Extract lead information
            first_name = lead_data.get("first_name", "")
            last_name = lead_data.get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            
            # Extract consent information
            consent = lead_data.get("consent", {})
            marketing_consent = consent.get("marketing", None)
            terms_consent = consent.get("terms", None)
            
            # Extract UTM information
            utm = lead_data.get("utm", {})
            utm_source = utm.get("source")
            utm_medium = utm.get("medium")
            utm_campaign = utm.get("campaign")
            utm_term = utm.get("term")
            utm_content = utm.get("content")
            
            # Get page URL from source_ids or lead data
            page_url = source_ids.get("page_url") or lead_data.get("page_url")
            
            new_lead = Lead(
                # Webhook metadata
                event_id=event_id,
                tenant_id=tenant_id,
                provider=provider_name,
                event_type=event_type,
                occurred_at=occurred_at,
                payload_version=payload_version,
                source_ids=source_ids,
                
                # Legacy compatibility
                source=provider_name,
                source_lead_id=source_ids.get("form_id"),
                
                # Lead information
                first_name=first_name,
                last_name=last_name,
                full_name=full_name,
                phone_number=lead_data.get("phone"),
                email=lead_data.get("email"),
                message=lead_data.get("message"),
                page_url=page_url,
                ip_address=lead_data.get("ip"),
                submitted_at=submitted_at,
                
                # Consent
                marketing_consent=marketing_consent,
                terms_consent=terms_consent,
                
                # UTM tracking
                utm_source=utm_source,
                utm_medium=utm_medium,
                utm_campaign=utm_campaign,
                utm_term=utm_term,
                utm_content=utm_content,
                
                # Store full payload
                meta_data=webhook_data
            )
            
        else:
            # Legacy format for backward compatibility
            lead = body.get("lead", body)
            full_name = f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()

            new_lead = Lead(
                # Generate required fields for legacy data
                event_id=str(uuid.uuid4()),
                tenant_id=tenant,
                provider=provider,
                event_type="lead.submitted",
                occurred_at=datetime.utcnow(),
                payload_version=0,  # Mark as legacy
                
                # Legacy fields
                source=provider,
                source_lead_id=body.get("form_id"),
                full_name=full_name,
                phone_number=lead.get("phone"),
                message=lead.get("message"), 
                page_url=lead.get("page_url"),
                email=lead.get("email"),
                ad_id=body.get("ad_id"),
                appointment_id=body.get("appointment_id"),
                
                # Store original payload
                meta_data=body
            )

        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error processing webhook: {str(e)}")
    finally:
        db.close()

    return JSONResponse(
        status_code=202,
        content={"ok": True, "id": new_lead.id, "correlation_id": str(uuid.uuid4())}
    )
