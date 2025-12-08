import asyncio
import sys
import os
import httpx
import time

# Add backend directory to path
sys.path.append(os.getcwd())

from app.main import app

async def run_tests():
    """Run User CRUD tests."""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        # 1. Login
        print("\n--- 1. Login ---")
        login_data = {"username": "admin", "password": "admin123"}
        response = await client.post("/api/v1/auth/login", json=login_data)
        access_token = response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        print("✅ Login successful")

        # 2. Create User
        print("\n--- 2. Create User ---")
        new_username = f"user_{int(time.time())}"
        user_data = {
            "username": new_username,
            "password": "password123",
            "real_name": "Test User",
            "nickname": "Tester",
            "email": f"{new_username}@example.com",
            "status": 1
        }
        response = await client.post("/api/v1/users", json=user_data, headers=headers)
        print(f"Create Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code != 200:
             print("❌ Create failed")
             return
             
        user_id = response.json()["data"]["id"]
        print(f"✅ User created with ID: {user_id}")

        # 3. Get User List
        print("\n--- 3. Get User List ---")
        response = await client.get("/api/v1/users", headers=headers, params={"username": new_username})
        print(f"List Status: {response.status_code}")
        data = response.json()["data"]
        items = data["items"]
        print(f"items found: {len(items)}")
        
        found = False
        for item in items:
            if item["id"] == user_id:
                found = True
                print(f"Found User: {item['username']} / {item['real_name']}")
                break
        
        if found:
            print("✅ User found in list")
        else:
            print("❌ User NOT found in list")

        # 4. Update User
        print("\n--- 4. Update User ---")
        update_data = {"nickname": "Updated Tester", "remark": "Updated remark"}
        response = await client.put(f"/api/v1/users/{user_id}", json=update_data, headers=headers)
        print(f"Update Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ User updated")
        else:
            print("❌ Update failed")

        # 4.5. Reset Password
        print("\n--- 4.5. Reset Password ---")
        reset_data = {"password": "newpassword123"}
        response = await client.post(f"/api/v1/users/{user_id}/reset-password", json=reset_data, headers=headers)
        print(f"Reset Status: {response.status_code}")
        if response.status_code == 200:
             print("✅ Password reset successful")
        else:
             print("❌ Password reset failed")

        # 5. Delete User
        print("\n--- 5. Delete User ---")
        response = await client.delete(f"/api/v1/users/{user_id}", headers=headers)
        print(f"Delete Status: {response.status_code}")
        if response.status_code == 200:
             print("✅ User deleted")
        else:
             print("❌ Delete failed")

        # 6. Verify Delete
        print("\n--- 6. Verify Delete ---")
        response = await client.get("/api/v1/users", headers=headers, params={"username": new_username})
        # Note: Depending on implementation, it might return empty list or not include deleted user
        items = response.json()["data"]["items"]
        found = False
        for item in items:
            if item["id"] == user_id:
                found = True
                break
                
        if not found:
            print("✅ User successfully removed from list")
        else:
            print("❌ User still appears in list (Soft delete?)")

if __name__ == "__main__":
    asyncio.run(run_tests())
