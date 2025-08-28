# test_webhook.py
import requests
import json

def test_new_webhook_format():
    """Test the new webhook payload format"""
    
    # Your provided payload
    payload = {
        "event_id": "webhook-test-12345",
        "tenant_id": "calm-dental",
        "provider": "wix",
        "event_type": "lead.submitted",
        "occurred_at": "2025-08-27T15:30:00Z",
        "source_ids": {
            "form_id": "abc123",
            "page_url": "https://calm-dental.com/contact"
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
                    "marketing": True,
                    "terms": True
                },
                "utm": {
                    "source": "wix",
                    "medium": "form",
                    "campaign": "veneers"
                },
                "submitted_at": "2025-08-27T15:30:00Z",
                "ip": "203.0.113.10"
            }
        }
    }
    
    # Send to webhook endpoint
    url = "http://127.0.0.1:8000/v1/webhooks/calm-dental/wix"
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 202:
            print("✅ New webhook format test PASSED")
        else:
            print("❌ New webhook format test FAILED")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to webhook server. Make sure it's running on 127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def test_legacy_webhook_format():
    """Test backward compatibility with legacy webhook format"""
    
    # Legacy payload format
    payload = {
        "form_id": "legacy123",
        "lead": {
            "first_name": "John",
            "last_name": "Smith",
            "email": "john@example.com",
            "phone": "+15551234567",
            "message": "Interested in dental implants",
            "page_url": "https://legacy-site.com/contact"
        },
        "ad_id": "ad456",
        "appointment_id": "apt789"
    }
    
    # Send to webhook endpoint
    url = "http://127.0.0.1:8000/v1/webhooks/legacy-tenant/typeform"
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 202:
            print("✅ Legacy webhook format test PASSED")
        else:
            print("❌ Legacy webhook format test FAILED")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to webhook server. Make sure it's running on 127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    print("Testing new webhook payload format...")
    test_new_webhook_format()
    print("\nTesting legacy webhook format (backward compatibility)...")
    test_legacy_webhook_format()
    print("\nDone!")
