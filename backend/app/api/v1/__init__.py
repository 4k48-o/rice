"""
API v1 router.
"""
from fastapi import APIRouter

from app.api.v1 import auth, users, menus, departments, roles, logs, dict_types, dict_data

api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(menus.router)
api_router.include_router(departments.router)
api_router.include_router(roles.router)
api_router.include_router(logs.router)
api_router.include_router(dict_types.router)
api_router.include_router(dict_data.router)

from app.api.v1 import system
api_router.include_router(system.router)




