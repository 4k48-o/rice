"""
Authentication API tests.
"""
import pytest
from httpx import AsyncClient
from app.models.user import User


class TestLogin:
    """Test login functionality."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Test successful login."""
        response = await client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "Test@123456"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        """Test login with wrong password."""
        response = await client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == 401
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        response = await client.post("/api/v1/auth/login", json={
            "username": "nonexistent",
            "password": "Test@123456"
        })
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_disabled_user(self, client: AsyncClient, disabled_user: User):
        """Test login with disabled user."""
        response = await client.post("/api/v1/auth/login", json={
            "username": "disabled",
            "password": "Test@123456"
        })
        
        # Should fail because user is disabled
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_login_missing_username(self, client: AsyncClient):
        """Test login without username."""
        response = await client.post("/api/v1/auth/login", json={
            "password": "Test@123456"
        })
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_login_missing_password(self, client: AsyncClient):
        """Test login without password."""
        response = await client.post("/api/v1/auth/login", json={
            "username": "testuser"
        })
        
        assert response.status_code == 422  # Validation error


class TestTokenRefresh:
    """Test token refresh functionality."""
    
    @pytest.mark.asyncio
    async def test_token_refresh_success(self, client: AsyncClient, test_user: User):
        """Test successful token refresh."""
        # Login first
        login_response = await client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "Test@123456"
        })
        refresh_token = login_response.json()["data"]["refresh_token"]
        
        # Refresh token
        response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]
    
    @pytest.mark.asyncio
    async def test_token_refresh_invalid(self, client: AsyncClient):
        """Test token refresh with invalid token."""
        response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid_token"
        })
        
        assert response.status_code == 401


class TestLogout:
    """Test logout functionality."""
    
    @pytest.mark.asyncio
    async def test_logout_success(self, client: AsyncClient, user_token: str):
        """Test successful logout."""
        response = await client.post("/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_logout_without_token(self, client: AsyncClient):
        """Test logout without token."""
        response = await client.post("/api/v1/auth/logout")
        
        assert response.status_code == 401


class TestGetCurrentUser:
    """Test get current user functionality."""
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, client: AsyncClient, user_token: str):
        """Test get current user with valid token."""
        response = await client.get("/api/v1/auth/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["username"] == "testuser"
    
    @pytest.mark.asyncio
    async def test_get_current_user_without_token(self, client: AsyncClient):
        """Test get current user without token."""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test get current user with invalid token."""
        response = await client.get("/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
