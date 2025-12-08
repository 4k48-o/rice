"""
Quick test script to verify Snowflake ID integration with User model.
"""
import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.getcwd())

# Force config before app import
os.environ["SNOWFLAKE_DATACENTER_ID"] = "1"
os.environ["SNOWFLAKE_WORKER_ID"] = "1"
# Use environment variable or empty password for test Redis
os.environ["REDIS_PASSWORD"] = os.getenv("TEST_REDIS_PASSWORD", "")


from app.main import app
from httpx import AsyncClient


async def test_user_creation_with_snowflake():
    """Test that creating a user generates a Snowflake ID."""
    print("\n--- Testing Snowflake ID Integration ---")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login as admin
        print("Logging in as admin...")
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        
        if login_resp.status_code != 200:
            print(f"Login failed: {login_resp.json()}")
            return
        
        token = login_resp.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a new user
        print("Creating new user...")
        import time
        username = f"snowflake_test_{int(time.time())}"
        
        create_resp = await client.post(
            "/api/v1/users",
            headers=headers,
            json={
                "username": username,
                "password": "Test@123456",
                "email": f"{username}@example.com",
                "user_type": 2,
                "status": 1
            }
        )
        
        if create_resp.status_code != 200:
            print(f"User creation failed: {create_resp.json()}")
            return
        
        user_data = create_resp.json()["data"]
        user_id = user_data["id"]
        
        print(f"✅ User created successfully!")
        print(f"   User ID: {user_id}")
        print(f"   ID Length: {len(str(user_id))} digits")
        print(f"   Username: {user_data['username']}")
        
        # Verify ID is a Snowflake ID (should be 18-19 digits)
        if len(str(user_id)) >= 18:
            print(f"✅ ID format is correct (Snowflake ID)")
            
            # Parse the ID
            from app.utils.snowflake import parse_id
            parsed = parse_id(user_id)
            print(f"   Parsed ID:")
            print(f"     - Datacenter: {parsed['datacenter_id']}")
            print(f"     - Worker: {parsed['worker_id']}")
            print(f"     - Sequence: {parsed['sequence']}")
            print(f"     - Timestamp: {parsed['timestamp']}")
        else:
            print(f"❌ ID format is incorrect (not a Snowflake ID)")
            print(f"   Expected 18-19 digits, got {len(str(user_id))}")
        
        # Create another user to verify uniqueness
        print("\nCreating second user...")
        username2 = f"snowflake_test2_{int(time.time())}"
        
        create_resp2 = await client.post(
            "/api/v1/users",
            headers=headers,
            json={
                "username": username2,
                "password": "Test@123456",
                "email": f"{username2}@example.com",
                "user_type": 2,
                "status": 1
            }
        )
        
        if create_resp2.status_code == 200:
            user_id2 = create_resp2.json()["data"]["id"]
            print(f"✅ Second user created: ID={user_id2}")
            
            if user_id != user_id2:
                print(f"✅ IDs are unique")
            else:
                print(f"❌ IDs are NOT unique!")
            
            if user_id2 > user_id:
                print(f"✅ IDs are monotonically increasing")
            else:
                print(f"⚠️  Second ID is not greater than first")
        
        print("\n✅ Snowflake ID Integration Test Complete!")


if __name__ == "__main__":
    asyncio.run(test_user_creation_with_snowflake())
