"""
Test Snowflake ID Generator.
"""
import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from app.utils.snowflake import SnowflakeIDGenerator, init_snowflake, generate_id, parse_id


class TestSnowflakeIDGenerator:
    """Test Snowflake ID generator."""
    
    def test_initialization(self):
        """Test generator initialization."""
        generator = SnowflakeIDGenerator(datacenter_id=1, worker_id=2)
        assert generator.datacenter_id == 1
        assert generator.worker_id == 2
    
    def test_invalid_datacenter_id(self):
        """Test invalid datacenter ID."""
        with pytest.raises(ValueError):
            SnowflakeIDGenerator(datacenter_id=32)
    
    def test_invalid_worker_id(self):
        """Test invalid worker ID."""
        with pytest.raises(ValueError):
            SnowflakeIDGenerator(worker_id=32)
    
    def test_id_generation(self):
        """Test basic ID generation."""
        generator = SnowflakeIDGenerator()
        id1 = generator.generate_id()
        id2 = generator.generate_id()
        
        assert isinstance(id1, int)
        assert isinstance(id2, int)
        assert id1 != id2
        assert id2 > id1  # IDs should be monotonically increasing
    
    def test_id_uniqueness(self):
        """Test ID uniqueness with 10,000 IDs."""
        generator = SnowflakeIDGenerator()
        ids = set()
        
        for _ in range(10000):
            new_id = generator.generate_id()
            assert new_id not in ids, "Duplicate ID generated!"
            ids.add(new_id)
        
        assert len(ids) == 10000
    
    def test_concurrent_generation(self):
        """Test concurrent ID generation."""
        generator = SnowflakeIDGenerator()
        ids = set()
        
        def generate_batch():
            batch_ids = []
            for _ in range(1000):
                batch_ids.append(generator.generate_id())
            return batch_ids
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(generate_batch) for _ in range(10)]
            for future in futures:
                batch = future.result()
                for id_val in batch:
                    assert id_val not in ids, "Duplicate ID in concurrent generation!"
                    ids.add(id_val)
        
        assert len(ids) == 10000
    
    def test_parse_id(self):
        """Test parsing Snowflake ID."""
        generator = SnowflakeIDGenerator(datacenter_id=5, worker_id=10)
        snowflake_id = generator.generate_id()
        
        parsed = generator.parse_id(snowflake_id)
        
        assert parsed["datacenter_id"] == 5
        assert parsed["worker_id"] == 10
        assert parsed["sequence"] >= 0
        assert parsed["timestamp"] > generator.epoch
    
    def test_global_functions(self):
        """Test global init and generate functions."""
        init_snowflake(datacenter_id=3, worker_id=7, epoch=1609459200000)
        
        id1 = generate_id()
        id2 = generate_id()
        
        assert id1 != id2
        assert id2 > id1
        
        parsed = parse_id(id1)
        assert parsed["datacenter_id"] == 3
        assert parsed["worker_id"] == 7
    
    def test_sequence_overflow(self):
        """Test sequence overflow handling."""
        generator = SnowflakeIDGenerator()
        
        # Force sequence to max
        generator.sequence = 4095
        generator.last_timestamp = generator._current_millis()
        
        # Next ID should wait for next millisecond and reset sequence
        id1 = generator.generate_id()
        assert generator.sequence == 0
    
    def test_id_format(self):
        """Test ID format (should be 19 digits for typical use)."""
        generator = SnowflakeIDGenerator()
        snowflake_id = generator.generate_id()
        
        # Snowflake IDs are typically 18-19 digits
        assert len(str(snowflake_id)) >= 18
        assert len(str(snowflake_id)) <= 19


def test_performance_benchmark():
    """Benchmark ID generation performance."""
    generator = SnowflakeIDGenerator()
    
    start = time.time()
    for _ in range(100000):
        generator.generate_id()
    elapsed = time.time() - start
    
    rate = 100000 / elapsed
    print(f"\nGeneration rate: {rate:.0f} IDs/second")
    
    # Should be able to generate at least 100k IDs per second
    assert rate > 100000
