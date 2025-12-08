"""
缓存工具模块

提供部门数据的Redis缓存操作。
"""
import json
import logging
from typing import Optional, List, Dict, Any, Union
from redis.asyncio import Redis

from app.core.redis import RedisClient
from app.schemas.department import DepartmentResponse, DepartmentTreeNode

logger = logging.getLogger(__name__)


def _to_id_string(id_value: Union[int, str]) -> str:
    """
    将ID转换为字符串，确保Redis key中的ID都是字符串类型。
    这样可以避免前端使用BigInt ID时的精度问题。
    
    Args:
        id_value: ID值（int或str）
        
    Returns:
        字符串形式的ID
    """
    if id_value is None:
        return ""
    return str(id_value)


class DepartmentCache:
    """部门数据缓存工具类"""
    
    # 缓存键前缀
    CACHE_KEY_LIST = "dept:list:{tenant_id}"
    CACHE_KEY_TREE = "dept:tree:{tenant_id}"
    CACHE_KEY_DETAIL = "dept:detail:{dept_id}"
    
    @staticmethod
    def _get_redis() -> Optional[Redis]:
        """获取Redis客户端，失败时返回None"""
        try:
            return RedisClient.get_client()
        except Exception as e:
            logger.warning(f"Failed to get Redis client: {e}")
            return None
    
    @staticmethod
    async def get_departments_list(tenant_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        获取部门列表缓存
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            部门列表字典列表，缓存未命中返回None
        """
        redis = DepartmentCache._get_redis()
        if not redis:
            return None
        
        try:
            cache_key = DepartmentCache.CACHE_KEY_LIST.format(tenant_id=_to_id_string(tenant_id))
            cached_data = await redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Failed to get departments list from cache: {e}")
        
        return None
    
    @staticmethod
    async def set_departments_list(tenant_id: int, departments: List[Any]) -> bool:
        """
        设置部门列表缓存
        
        Args:
            tenant_id: 租户ID
            departments: 部门对象列表
            
        Returns:
            是否设置成功
        """
        redis = DepartmentCache._get_redis()
        if not redis:
            return False
        
        try:
            cache_key = DepartmentCache.CACHE_KEY_LIST.format(tenant_id=_to_id_string(tenant_id))
            # 将部门对象序列化为字典列表
            dept_dicts = [DepartmentResponse.model_validate(d).model_dump(mode='json') for d in departments]
            cached_data = json.dumps(dept_dicts, ensure_ascii=False)
            await redis.set(cache_key, cached_data)
            return True
        except Exception as e:
            logger.warning(f"Failed to set departments list to cache: {e}")
        
        return False
    
    @staticmethod
    async def get_departments_tree(tenant_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        获取部门树缓存
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            部门树字典列表，缓存未命中返回None
        """
        redis = DepartmentCache._get_redis()
        if not redis:
            return None
        
        try:
            cache_key = DepartmentCache.CACHE_KEY_TREE.format(tenant_id=_to_id_string(tenant_id))
            cached_data = await redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Failed to get departments tree from cache: {e}")
        
        return None
    
    @staticmethod
    async def set_departments_tree(tenant_id: int, tree: List[Any]) -> bool:
        """
        设置部门树缓存
        
        Args:
            tenant_id: 租户ID
            tree: 部门树节点列表
            
        Returns:
            是否设置成功
        """
        redis = DepartmentCache._get_redis()
        if not redis:
            return False
        
        try:
            cache_key = DepartmentCache.CACHE_KEY_TREE.format(tenant_id=_to_id_string(tenant_id))
            # 将树节点序列化为字典列表（递归处理）
            def serialize_tree_node(node):
                """递归序列化树节点"""
                if isinstance(node, dict):
                    # 已经是字典，递归处理children
                    result = node.copy()
                    if 'children' in result and result['children']:
                        result['children'] = [serialize_tree_node(child) for child in result['children']]
                    return result
                else:
                    # Pydantic模型，转换为字典
                    node_dict = node.model_dump(mode='json') if hasattr(node, 'model_dump') else dict(node)
                    if 'children' in node_dict and node_dict['children']:
                        node_dict['children'] = [serialize_tree_node(child) for child in node_dict['children']]
                    return node_dict
            
            tree_dicts = [serialize_tree_node(node) for node in tree]
            cached_data = json.dumps(tree_dicts, ensure_ascii=False)
            await redis.set(cache_key, cached_data)
            return True
        except Exception as e:
            logger.warning(f"Failed to set departments tree to cache: {e}")
        
        return False
    
    @staticmethod
    async def get_department_detail(dept_id: int) -> Optional[Dict[str, Any]]:
        """
        获取部门详情缓存
        
        Args:
            dept_id: 部门ID
            
        Returns:
            部门详情字典，缓存未命中返回None
        """
        redis = DepartmentCache._get_redis()
        if not redis:
            return None
        
        try:
            cache_key = DepartmentCache.CACHE_KEY_DETAIL.format(dept_id=_to_id_string(dept_id))
            cached_data = await redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Failed to get department detail from cache: {e}")
        
        return None
    
    @staticmethod
    async def set_department_detail(dept_id: int, department: Any) -> bool:
        """
        设置部门详情缓存
        
        Args:
            dept_id: 部门ID
            department: 部门对象
            
        Returns:
            是否设置成功
        """
        redis = DepartmentCache._get_redis()
        if not redis:
            return False
        
        try:
            cache_key = DepartmentCache.CACHE_KEY_DETAIL.format(dept_id=_to_id_string(dept_id))
            dept_dict = DepartmentResponse.model_validate(department).model_dump(mode='json')
            cached_data = json.dumps(dept_dict, ensure_ascii=False)
            await redis.set(cache_key, cached_data)
            return True
        except Exception as e:
            logger.warning(f"Failed to set department detail to cache: {e}")
        
        return False
    
    @staticmethod
    async def clear_list_cache(tenant_id: int) -> bool:
        """
        清除部门列表缓存
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            是否清除成功
        """
        redis = DepartmentCache._get_redis()
        if not redis:
            return False
        
        try:
            cache_key = DepartmentCache.CACHE_KEY_LIST.format(tenant_id=_to_id_string(tenant_id))
            await redis.delete(cache_key)
            return True
        except Exception as e:
            logger.warning(f"Failed to clear departments list cache: {e}")
        
        return False
    
    @staticmethod
    async def clear_tree_cache(tenant_id: int) -> bool:
        """
        清除部门树缓存
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            是否清除成功
        """
        redis = DepartmentCache._get_redis()
        if not redis:
            return False
        
        try:
            cache_key = DepartmentCache.CACHE_KEY_TREE.format(tenant_id=_to_id_string(tenant_id))
            await redis.delete(cache_key)
            return True
        except Exception as e:
            logger.warning(f"Failed to clear departments tree cache: {e}")
        
        return False
    
    @staticmethod
    async def clear_detail_cache(dept_id: int) -> bool:
        """
        清除部门详情缓存
        
        Args:
            dept_id: 部门ID
            
        Returns:
            是否清除成功
        """
        redis = DepartmentCache._get_redis()
        if not redis:
            return False
        
        try:
            cache_key = DepartmentCache.CACHE_KEY_DETAIL.format(dept_id=_to_id_string(dept_id))
            await redis.delete(cache_key)
            return True
        except Exception as e:
            logger.warning(f"Failed to clear department detail cache: {e}")
        
        return False
    
    @staticmethod
    async def clear_all_cache(tenant_id: int, dept_id: Optional[int] = None) -> bool:
        """
        清除租户所有部门缓存（用于更新/删除操作）
        
        Args:
            tenant_id: 租户ID
            dept_id: 可选的部门ID，如果提供则同时清除该部门的详情缓存
            
        Returns:
            是否清除成功
        """
        redis = DepartmentCache._get_redis()
        if not redis:
            return False
        
        try:
            # 清除列表和树缓存（确保ID转换为字符串）
            list_key = DepartmentCache.CACHE_KEY_LIST.format(tenant_id=_to_id_string(tenant_id))
            tree_key = DepartmentCache.CACHE_KEY_TREE.format(tenant_id=_to_id_string(tenant_id))
            keys_to_delete = [list_key, tree_key]
            
            # 如果提供了dept_id，也清除详情缓存
            if dept_id:
                detail_key = DepartmentCache.CACHE_KEY_DETAIL.format(dept_id=_to_id_string(dept_id))
                keys_to_delete.append(detail_key)
            
            # 同时清除超级管理员的缓存（tenant_id=0），因为超级管理员可以看到所有部门
            if tenant_id != "0":
                superadmin_list_key = DepartmentCache.CACHE_KEY_LIST.format(tenant_id=_to_id_string(0))
                superadmin_tree_key = DepartmentCache.CACHE_KEY_TREE.format(tenant_id=_to_id_string(0))
                keys_to_delete.extend([superadmin_list_key, superadmin_tree_key])
            
            if keys_to_delete:
                await redis.delete(*keys_to_delete)
            
            return True
        except Exception as e:
            logger.warning(f"Failed to clear all department cache: {e}")
        
        return False

