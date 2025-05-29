"""
Prototype of single-array node structure for performance testing.
This demonstrates the proposed memory layout before C implementation.
"""

import bisect
from typing import Optional, Union, List, Tuple


class SingleArrayLeafNode:
    """Leaf node with keys and values in a single array for better cache locality."""
    
    def __init__(self, capacity: int = 128):
        self.capacity = capacity
        self.num_keys = 0
        # Single array: first half keys, second half values
        self.data = [None] * (capacity * 2)
        self.next: Optional['SingleArrayLeafNode'] = None
    
    @property
    def keys(self):
        """View of keys (first half of array)."""
        return self.data[:self.capacity]
    
    @property
    def values(self):
        """View of values (second half of array)."""
        return self.data[self.capacity:]
    
    def get_key(self, index: int):
        """Direct array access for C optimization."""
        return self.data[index]
    
    def get_value(self, index: int):
        """Direct array access for C optimization."""
        return self.data[self.capacity + index]
    
    def set_key(self, index: int, key):
        """Direct array access for C optimization."""
        self.data[index] = key
    
    def set_value(self, index: int, value):
        """Direct array access for C optimization."""
        self.data[self.capacity + index] = value
    
    def find_position(self, key) -> int:
        """Binary search optimized for single array access."""
        left, right = 0, self.num_keys
        while left < right:
            mid = (left + right) // 2
            if self.data[mid] < key:
                left = mid + 1
            else:
                right = mid
        return left
    
    def insert(self, key, value) -> Optional[Tuple]:
        """Insert with single array manipulation."""
        pos = self.find_position(key)
        
        # Check if key exists
        if pos < self.num_keys and self.data[pos] == key:
            self.data[self.capacity + pos] = value
            return None
        
        # Check if split needed
        if self.num_keys >= self.capacity:
            return self._split_and_insert(pos, key, value)
        
        # Shift elements in both halves
        for i in range(self.num_keys, pos, -1):
            self.data[i] = self.data[i - 1]
            self.data[self.capacity + i] = self.data[self.capacity + i - 1]
        
        # Insert
        self.data[pos] = key
        self.data[self.capacity + pos] = value
        self.num_keys += 1
        return None
    
    def _split_and_insert(self, pos: int, key, value) -> Tuple:
        """Split node and insert, returning (split_key, new_node)."""
        new_node = SingleArrayLeafNode(self.capacity)
        mid = self.capacity // 2
        
        # Create temporary array with new element
        temp_keys = []
        temp_values = []
        
        for i in range(pos):
            temp_keys.append(self.data[i])
            temp_values.append(self.data[self.capacity + i])
        
        temp_keys.append(key)
        temp_values.append(value)
        
        for i in range(pos, self.num_keys):
            temp_keys.append(self.data[i])
            temp_values.append(self.data[self.capacity + i])
        
        # Distribute to nodes
        self.num_keys = mid
        for i in range(mid):
            self.data[i] = temp_keys[i]
            self.data[self.capacity + i] = temp_values[i]
        
        new_node.num_keys = len(temp_keys) - mid
        for i in range(new_node.num_keys):
            new_node.data[i] = temp_keys[mid + i]
            new_node.data[new_node.capacity + i] = temp_values[mid + i]
        
        # Update next pointers
        new_node.next = self.next
        self.next = new_node
        
        return (new_node.data[0], new_node)


class SingleArrayBranchNode:
    """Branch node with keys and child pointers in a single array."""
    
    def __init__(self, capacity: int = 128):
        self.capacity = capacity
        self.num_keys = 0
        # Single array: first half keys, second half children
        # Note: children array has capacity+1 to handle edge case
        self.data = [None] * (capacity * 2 + 1)
    
    def get_key(self, index: int):
        """Direct array access for C optimization."""
        return self.data[index]
    
    def get_child(self, index: int):
        """Direct array access for C optimization."""
        return self.data[self.capacity + index]
    
    def set_key(self, index: int, key):
        """Direct array access for C optimization."""
        self.data[index] = key
    
    def set_child(self, index: int, child):
        """Direct array access for C optimization."""
        self.data[self.capacity + index] = child
    
    def find_child_index(self, key) -> int:
        """Binary search optimized for single array access."""
        left, right = 0, self.num_keys
        while left < right:
            mid = (left + right) // 2
            if self.data[mid] < key:
                left = mid + 1
            else:
                right = mid
        return left


def benchmark_single_array():
    """Quick benchmark to test the concept."""
    import time
    import random
    
    # Test leaf node operations
    node = SingleArrayLeafNode(128)
    keys = list(range(100))
    random.shuffle(keys)
    
    start = time.perf_counter()
    for key in keys:
        node.insert(key, key * 2)
    insert_time = time.perf_counter() - start
    
    start = time.perf_counter()
    for _ in range(1000):
        for key in keys[:node.num_keys]:
            pos = node.find_position(key)
            value = node.get_value(pos)
    lookup_time = time.perf_counter() - start
    
    print(f"Single Array Performance:")
    print(f"  Insert time: {insert_time:.6f}s")
    print(f"  Lookup time: {lookup_time:.6f}s")
    print(f"  Lookups/sec: {(1000 * node.num_keys) / lookup_time:,.0f}")


if __name__ == "__main__":
    benchmark_single_array()