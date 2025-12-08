#!/usr/bin/env python3
"""
简化的 Schema 完整性检查脚本（不需要数据库连接）

检查项：
1. Schema 字段定义完整性
2. Update Schema 是否包含所有 Base 字段
3. 前后端字段命名一致性

使用方法：
    python3 scripts/check_schema_simple.py
"""
import sys
import ast
import re
from pathlib import Path
from typing import Set, List

project_root = Path(__file__).parent.parent


def extract_pydantic_fields(file_path: Path) -> Set[str]:
    """从 Pydantic Schema 文件中提取字段名"""
    try:
        content = file_path.read_text()
        # 使用正则表达式提取 Field 定义的字段
        # 匹配模式: field_name: Type = Field(...)
        pattern = r'(\w+):\s*(?:Optional\[)?\w+(?:\]|str|int|List)?\s*=\s*Field'
        fields = re.findall(pattern, content)
        # 也匹配没有 Field 的字段: field_name: Optional[str] = None
        pattern2 = r'(\w+):\s*(?:Optional\[)?\w+(?:\]|str|int|List)?\s*=\s*(?:None|\d+|"[^"]*")'
        fields2 = re.findall(pattern2, content)
        all_fields = set(fields + fields2)
        # 过滤掉 Python 关键字和常见方法
        excluded = {'BaseModel', 'Field', 'Optional', 'List', 'Dict', 'Union', 'Config'}
        return all_fields - excluded
    except Exception as e:
        print(f"⚠️  读取文件失败 {file_path}: {e}")
        return set()


def extract_typescript_fields(file_path: Path) -> Set[str]:
    """从 TypeScript 类型文件中提取字段名"""
    try:
        content = file_path.read_text()
        # 匹配 TypeScript 接口字段: field_name?: type;
        pattern = r'(\w+)(?:\?)?:\s*(?:number|string|boolean|\w+(?:\[\])?|Array<.*?>)?;'
        fields = re.findall(pattern, content)
        # 过滤掉 TypeScript 关键字
        excluded = {'export', 'interface', 'type', 'extends', 'readonly', 'private', 'public'}
        return set(fields) - excluded
    except Exception as e:
        print(f"⚠️  读取文件失败 {file_path}: {e}")
        return set()


def check_department_schema():
    """检查 Department Schema"""
    print("=" * 60)
    print("检查 Department Schema 完整性")
    print("=" * 60)
    
    errors: List[str] = []
    warnings: List[str] = []
    
    backend_schema_file = project_root / "backend" / "app" / "schemas" / "department.py"
    frontend_types_file = project_root / "frontend" / "src" / "types" / "department.ts"
    
    if not backend_schema_file.exists():
        print(f"❌ 后端 Schema 文件不存在: {backend_schema_file}")
        return 1
    
    content = backend_schema_file.read_text()
    
    # 检查关键字段是否存在
    required_fields = {
        "remark": "备注字段",
        "code": "部门编码",
        "name": "部门名称",
        "sort": "排序字段"
    }
    
    print("\n1. 检查 Base Schema 关键字段:")
    base_schema_fields = extract_pydantic_fields(backend_schema_file)
    
    # 检查 DepartmentBase 类中的字段
    base_content = content
    if "class DepartmentBase" in content:
        base_start = content.find("class DepartmentBase")
        base_end = content.find("\n\nclass", base_start + 1)
        if base_end == -1:
            base_end = len(content)
        base_content = content[base_start:base_end]
        base_fields = extract_pydantic_fields_from_content(base_content)
    else:
        base_fields = set()
    
    for field, desc in required_fields.items():
        if field in base_content or field in base_fields:
            print(f"  ✅ {field} ({desc})")
        else:
            errors.append(f"❌ Base Schema 缺少字段: {field} ({desc})")
    
    # 检查 DepartmentUpdate
    print("\n2. 检查 Update Schema 字段:")
    if "class DepartmentUpdate" in content:
        update_start = content.find("class DepartmentUpdate")
        update_end = content.find("\n\nclass", update_start + 1)
        if update_end == -1:
            update_end = len(content)
        update_content = content[update_start:update_end]
        update_fields = extract_pydantic_fields_from_content(update_content)
        
        if "remark" in update_content or "remark" in update_fields:
            print("  ✅ remark 字段")
        else:
            errors.append("❌ Update Schema 缺少 remark 字段")
            
        if "code" in update_content or "code" in update_fields:
            print("  ✅ code 字段")
        else:
            warnings.append("⚠️  Update Schema 缺少 code 字段")
            
        if "name" in update_content or "name" in update_fields:
            print("  ✅ name 字段")
        else:
            warnings.append("⚠️  Update Schema 缺少 name 字段")
    else:
        errors.append("❌ 找不到 DepartmentUpdate 类定义")
    
    # 检查前端类型定义
    print("\n3. 检查前端类型定义:")
    if frontend_types_file.exists():
        frontend_content = frontend_types_file.read_text()
        frontend_fields = extract_typescript_fields(frontend_types_file)
        
        # 检查是否有不一致的字段名
        inconsistent = []
        if "dept_code" in frontend_content:
            inconsistent.append("dept_code (应使用 'code')")
        if "dept_name" in frontend_content:
            inconsistent.append("dept_name (应使用 'name')")
        if "sort_order" in frontend_content:
            inconsistent.append("sort_order (应使用 'sort')")
        
        if inconsistent:
            warnings.append(f"⚠️  前端字段命名不一致: {', '.join(inconsistent)}")
            print("  ⚠️  发现不一致的字段名:")
            for field in inconsistent:
                print(f"     - {field}")
        else:
            print("  ✅ 字段命名一致")
        
        # 检查关键字段
        if "remark" in frontend_content:
            print("  ✅ remark 字段")
        else:
            warnings.append("⚠️  前端类型定义缺少 remark 字段")
    else:
        warnings.append(f"⚠️  前端类型文件不存在: {frontend_types_file}")
    
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
    elif errors:
        return 1
    else:
        return 0


def extract_pydantic_fields_from_content(content: str) -> Set[str]:
    """从内容字符串中提取 Pydantic 字段"""
    pattern = r'(\w+):\s*(?:Optional\[)?\w+(?:\]|str|int|List)?\s*=\s*Field'
    fields = re.findall(pattern, content)
    pattern2 = r'(\w+):\s*(?:Optional\[)?\w+(?:\]|str|int|List)?\s*=\s*(?:None|\d+|"[^"]*")'
    fields2 = re.findall(pattern2, content)
    excluded = {'BaseModel', 'Field', 'Optional', 'List', 'Dict', 'Union'}
    return set(fields + fields2) - excluded


if __name__ == "__main__":
    print("Schema 完整性检查工具（简化版）")
    print("=" * 60)
    print("注意：此版本不依赖数据库连接，仅检查文件内容\n")
    
    result = check_department_schema()
    
    print("\n" + "=" * 60)
    sys.exit(result)

