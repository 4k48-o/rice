
import asyncio
import sys
import os
import httpx
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.append(os.getcwd())

from app.main import app
from app.core import security
from app.core.config import settings

async def run_tests():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        print("\n--- 1. Testing Password Complexity (User Create) ---")
        # Login as admin to create user (assuming we need auth, but schema validation happens anyway)
        # Actually validation happens at Pydantic level, so we expect 422 if we hit the endpoint.
        # But for this test, let's just use the schema validation mechanism via API or mock?
        # Let's try to create a user with weak password
        
        # We need a token first... assuming we have admin/admin123 (created before policy?)
        # If admin123 is weak but already in DB, it works.
        
        # Login
        resp = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
        if resp.json()["code"] != 200:
            print("Skipping creation test: Admin login failed (maybe policy applied to admin too?)")
        else:
            token = resp.json()["data"]["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Weak password
            payload = {
                "username": "weak_user",
                "password": "123", # Too short
                "real_name": "Weak"
            }
            resp = await client.post("/api/v1/users", json=payload, headers=headers)
            print(f"Weak Password Response: {resp.json()}")
            assert resp.status_code == 422 # Validation Error
            
            # Complex Password
            payload["password"] = "StrongP@ss1" 
            payload["username"] = "strong_user"
            resp = await client.post("/api/v1/users", json=payload, headers=headers)
            print(f"Strong Password Response: {resp.json()}")
            # It might fail due to other value errors or successful. 200 or 10001 (exists)
            
        print("\n--- 2. Testing Password Expiration ---")
        # We can't easily mock DB state here without full fixture.
        # But we can unit test the utility function.
        
        # Test Not Expired
        now = datetime.utcnow()
        assert security.is_password_expired(now) == False
        
        # Test Expired
        old_date = now - timedelta(days=settings.PASSWORD_EXPIRE_DAYS + 1)
        assert security.is_password_expired(old_date) == True
        
        print("Password Expiration Logic Verified.")

if __name__ == "__main__":
    asyncio.run(run_tests())
