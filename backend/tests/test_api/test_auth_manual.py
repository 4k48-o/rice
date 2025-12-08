import asyncio
import sys
import os
import httpx

# Add backend directory to path
sys.path.append(os.getcwd())

from app.main import app

async def run_tests():
    """Run all tests with shared client."""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        # Test Case 1: Login
        print("\n--- Test Case 1: Login with correct credentials ---")
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        # print(f"Response: {response.json()}")
        
        access_token = None
        if response.status_code == 200:
            token_data = response.json()["data"]
            access_token = token_data["access_token"]
            print("✅ Login successful!")
        else:
            print("❌ Login failed!")
            return

        # Test Case 2: User Info
        print("\n--- Test Case 2: Access Protected Route (User Info) ---")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/api/v1/auth/user-info", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200: 
             print("✅ Get User Info successful!")
             data = response.json()["data"]
             print(f"User: {data['username']}, ID: {data['id']}")
        else:
             print("❌ Get User Info failed!")
             
        # Test Case 3: Refresh Token
        print("\n--- Test Case 3: Refresh Token ---")
        refresh_token = token_data["refresh_token"]
        response = await client.post("/api/v1/auth/refresh", params={"refresh_token": refresh_token})
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Refresh Token successful!")
            new_token_data = response.json()["data"]
            print(f"New Access Token: {new_token_data['access_token'][:20]}...")
        else:
            print(f"❌ Refresh Token failed: {response.text}")

if __name__ == "__main__":
    asyncio.run(run_tests())
