"""
IP utility functions.
"""
from fastapi import Request


class IPUtils:
    """IP utilities."""
    
    @staticmethod
    def get_ip(request: Request) -> str:
        """
        Get client IP address.
        
        Args:
            request: FastAPI Request
            
        Returns:
            IP address
        """
        if not request:
            return "127.0.0.1"
            
        # Check X-Forwarded-For
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
            
        # Check X-Real-IP
        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip
            
        if request.client:
            return request.client.host
            
        return "127.0.0.1"
    
    @staticmethod
    def get_location(ip: str) -> str:
        """
        Get IP location.
        TODO: Integrate ip2region or other offline library.
        
        Args:
            ip: IP address
            
        Returns:
            Location string
        """
        if ip in ["127.0.0.1", "localhost", "::1"]:
            return "内网IP"
        return "未知位置"
