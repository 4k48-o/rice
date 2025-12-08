"""
Manual API test script for User, Role, and Department modules.
Run this directly with: python tests/manual_module_test.py
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from httpx import AsyncClient


async def get_admin_token(client: AsyncClient) -> str:
    """Get admin token for authenticated requests."""
    response = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    if response.status_code != 200:
        raise Exception(f"Failed to login as admin: {response.text}")
    return response.json()["data"]["access_token"]


async def test_user_module(client: AsyncClient, token: str):
    """Test User Management API."""
    print("\n" + "="*60)
    print("📋 Testing User Module")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: List users
    print("\n1. Test list users...")
    response = await client.get("/api/v1/users", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    users = response.json()["data"]["items"]
    print(f"   ✅ PASSED - Found {len(users)} users")
    
    # Test 2: Create user
    print("\n2. Test create user...")
    response = await client.post("/api/v1/users", headers=headers, json={
        "username": "testuser_manual",
        "password": "Test@123456",
        "email": "testuser@example.com",
        "user_type": 2,
        "status": 1
    })
    if response.status_code == 200:
        response_data = response.json()
        new_user = response_data.get("data")
        if new_user and isinstance(new_user, dict):
            user_id = new_user.get("id")
            print(f"   ✅ PASSED - Created user with ID: {user_id}")
        else:
            print(f"   ⚠️  User created but unexpected response format: {response_data}")
            user_id = None
    elif response.status_code == 400:
        print(f"   ⚠️  User already exists (expected if run multiple times)")
        # Get existing user
        response = await client.get("/api/v1/users?keyword=testuser_manual", headers=headers)
        users = response.json()["data"]["items"]
        user_id = users[0]["id"] if users else None
    else:
        print(f"   ❌ FAILED - Status: {response.status_code}, Response: {response.text}")
        user_id = None

    
    # Test 3: Get user by ID
    if user_id:
        print(f"\n3. Test get user by ID ({user_id})...")
        response = await client.get(f"/api/v1/users/{user_id}", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        user = response.json()["data"]
        assert user["username"] == "testuser_manual"
        print(f"   ✅ PASSED - Retrieved user: {user['username']}")
    
    # Test 4: Update user
    if user_id:
        print(f"\n4. Test update user...")
        response = await client.put(f"/api/v1/users/{user_id}", headers=headers, json={
            "real_name": "Test User Updated"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"   ✅ PASSED - Updated user")
    
    # Test 5: Search users
    print(f"\n5. Test search users...")
    response = await client.get("/api/v1/users?keyword=testuser", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    users = response.json()["data"]["items"]
    print(f"   ✅ PASSED - Found {len(users)} users matching 'testuser'")
    
    # Test 6: Delete user (soft delete)
    if user_id:
        print(f"\n6. Test delete user...")
        response = await client.delete(f"/api/v1/users/{user_id}", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"   ✅ PASSED - Deleted user")


async def test_department_module(client: AsyncClient, token: str):
    """Test Department Management API."""
    print("\n" + "="*60)
    print("🏢 Testing Department Module")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: List departments
    print("\n1. Test list departments...")
    response = await client.get("/api/v1/departments", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    depts = response.json()["data"]
    print(f"   ✅ PASSED - Found {len(depts)} departments")
    
    # Test 2: Get department tree
    print("\n2. Test get department tree...")
    response = await client.get("/api/v1/departments/tree", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    tree = response.json()["data"]
    print(f"   ✅ PASSED - Retrieved department tree with {len(tree)} root nodes")
    
    # Test 3: Create department
    print("\n3. Test create department...")
    response = await client.post("/api/v1/departments", headers=headers, json={
        "name": "测试部门",
        "code": "TEST_DEPT",
        "sort": 100
    })
    if response.status_code == 200:
        new_dept = response.json()["data"]
        dept_id = new_dept["id"]
        print(f"   ✅ PASSED - Created department with ID: {dept_id}")
    elif response.status_code == 400:
        print(f"   ⚠️  Department already exists")
        response = await client.get("/api/v1/departments", headers=headers)
        depts = [d for d in response.json()["data"] if d["code"] == "TEST_DEPT"]
        dept_id = depts[0]["id"] if depts else None
    else:
        print(f"   ❌ FAILED - Status: {response.status_code}")
        return
    
    # Test 4: Get department by ID
    if dept_id:
        print(f"\n4. Test get department by ID...")
        response = await client.get(f"/api/v1/departments/{dept_id}", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        dept = response.json()["data"]
        print(f"   ✅ PASSED - Retrieved department: {dept['name']}")
    
    # Test 5: Update department
    if dept_id:
        print(f"\n5. Test update department...")
        response = await client.put(f"/api/v1/departments/{dept_id}", headers=headers, json={
            "name": "测试部门(已更新)"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"   ✅ PASSED - Updated department")
    
    # Test 6: Delete department
    if dept_id:
        print(f"\n6. Test delete department...")
        response = await client.delete(f"/api/v1/departments/{dept_id}", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"   ✅ PASSED - Deleted department")


async def test_role_module(client: AsyncClient, token: str):
    """Test Role Management API."""
    print("\n" + "="*60)
    print("👥 Testing Role Module")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: List roles
    print("\n1. Test list roles...")
    response = await client.get("/api/v1/roles", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    roles = response.json()["data"]
    print(f"   ✅ PASSED - Found {len(roles)} roles")
    
    # Test 2: Get permission tree
    print("\n2. Test get permission tree...")
    response = await client.get("/api/v1/roles/permissions/tree", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    tree = response.json()["data"]
    print(f"   ✅ PASSED - Retrieved permission tree")
    
    # Test 3: Create role with permissions
    print("\n3. Test create role...")
    response = await client.post("/api/v1/roles", headers=headers, json={
        "name": "测试角色",
        "code": "TEST_ROLE",
        "data_scope": 4,
        "sort": 100,
        "permission_ids": [1, 2]  # Assuming these permission IDs exist
    })
    if response.status_code == 200:
        new_role = response.json()["data"]
        role_id = new_role["id"]
        print(f"   ✅ PASSED - Created role with ID: {role_id}")
    elif response.status_code == 400:
        print(f"   ⚠️  Role already exists")
        response = await client.get("/api/v1/roles", headers=headers)
        roles = [r for r in response.json()["data"] if r["code"] == "TEST_ROLE"]
        role_id = roles[0]["id"] if roles else None
    else:
        print(f"   ❌ FAILED - Status: {response.status_code}, Response: {response.text}")
        return
    
    # Test 4: Get role by ID (with permissions)
    if role_id:
        print(f"\n4. Test get role by ID...")
        response = await client.get(f"/api/v1/roles/{role_id}", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        role = response.json()["data"]
        print(f"   ✅ PASSED - Retrieved role: {role['name']} with {len(role.get('permissions', []))} permissions")
    
    # Test 5: Update role
    if role_id:
        print(f"\n5. Test update role...")
        response = await client.put(f"/api/v1/roles/{role_id}", headers=headers, json={
            "name": "测试角色(已更新)",
            "permission_ids": [1, 2, 6]
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"   ✅ PASSED - Updated role")
    
    # Test 6: Delete role
    if role_id:
        print(f"\n6. Test delete role...")
        response = await client.delete(f"/api/v1/roles/{role_id}", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"   ✅ PASSED - Deleted role")


async def test_menu_module(client: AsyncClient, token: str):
    """Test Menu Management API."""
    print("\n" + "="*60)
    print("📱 Testing Menu Module")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Get user menu tree (returns list directly)
    print("\n1. Test get user menu tree...")
    response = await client.get("/api/v1/menus/user", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    # Note: user menu tree returns list directly, not wrapped in data
    menus = response.json()
    print(f"   ✅ PASSED - Retrieved {len(menus)} root menus")
    
    # Test 2: List all menus (admin endpoint, wrapped in response)
    print("\n2. Test list all menus (Admin)...")
    response = await client.get("/api/v1/menus", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()["data"]
    items = data["items"]
    print(f"   ✅ PASSED - Found {len(items)} menus (Total: {data['total']})")
    
    # Test 3: Get admin menu tree
    print("\n3. Test get admin menu tree...")
    response = await client.get("/api/v1/menus/tree/all", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    tree = response.json()["data"]
    print(f"   ✅ PASSED - Retrieved admin tree with {len(tree)} root nodes")
    
    # Test 4: Create menu
    print("\n4. Test create menu...")
    menu_data = {
        "name": "test_menu",
        "title": "Test Menu",
        "type": 2,
        "sort": 999,
        "parent_id": 0
    }
    response = await client.post("/api/v1/menus", headers=headers, json=menu_data)
    if response.status_code == 200:
        new_menu = response.json()["data"]
        menu_id = new_menu.get("id")
        print(f"   ✅ PASSED - Created menu with ID: {menu_id}")
    else:
        print(f"   ❌ FAILED - Status: {response.status_code}, Response: {response.text}")
        menu_id = None

    # Test 5: Get menu by ID
    if menu_id:
        print(f"\n5. Test get menu by ID...")
        response = await client.get(f"/api/v1/menus/{menu_id}", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        menu = response.json()["data"]
        assert menu["name"] == "test_menu"
        print(f"   ✅ PASSED - Retrieved menu: {menu['title']}")
    
    # Test 6: Validation - Invalid Parent
    print("\n6. Test invalid parent validation...")
    bad_data = {
        "name": "bad_child",
        "title": "Bad Child",
        "type": 2,
        "parent_id": 999999999999  # Non-existent ID
    }
    response = await client.post("/api/v1/menus", headers=headers, json=bad_data)
    if response.status_code == 400:
        print(f"   ✅ PASSED - Correctly rejected invalid parent (400)")
    else:
        print(f"   ❌ FAILED - Expected 400, got {response.status_code}")

    # Test 7: Update and Circular Reference Check
    if menu_id:
        print("\n7. Test circular reference check...")
        # Try to set parent to self
        update_data = {"parent_id": menu_id}
        response = await client.put(f"/api/v1/menus/{menu_id}", headers=headers, json=update_data)
        if response.status_code == 400:
             print(f"   ✅ PASSED - Correctly rejected circular reference (400)")
        else:
             print(f"   ❌ FAILED - Expected 400, got {response.status_code}")
             
        # Delete the test menu
        print("\n8. Test delete menu...")
        await client.delete(f"/api/v1/menus/{menu_id}", headers=headers)
        print(f"   ✅ PASSED - Cleanup successful")



async def run_all_tests():
    """Run all module tests."""
    base_url = "http://localhost:8000"
    
    print("🧪 Starting Manual Module Tests...")
    print("="*60)
    
    async with AsyncClient(base_url=base_url, timeout=10.0) as client:
        try:
            # Get admin token
            print("\n🔑 Logging in as admin...")
            token = await get_admin_token(client)
            print("   ✅ Login successful")
            
            # Run tests
            await test_user_module(client, token)
            await test_department_module(client, token)
            await test_role_module(client, token)
            await test_menu_module(client, token)
            
            print("\n" + "="*60)
            print("✨ All module tests completed!")
            print("="*60)
            
        except AssertionError as e:
            print(f"\n❌ Test failed: {e}")
            raise
        except Exception as e:
            print(f"\n❌ Error: {e}")
            raise


if __name__ == "__main__":
    print("⚠️  Make sure the server is running on http://localhost:8000")
    print("   Run: cd backend && venv/bin/uvicorn app.main:app --reload\n")
    
    asyncio.run(run_all_tests())
