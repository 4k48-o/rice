# FastAndtAdmin API Documentation

## Overview
This document provides a summary of the available API endpoints for the FastAndtAdmin system.
For interactive documentation, please run the backend server and visit `/docs` (Swagger UI) or `/redoc`.

**Base URL**: `/api/v1`
**Version**: 1.0.0

## Authentication
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/login` | User login (returns access token) | No |
| `POST` | `/auth/refresh` | Refresh access token | No |
| `POST` | `/auth/logout` | Logout | Yes |
| `GET` | `/auth/user-info` | Get current user information | Yes |

## System Initialization
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/system/init` | Initialize system (create admin user) | No |

## User Management
| Method | Endpoint | Description | Permission |
| :--- | :--- | :--- | :--- |
| `GET` | `/users` | Get user list with pagination | `user:list` |
| `POST` | `/users` | Create new user | `user:create` |
| `PUT` | `/users/{id}` | Update user details | `user:update` |
| `DELETE` | `/users/{id}` | Delete user (soft delete) | `user:delete` |
| `POST` | `/users/{id}/reset-password` | Reset user password | `user:update` |

## Role Management
| Method | Endpoint | Description | Permission |
| :--- | :--- | :--- | :--- |
| `GET` | `/roles` | Get role list | `role:list` |
| `POST` | `/roles` | Create new role | `role:create` |
| `PUT` | `/roles/{id}` | Update role | `role:update` |
| `DELETE` | `/roles/{id}` | Delete role | `role:delete` |
| `GET` | `/roles/permissions/tree` | Get permissions tree structure | `role:list` |
| `POST` | `/roles/{id}/permissions` | Assign permissions to role | `role:update` |

## Department Management
| Method | Endpoint | Description | Permission |
| :--- | :--- | :--- | :--- |
| `GET` | `/departments` | Get department list | `dept:list` |
| `GET` | `/departments/tree` | Get department tree structure | `dept:list` |
| `POST` | `/departments` | Create new department | `dept:create` |
| `GET` | `/departments/{id}` | Get department details | `dept:query` |
| `PUT` | `/departments/{id}` | Update department | `dept:update` |
| `DELETE` | `/departments/{id}` | Delete department | `dept:delete` |

## Menu Management
| Method | Endpoint | Description | Permission |
| :--- | :--- | :--- | :--- |
| `GET` | `/menus` | Get menu list | `menu:list` |
| `GET` | `/menus/user` | Get current user's menu tree | - |
| `GET` | `/menus/tree/all` | Get complete menu tree (Admin) | `menu:list` |
| `POST` | `/menus` | Create new menu | `menu:create` |
| `GET` | `/menus/{id}` | Get menu details | `menu:query` |
| `PUT` | `/menus/{id}` | Update menu | `menu:update` |
| `DELETE` | `/menus/{id}` | Delete menu | `menu:delete` |

## Data Models (Schemas)

### Response Format
```json
{
  "code": 200,
  "message": "Success",
  "data": { ... }
}
```

### Common Errors
- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Validation Error**: Request schema validation failed
- **500 Internal Error**: Server-side exception

## Data Scope
The system implements role-based data isolation controlled by the `data_scope` field in Roles:
1. **ALL**: Access all data
2. **DEPT**: Access own department data
3. **DEPT_AND_SUB**: Access own and sub-departments data
4. **SELF**: Access only own data
5. **CUSTOM**: Access specific departments data
