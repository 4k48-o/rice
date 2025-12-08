
import asyncio
import sys
import os
import httpx

# Add backend directory to path
sys.path.append(os.getcwd())

from app.main import app

# We need to temporarily add an endpoint to test exceptions
from fastapi import APIRouter
from app.core.exceptions import BusinessException, SystemException

test_router = APIRouter(prefix="/test-exceptions")

@test_router.get("/business")
async def test_business():
    raise BusinessException(code=10001, message="This is a business error", data={"info": "extra"})

@test_router.get("/system")
async def test_system():
    raise SystemException(code=50001, message="This is a system error")

@test_router.get("/validation")
async def test_validation(q: int):
    return {"q": q}

@test_router.get("/unknown")
async def test_unknown():
    return 1 / 0

app.include_router(test_router)

async def run_tests():
    # Note: raise_app_exceptions=False is needed if we use TestClient, 
    # but for AsyncClient with app, exceptions might bubble up in debug mode.
    # We'll use try-except for the unknown exception test.
    
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        print("1. Testing Business Exception...")
        resp = await client.get("/test-exceptions/business")
        print(f"Status: {resp.status_code}, Body: {resp.json()}")
        assert resp.status_code == 200 # As defined in BusinessException default
        assert resp.json()["code"] == 10001

        print("\n2. Testing System Exception...")
        resp = await client.get("/test-exceptions/system")
        print(f"Status: {resp.status_code}, Body: {resp.json()}")
        assert resp.status_code == 500
        assert resp.json()["code"] == 50001

        print("\n3. Testing Validation Exception (standard)...")
        resp = await client.get("/test-exceptions/validation?q=abc")
        print(f"Status: {resp.status_code}, Body: {resp.json()}")
        assert resp.status_code == 422
        
        print("\n4. Testing Unknown Exception...")
        try:
            resp = await client.get("/test-exceptions/unknown")
            print(f"Status: {resp.status_code}, Body: {resp.json()}")
        except ZeroDivisionError:
            print("Caught ZeroDivisionError (Expected in Debug mode with AsyncClient)")
        except Exception as e:
            print(f"Caught expected exception: {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())
