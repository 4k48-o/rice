"""
Manual API test script to validate authentication endpoints.
Run this directly with: python tests/manual_api_test.py
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from httpx import AsyncClient


async def test_authentication():
    """Test authentication endpoints manually."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Authentication API...")
    print("=" * 60)
    
    async with AsyncClient(base_url=base_url) as client:
        # Test 1: Login with missing username
        print("\n1. Test login with missing username...")
        response = await client.post("/api/v1/auth/login", json={
            "password": "Test@123456"
        })
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        print("   ✅ PASSED - Returns 422 for missing username")
        
        # Test 2: Login with missing password
        print("\n2. Test login with missing password...")
        response = await client.post("/api/v1/auth/login", json={
            "username": "testuser"
        })
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        print("   ✅ PASSED - Returns 422 for missing password")
        
        # Test 3: Login with non-existent user
        print("\n3. Test login with non-existent user...")
        response = await client.post("/api/v1/auth/login", json={
            "username": "nonexistent_user_12345",
            "password": "Test@123456"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("   ✅ PASSED - Returns 401 for non-existent user")
        
        # Test 4: Get current user without token
        print("\n4. Test get current user without token...")
        response = await client.get("/api/v1/auth/me")
        assert response.status_code in [401, 404], f"Expected 401/404, got {response.status_code}"
        print(f"   ✅ PASSED - Returns {response.status_code} without token")
        
        # Test 5: Logout without token
        print("\n5. Test logout without token...")
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code in [401, 200], f"Expected 401/200, got {response.status_code}"
        print(f"   ✅ PASSED - Returns {response.status_code} without token")
        
        # Test 6: Invalid token refresh
        print("\n6. Test token refresh with invalid token...")
        response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid_token_12345"
        })
        assert response.status_code in [401, 422], f"Expected 401/422, got {response.status_code}"
        print(f"   ✅ PASSED - Returns {response.status_code} for invalid refresh token")
        
    print("\n" + "=" * 60)
    print("✨ All manual tests PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    print("⚠️  Make sure the server is running on http://localhost:8000")
    print("   Run: cd backend && venv/bin/uvicorn app.main:app --reload\n")
    
    asyncio.run(test_authentication())
