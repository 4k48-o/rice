"""
Snowflake ID Generator.

Twitter's Snowflake algorithm for generating distributed unique IDs.
64-bit structure:
- 1 bit: unused (always 0)
- 41 bits: timestamp in milliseconds (since custom epoch)
- 10 bits: machine ID (5 bits datacenter + 5 bits worker)
- 12 bits: sequence number (0-4095)
"""
import time
import threading
from typing import Optional


class SnowflakeIDGenerator:
    """Thread-safe Snowflake ID generator."""
    
    # Bit lengths
    TIMESTAMP_BITS = 41
    DATACENTER_BITS = 5
    WORKER_BITS = 5
    SEQUENCE_BITS = 12
    
    # Max values
    MAX_DATACENTER_ID = (1 << DATACENTER_BITS) - 1  # 31
    MAX_WORKER_ID = (1 << WORKER_BITS) - 1  # 31
    MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1  # 4095
    
    # Bit shifts
    TIMESTAMP_SHIFT = DATACENTER_BITS + WORKER_BITS + SEQUENCE_BITS  # 22
    DATACENTER_SHIFT = WORKER_BITS + SEQUENCE_BITS  # 17
    WORKER_SHIFT = SEQUENCE_BITS  # 12
    
    def __init__(
        self,
        datacenter_id: int = 0,
        worker_id: int = 0,
        epoch: int = 1609459200000  # 2021-01-01 00:00:00 UTC in milliseconds
    ):
        """
        Initialize Snowflake ID generator.
        
        Args:
            datacenter_id: Datacenter ID (0-31)
            worker_id: Worker ID (0-31)
            epoch: Custom epoch timestamp in milliseconds
            
        Raises:
            ValueError: If datacenter_id or worker_id is out of range
        """
        if datacenter_id < 0 or datacenter_id > self.MAX_DATACENTER_ID:
            raise ValueError(
                f"Datacenter ID must be between 0 and {self.MAX_DATACENTER_ID}"
            )
        if worker_id < 0 or worker_id > self.MAX_WORKER_ID:
            raise ValueError(
                f"Worker ID must be between 0 and {self.MAX_WORKER_ID}"
            )
        
        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.epoch = epoch
        
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()
    
    def _current_millis(self) -> int:
        """Get current timestamp in milliseconds."""
        return int(time.time() * 1000)
    
    def _wait_next_millis(self, last_timestamp: int) -> int:
        """
        Wait until next millisecond.
        
        Args:
            last_timestamp: Last timestamp in milliseconds
            
        Returns:
            Current timestamp in milliseconds
        """
        timestamp = self._current_millis()
        while timestamp <= last_timestamp:
            timestamp = self._current_millis()
        return timestamp
    
    def generate_id(self) -> int:
        """
        Generate a unique Snowflake ID.
        
        Returns:
            64-bit unique ID
            
        Raises:
            RuntimeError: If clock moves backwards
        """
        with self.lock:
            timestamp = self._current_millis()
            
            # Clock moved backwards
            if timestamp < self.last_timestamp:
                offset = self.last_timestamp - timestamp
                if offset <= 5:
                    # Wait if offset is small (< 5ms)
                    time.sleep(offset / 1000.0)
                    timestamp = self._current_millis()
                    if timestamp < self.last_timestamp:
                        raise RuntimeError(
                            f"Clock moved backwards. Refusing to generate ID for "
                            f"{self.last_timestamp - timestamp}ms"
                        )
                else:
                    raise RuntimeError(
                        f"Clock moved backwards. Refusing to generate ID for "
                        f"{offset}ms"
                    )
            
            # Same millisecond
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.MAX_SEQUENCE
                if self.sequence == 0:
                    # Sequence overflow, wait for next millisecond
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                # New millisecond, reset sequence
                self.sequence = 0
            
            self.last_timestamp = timestamp
            
            # Generate ID
            snowflake_id = (
                ((timestamp - self.epoch) << self.TIMESTAMP_SHIFT) |
                (self.datacenter_id << self.DATACENTER_SHIFT) |
                (self.worker_id << self.WORKER_SHIFT) |
                self.sequence
            )
            
            return snowflake_id
    
    def parse_id(self, snowflake_id: int) -> dict:
        """
        Parse a Snowflake ID into its components.
        
        Args:
            snowflake_id: Snowflake ID to parse
            
        Returns:
            Dictionary with timestamp, datacenter_id, worker_id, sequence
        """
        timestamp_offset = (snowflake_id >> self.TIMESTAMP_SHIFT) & ((1 << self.TIMESTAMP_BITS) - 1)
        timestamp = timestamp_offset + self.epoch
        
        datacenter_id = (snowflake_id >> self.DATACENTER_SHIFT) & self.MAX_DATACENTER_ID
        worker_id = (snowflake_id >> self.WORKER_SHIFT) & self.MAX_WORKER_ID
        sequence = snowflake_id & self.MAX_SEQUENCE
        
        return {
            "timestamp": timestamp,
            "datacenter_id": datacenter_id,
            "worker_id": worker_id,
            "sequence": sequence
        }


# Global instance (will be initialized from settings)
_snowflake_generator: Optional[SnowflakeIDGenerator] = None


def init_snowflake(datacenter_id: int, worker_id: int, epoch: int) -> None:
    """
    Initialize global Snowflake ID generator.
    
    Args:
        datacenter_id: Datacenter ID (0-31)
        worker_id: Worker ID (0-31)
        epoch: Custom epoch timestamp in milliseconds
    """
    global _snowflake_generator
    _snowflake_generator = SnowflakeIDGenerator(datacenter_id, worker_id, epoch)


def generate_id() -> int:
    """
    Generate a Snowflake ID using the global generator.
    
    Returns:
        64-bit unique ID
        
    Raises:
        RuntimeError: If generator is not initialized
    """
    if _snowflake_generator is None:
        raise RuntimeError(
            "Snowflake generator not initialized. Call init_snowflake() first."
        )
    return _snowflake_generator.generate_id()


def parse_id(snowflake_id: int) -> dict:
    """
    Parse a Snowflake ID using the global generator.
    
    Args:
        snowflake_id: Snowflake ID to parse
        
    Returns:
        Dictionary with timestamp, datacenter_id, worker_id, sequence
        
    Raises:
        RuntimeError: If generator is not initialized
    """
    if _snowflake_generator is None:
        raise RuntimeError(
            "Snowflake generator not initialized. Call init_snowflake() first."
        )
    return _snowflake_generator.parse_id(snowflake_id)
