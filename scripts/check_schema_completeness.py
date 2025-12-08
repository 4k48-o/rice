#!/usr/bin/env python3
"""
检查 Schema 完整性脚本

检查项：
1. BaseModel 的所有字段是否在 Schema 中定义
2. Update Schema 是否包含所有 Base 字段（Optional）
3. 前后端字段命名一致性

使用方法：
    python scripts/check_schema_completeness.py
"""
import sys
import os
import inspect
from pathlib import Path
from typing import Set, Dict, List, Tuple
import importlib.util

# 设置环境变量以避免数据库连接初始化
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/test")
os.environ.setdefault("SECRET_KEY", "check-schema-tool-only")

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "backend"))


def get_model_fields(model_class) -> Set[str]:
    """获取数据库模型的所有字段名"""
    if hasattr(model_class, "__table__"):
        return set(model_class.__table__.columns.keys())
    return set()


def get_schema_fields(schema_class) -> Set[str]:
    """获取 Pydantic Schema 的所有字段名"""
    if hasattr(schema_class, "model_fields"):
        return set(schema_class.model_fields.keys())
    elif hasattr(schema_class, "__fields__"):
        return set(schema_class.__fields__.keys())
    return set()


def check_schema_completeness():
    """检查 Schema 完整性"""
    errors: List[str] = []
    warnings: List[str] = []

    # 动态导入模块
    try:
        # 延迟导入数据库相关模块，避免初始化数据库连接
        import warnings
        warnings.filterwarnings("ignore")
        
        # 临时禁用数据库初始化
        import app.core.database as db_module
        # 保存原始函数
        original_create_engine = None
        if hasattr(db_module, 'create_async_engine'):
            original_create_engine = db_module.create_async_engine
        
        # 尝试导入 Schema（不依赖数据库）
        from app.schemas.department import (
            DepartmentBase,
            DepartmentCreate,
            DepartmentUpdate,
            DepartmentResponse
        )
        
        # 尝试导入模型（可能需要数据库，但我们可以处理错误）
        try:
            from app.models.department import Department
            model_available = True
        except Exception as e:
            print(f"⚠️  无法导入 Department 模型: {e}")
            print("   将仅检查 Schema 字段完整性")
            model_available = False
        
        print("=" * 60)
        print("检查 Department Schema 完整性")
        print("=" * 60)
        
        # 2. 检查 Base Schema 字段
        base_schema_fields = get_schema_fields(DepartmentBase)
        print(f"\nBase Schema 字段 ({len(base_schema_fields)}):")
        for field in sorted(base_schema_fields):
            print(f"  - {field}")
        
        # 1. 检查数据库模型字段（如果可用）
        if model_available:
            model_fields = get_model_fields(Department)
            print(f"\n数据库模型字段 ({len(model_fields)}):")
            for field in sorted(model_fields):
                print(f"  - {field}")
            
            # 3. 检查缺失字段（BaseModel 字段应在 Schema 中）
            # BaseModel 标准字段（这些字段通常继承自 BaseModel，可能不需要在 Schema 中显式定义）
            base_model_only_fields = {"id", "created_at", "updated_at", "created_by", 
                                      "updated_by", "is_deleted", "deleted_at", "deleted_by"}
            
            # 业务字段应该在 Schema 中
            business_fields = model_fields - base_model_only_fields
            missing_in_base = business_fields - base_schema_fields
            
            if missing_in_base:
                errors.append(f"❌ Base Schema 缺少字段: {missing_in_base}")
            else:
                print("\n✅ Base Schema 包含所有业务字段")
        else:
            print("\n⚠️  跳过数据库模型检查（模型无法导入）")
        
        # 4. 检查 Update Schema
        update_schema_fields = get_schema_fields(DepartmentUpdate)
        print(f"\nUpdate Schema 字段 ({len(update_schema_fields)}):")
        for field in sorted(update_schema_fields):
            print(f"  - {field}")
        
        # Update Schema 应该包含所有 Base 字段（至少是可选的）
        missing_in_update = base_schema_fields - update_schema_fields
        if missing_in_update:
            warnings.append(f"⚠️  Update Schema 缺少字段（建议添加）: {missing_in_update}")
        else:
            print("\n✅ Update Schema 包含所有 Base 字段")
        
        # 5. 检查 Response Schema
        response_schema_fields = get_schema_fields(DepartmentResponse)
        print(f"\nResponse Schema 字段 ({len(response_schema_fields)}):")
        for field in sorted(response_schema_fields):
            print(f"  - {field}")
        
        # 6. 特殊字段检查
        if "remark" not in base_schema_fields:
            errors.append("❌ Base Schema 缺少 remark 字段（继承自 BaseModel）")
        if "remark" not in update_schema_fields:
            errors.append("❌ Update Schema 缺少 remark 字段")
        
        # 打印结果
        print("\n" + "=" * 60)
        print("检查结果")
        print("=" * 60)
        
        if errors:
            print("\n❌ 错误:")
            for error in errors:
                print(f"  {error}")
        
        if warnings:
            print("\n⚠️  警告:")
            for warning in warnings:
                print(f"  {warning}")
        
        if not errors and not warnings:
            print("\n✅ 所有检查通过！")
            return 0
        else:
            return 1
            
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        return 1
    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


def check_field_naming_consistency():
    """检查字段命名一致性"""
    print("\n" + "=" * 60)
    print("检查字段命名一致性")
    print("=" * 60)
    
    # 检查前端类型定义文件
    frontend_types_file = project_root / "frontend" / "src" / "types" / "department.ts"
    
    if not frontend_types_file.exists():
        print(f"⚠️  前端类型文件不存在: {frontend_types_file}")
        return
    
    content = frontend_types_file.read_text()
    
    # 检查是否有不一致的字段名
    inconsistent_fields = {
        "dept_code": "应该使用 'code'",
        "dept_name": "应该使用 'name'",
        "sort_order": "应该使用 'sort'"
    }
    
    issues = []
    for old_name, suggestion in inconsistent_fields.items():
        if old_name in content:
            issues.append(f"  - 发现 '{old_name}'，建议改为: {suggestion}")
    
    if issues:
        print("\n⚠️  发现可能的字段命名不一致:")
        for issue in issues:
            print(issue)
        print("\n建议：前端类型定义应直接使用后端 Schema 字段名")
    else:
        print("\n✅ 字段命名一致")


if __name__ == "__main__":
    print("Schema 完整性检查工具")
    print("=" * 60)
    
    result = check_schema_completeness()
    check_field_naming_consistency()
    
    print("\n" + "=" * 60)
    sys.exit(result)

