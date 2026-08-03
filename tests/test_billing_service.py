import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app
from backend.db.database import SessionLocal
from backend.models.user import User
from backend.core.token import create_access_token
from backend.services.billing_service import BillingService

client = TestClient(app)

import uuid

def test_billing_and_quota_flow():
    db = SessionLocal()
    email = f"billing_{uuid.uuid4().hex[:8]}@scriptloom.ai"
    user = User(name="Sarah Jenkins", email=email, hashed_password="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id
    db.close()

    token = create_access_token({"sub": str(user_id)})
    headers = {"Authorization": f"Bearer {token}"}

    print("\n--- 1. Fetching Initial Subscription & Usage ---")
    sub_res = client.get("/billing/subscription", headers=headers)
    print("Subscription Status:", sub_res.status_code)
    print("Subscription Output:", sub_res.json())

    assert sub_res.status_code == 200
    assert sub_res.json()["plan_name"] == "starter"

    usage_res = client.get("/billing/usage", headers=headers)
    print("Usage Status:", usage_res.status_code)
    print("Usage Output:", usage_res.json())

    assert usage_res.status_code == 200
    assert usage_res.json()["hours_limit"] == 5.0

    print("\n--- 2. Upgrading Subscription to Founder Pro ($49/mo) ---")
    upgrade_res = client.post(
        "/billing/upgrade",
        json={"plan_name": "founder_pro"},
        headers=headers,
    )
    print("Upgrade Status:", upgrade_res.status_code)
    print("Upgrade Output:", upgrade_res.json())

    assert upgrade_res.status_code == 200
    assert upgrade_res.json()["plan_name"] == "founder_pro"

    print("\n--- 3. Verifying Expanded Limits ---")
    updated_usage = client.get("/billing/usage", headers=headers)
    print("Updated Usage Limit:", updated_usage.json()["hours_limit"])
    assert updated_usage.json()["hours_limit"] == 50.0

    print("\n--- 4. Testing Quota Exceeded Enforcement ---")
    db_session = SessionLocal()
    billing = BillingService(db_session)
    # Simulate processing 51 hours
    billing.record_usage(user_id=user_id, duration_seconds=51 * 3600.0)

    try:
        billing.check_quota(user_id=user_id, duration_seconds=3600.0)
        quota_blocked = False
    except Exception as exc:
        print("Quota enforcement triggered:", exc.detail if hasattr(exc, "detail") else exc)
        quota_blocked = True

    db_session.close()
    assert quota_blocked is True, "Quota check should block when limit exceeded"

    print("\n[SUCCESS] All Billing & Usage System tests PASSED!")

if __name__ == "__main__":
    test_billing_and_quota_flow()
