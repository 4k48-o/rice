
import asyncio
import sys
import os
import httpx
from datetime import datetime

# Add backend directory to path
sys.path.append(os.getcwd())

# Force Redis Password (override .env)
# Use environment variable or empty password for test Redis
os.environ["REDIS_PASSWORD"] = os.getenv("TEST_REDIS_PASSWORD", "")

from app.main import app

async def run_tests():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        print("\n--- Testing Single Session ---")
        
        # 1. Login First time
        print("Login 1...")
        try:
            resp1 = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
        except Exception as e:
            print(f"CRITICAL ERROR during Login 1: {e}")
            return

        if resp1.status_code != 200:
            print(f"Login 1 failed: {resp1.json()}")
            return
        token1 = resp1.json()["data"]["access_token"]
        print("Token 1 obtained.")
        
        # 2. Verify Token 1 works
        headers1 = {"Authorization": f"Bearer {token1}"}
        resp = await client.get("/api/v1/users", headers=headers1)
        print(f"Token 1 Access: {resp.status_code}")
        assert resp.status_code == 200
        
        # 3. Login Second time (Same user)
        print("Login 2...")
        resp2 = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
        token2 = resp2.json()["data"]["access_token"]
        print("Token 2 obtained.")
        
        # 4. Verify Token 1 is now INVALID
        print("Verifying Token 1 is kicked out...")
        resp = await client.get("/api/v1/users", headers=headers1)
        print(f"Token 1 Access (Should fail): {resp.status_code}, Body: {resp.json()}")
        assert resp.status_code == 401
        assert resp.json()["message"] == "账号已在其他地方登录" # Unified response uses 'message'
        
        # 5. Verify Token 2 works
        print("Verifying Token 2 works...")
        headers2 = {"Authorization": f"Bearer {token2}"}
        resp = await client.get("/api/v1/users", headers=headers2)
        print(f"Token 2 Access: {resp.status_code}")
        assert resp.status_code == 200
        
        print("\nSUCCESS: Single User Session Verified!")

if __name__ == "__main__":
    asyncio.run(run_tests())
