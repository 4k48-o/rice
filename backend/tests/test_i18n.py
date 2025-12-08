
import asyncio
import sys
import os
import httpx

# Add backend directory to path
sys.path.append(os.getcwd())

from app.main import app

async def run_tests():
    # Test English
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        print("\n--- 1. Testing Default (Chinese) ---")
        resp = await client.post("/api/v1/auth/login", json={"username": "test_missing", "password": "123456"})
        print(f"Body: {resp.json()}")
        assert "账号或密码错误" in resp.json()["message"]
        
        print("\n--- 2. Testing English (Query Param) ---")
        resp = await client.post("/api/v1/auth/login?lang=en", json={"username": "test_missing", "password": "123456"})
        print(f"Body: {resp.json()}")
        assert "Invalid username or password" in resp.json()["message"]
        
        print("\n--- 3. Testing Japanese (Header) ---")
        headers = {"Accept-Language": "ja"}
        resp = await client.post("/api/v1/auth/login", json={"username": "test_missing", "password": "123456"}, headers=headers)
        print(f"Body: {resp.json()}")
        assert "ユーザー名またはパスワードが正しくありません" in resp.json()["message"]

if __name__ == "__main__":
    asyncio.run(run_tests())
