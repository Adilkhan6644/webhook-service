# models.py
from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, Boolean, func
from db import Base

class Lead(Base):
    __tablename__ = "Leads"

    id = Column(Integer, primary_key=True, index=True)
    # Webhook metadata
    event_id = Column(String(255), unique=True, nullable=False)
    tenant_id = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)
    event_type = Column(String(50), nullable=False)
    occurred_at = Column(TIMESTAMP, nullable=False)
    payload_version = Column(Integer, default=1)
    
    # Source information
    source_ids = Column(JSON)  # Contains form_id, page_url, etc.
    
    # Legacy fields (keeping for backward compatibility)
    source = Column(String(50), nullable=True)  # Now maps to provider
    source_lead_id = Column(String(255))  # Now maps to source_ids.form_id
    ad_id = Column(String(255))
    appointment_id = Column(String(255))
    
    # Lead information
    first_name = Column(String(255))
    last_name = Column(String(255))
    full_name = Column(String(255))
    phone_number = Column(String(50))
    email = Column(String(255))
    message = Column(String(1000))
    page_url = Column(String(1000))
    ip_address = Column(String(45))  # Supports both IPv4 and IPv6
    submitted_at = Column(TIMESTAMP)
    
    # Consent information
    marketing_consent = Column(Boolean)
    terms_consent = Column(Boolean)
    
    # UTM tracking
    utm_source = Column(String(255))
    utm_medium = Column(String(255))
    utm_campaign = Column(String(255))
    utm_term = Column(String(255))
    utm_content = Column(String(255))
    
    # Full payload storage
    meta_data = Column(JSON)
    
    # Timestamps
    created_on = Column(TIMESTAMP, server_default=func.now())
    updated_on = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
