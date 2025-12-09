"""
检查所有表是否缺少 BaseModel 定义的字段。

BaseModel 包含的字段：
- id: String(50) - 主键
- remark: String(500) - 备注（可选）
- created_at: DateTime - 创建时间
- updated_at: DateTime - 更新时间
- created_by: String(50) - 创建人ID（可选）
- updated_by: String(50) - 更新人ID（可选）
- is_deleted: Boolean - 是否删除
- deleted_at: DateTime - 删除时间（可选）
- deleted_by: String(50) - 删除人ID（可选）

TenantMixin 包含的字段：
- tenant_id: String(50) - 租户ID

继承 BaseModel 的表：
- users (继承 TenantMixin)
- departments (继承 TenantMixin)
- roles (继承 TenantMixin)
- permissions (继承 TenantMixin)
- menus (继承 TenantMixin)
- tenants (不继承 TenantMixin)
- sys_login_log (继承 TenantMixin)
- sys_opt_log (继承 TenantMixin)
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text
from app.core.database import AsyncSessionLocal


async def check_table_fields():
    """检查所有表是否缺少必要的字段。"""
    
    # 定义所有需要检查的表及其应该包含的字段
    tables_to_check = {
        'users': {
            'base_fields': ['id', 'remark', 'created_at', 'updated_at', 'created_by', 'updated_by', 
                           'is_deleted', 'deleted_at', 'deleted_by'],
            'tenant_fields': ['tenant_id'],
            'inherits_tenant': True
        },
        'departments': {
            'base_fields': ['id', 'remark', 'created_at', 'updated_at', 'created_by', 'updated_by',
                           'is_deleted', 'deleted_at', 'deleted_by'],
            'tenant_fields': ['tenant_id'],
            'inherits_tenant': True
        },
        'roles': {
            'base_fields': ['id', 'remark', 'created_at', 'updated_at', 'created_by', 'updated_by',
                           'is_deleted', 'deleted_at', 'deleted_by'],
            'tenant_fields': ['tenant_id'],
            'inherits_tenant': True
        },
        'permissions': {
            'base_fields': ['id', 'remark', 'created_at', 'updated_at', 'created_by', 'updated_by',
                           'is_deleted', 'deleted_at', 'deleted_by'],
            'tenant_fields': ['tenant_id'],
            'inherits_tenant': True
        },
        'menus': {
            'base_fields': ['id', 'remark', 'created_at', 'updated_at', 'created_by', 'updated_by',
                           'is_deleted', 'deleted_at', 'deleted_by'],
            'tenant_fields': ['tenant_id'],
            'inherits_tenant': True
        },
        'tenants': {
            'base_fields': ['id', 'remark', 'created_at', 'updated_at', 'created_by', 'updated_by',
                           'is_deleted', 'deleted_at', 'deleted_by'],
            'tenant_fields': [],
            'inherits_tenant': False
        },
        'sys_login_log': {
            'base_fields': ['id', 'remark', 'created_at', 'updated_at', 'created_by', 'updated_by',
                           'is_deleted', 'deleted_at', 'deleted_by'],
            'tenant_fields': ['tenant_id'],
            'inherits_tenant': True
        },
        'sys_opt_log': {
            'base_fields': ['id', 'remark', 'created_at', 'updated_at', 'created_by', 'updated_by',
                           'is_deleted', 'deleted_at', 'deleted_by'],
            'tenant_fields': ['tenant_id'],
            'inherits_tenant': True
        },
    }
    
    async with AsyncSessionLocal() as db:
        # 获取数据库连接
        connection = await db.connection()
        inspector = inspect(connection.sync_engine)
        
        issues = []
        
        for table_name, expected_fields in tables_to_check.items():
            # 检查表是否存在
            if table_name not in inspector.get_table_names():
                issues.append(f"❌ 表 {table_name} 不存在")
                continue
            
            # 获取表的列
            columns = {col['name']: col for col in inspector.get_columns(table_name)}
            column_names = set(columns.keys())
            
            # 检查 BaseModel 字段
            missing_base_fields = []
            for field in expected_fields['base_fields']:
                if field not in column_names:
                    missing_base_fields.append(field)
            
            # 检查 TenantMixin 字段
            missing_tenant_fields = []
            if expected_fields['inherits_tenant']:
                for field in expected_fields['tenant_fields']:
                    if field not in column_names:
                        missing_tenant_fields.append(field)
            
            # 报告问题
            if missing_base_fields or missing_tenant_fields:
                issue_msg = f"❌ 表 {table_name} 缺少字段:"
                if missing_base_fields:
                    issue_msg += f"\n   - BaseModel 字段: {', '.join(missing_base_fields)}"
                if missing_tenant_fields:
                    issue_msg += f"\n   - TenantMixin 字段: {', '.join(missing_tenant_fields)}"
                issues.append(issue_msg)
            else:
                print(f"✅ 表 {table_name} 字段完整")
        
        # 输出结果
        if issues:
            print("\n" + "="*60)
            print("发现以下问题：")
            print("="*60)
            for issue in issues:
                print(issue)
            print("="*60)
            return False
        else:
            print("\n" + "="*60)
            print("✅ 所有表的字段都完整！")
            print("="*60)
            return True


if __name__ == "__main__":
    print("🔍 检查所有表的字段完整性...")
    result = asyncio.run(check_table_fields())
    sys.exit(0 if result else 1)

