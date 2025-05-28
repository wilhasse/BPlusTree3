"""
Comprehensive fuzz tester for B+ Tree implementation.

This tester performs a million random operations and compares results with
a reference implementation (OrderedDict), while tracking operations for
debugging purposes.
"""

import random
import time
from collections import OrderedDict
from typing import List, Tuple, Any, Dict
from bplus_tree import BPlusTreeMap


class BPlusTreeFuzzTester:
    """Fuzz tester for B+ Tree with operation tracking and reference comparison"""
    
    def __init__(self, capacity: int = 4, seed: int = None):
        self.capacity = capacity
        self.seed = seed or random.randint(1, 1000000)
        random.seed(self.seed)
        
        # Initialize data structures
        self.btree = BPlusTreeMap(capacity=capacity)
        self.reference = OrderedDict()
        
        # Operation tracking for debugging
        self.operations: List[Tuple[str, Any, Any]] = []
        self.operation_count = 0
        
        # Statistics
        self.stats = {
            'insert': 0,
            'delete': 0,
            'update': 0,
            'get': 0,
            'batch_delete': 0,
            'compact': 0,
            'errors': 0
        }
    
    def log_operation(self, op_type: str, key: Any = None, value: Any = None, extra: Any = None):
        """Log an operation for replay in case of errors"""
        self.operations.append((op_type, key, value, extra))
        self.operation_count += 1
        self.stats[op_type] = self.stats.get(op_type, 0) + 1
    
    def verify_consistency(self) -> bool:
        """Verify that B+ tree matches reference implementation"""
        try:
            # Check lengths match
            if len(self.btree) != len(self.reference):
                print(f"Length mismatch: btree={len(self.btree)}, reference={len(self.reference)}")
                return False
            
            # Check all keys in reference exist in btree with same values
            for key, expected_value in self.reference.items():
                try:
                    actual_value = self.btree[key]
                    if actual_value != expected_value:
                        print(f"Value mismatch for key {key}: btree={actual_value}, reference={expected_value}")
                        return False
                except KeyError:
                    print(f"Key {key} missing from btree but exists in reference")
                    return False
            
            # Check no extra keys in btree
            for leaf in self._get_all_btree_keys():
                if leaf not in self.reference:
                    print(f"Extra key {leaf} in btree but not in reference")
                    return False
            
            # Check B+ tree invariants
            if not self.btree.invariants():
                print("B+ tree invariants violated")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error during consistency check: {e}")
            return False
    
    def _get_all_btree_keys(self) -> List[Any]:
        """Extract all keys from B+ tree by traversing leaves"""
        keys = []
        current = self.btree.leaves
        while current is not None:
            keys.extend(current.keys)
            current = current.next
        return keys
    
    def random_key(self, existing_bias: float = 0.7) -> Any:
        """Generate a random key, biased towards existing keys for deletions/updates"""
        if self.reference and random.random() < existing_bias:
            return random.choice(list(self.reference.keys()))
        else:
            return random.randint(1, 10000)
    
    def random_value(self) -> str:
        """Generate a random value"""
        return f"value_{random.randint(1, 1000000)}"
    
    def do_insert_or_update(self):
        """Perform insert or update operation"""
        key = self.random_key(existing_bias=0.3)  # Favor new keys for inserts
        value = self.random_value()
        
        # Determine operation type before modifying
        op_type = 'update' if key in self.reference else 'insert'
        
        # Apply to both implementations
        self.btree[key] = value
        self.reference[key] = value
        
        self.log_operation(op_type, key, value)
        return True
    
    def do_delete(self):
        """Perform delete operation"""
        if not self.reference:
            return True  # Nothing to delete
        
        key = self.random_key(existing_bias=0.9)  # Heavily favor existing keys
        
        # Check if key exists before deletion
        exists_in_btree = key in self.reference  # Use reference as source of truth
        
        try:
            if exists_in_btree:
                del self.btree[key]
                del self.reference[key]
                self.log_operation('delete', key)
            else:
                # Try to delete non-existent key - should raise KeyError in both
                try:
                    del self.btree[key]
                    print(f"ERROR: btree allowed deletion of non-existent key {key}")
                    return False
                except KeyError:
                    pass  # Expected behavior
                
                self.log_operation('delete_nonexistent', key)
                
        except Exception as e:
            print(f"Error during delete operation: {e}")
            return False
        
        return True
    
    def do_get(self):
        """Perform get operation"""
        key = self.random_key(existing_bias=0.8)
        
        # Get from reference
        ref_result = self.reference.get(key, "NOT_FOUND")
        
        # Get from btree
        try:
            btree_result = self.btree[key]
            if ref_result == "NOT_FOUND":
                print(f"ERROR: btree returned {btree_result} for non-existent key {key}")
                return False
            elif btree_result != ref_result:
                print(f"ERROR: value mismatch for key {key}: btree={btree_result}, ref={ref_result}")
                return False
        except KeyError:
            if ref_result != "NOT_FOUND":
                print(f"ERROR: btree missing key {key} that exists in reference")
                return False
        
        self.log_operation('get', key)
        return True
    
    def do_batch_delete(self):
        """Perform batch delete operation"""
        if len(self.reference) < 5:
            return True  # Not enough keys for meaningful batch operation
        
        # Select random subset of existing keys
        batch_size = min(random.randint(2, 10), len(self.reference) // 2)
        keys_to_delete = random.sample(list(self.reference.keys()), batch_size)
        
        # Add some non-existent keys to test robustness
        keys_to_delete.extend([self.random_key(existing_bias=0.1) for _ in range(2)])
        
        # Remove duplicates and count expected deletions
        keys_to_delete = list(set(keys_to_delete))  # Remove duplicates
        expected_deletions = sum(1 for key in keys_to_delete if key in self.reference)
        
        # Perform batch delete on btree
        actual_deletions = self.btree.delete_batch(keys_to_delete)
        
        # Manually delete from reference
        for key in keys_to_delete:
            if key in self.reference:
                del self.reference[key]
        
        if actual_deletions != expected_deletions:
            print(f"ERROR: batch delete count mismatch: expected={expected_deletions}, actual={actual_deletions}")
            return False
        
        self.log_operation('batch_delete', keys_to_delete, expected_deletions)
        return True
    
    def do_compact(self):
        """Perform tree compaction"""
        initial_nodes = self.btree._count_total_nodes()
        self.btree.compact()
        final_nodes = self.btree._count_total_nodes()
        
        self.log_operation('compact', initial_nodes, final_nodes)
        return True
    
    def run_fuzz_test(self, num_operations: int = 1000000) -> bool:
        """Run the main fuzz test with specified number of operations"""
        print(f"Starting fuzz test with {num_operations} operations (seed={self.seed})")
        print(f"B+ tree capacity: {self.capacity}")
        
        start_time = time.time()
        
        # Define operation weights
        operations = [
            (self.do_insert_or_update, 40),  # 40% inserts/updates
            (self.do_delete, 25),            # 25% deletes
            (self.do_get, 20),               # 20% gets
            (self.do_batch_delete, 10),      # 10% batch deletes
            (self.do_compact, 5),            # 5% compactions
        ]
        
        # Create weighted operation list
        weighted_ops = []
        for op_func, weight in operations:
            weighted_ops.extend([op_func] * weight)
        
        # Perform operations
        for i in range(num_operations):
            if i % 100000 == 0 and i > 0:
                elapsed = time.time() - start_time
                print(f"Completed {i} operations in {elapsed:.1f}s (rate: {i/elapsed:.0f} ops/s)")
                print(f"  Current tree size: {len(self.btree)} keys")
                
                # Verify consistency periodically
                if not self.verify_consistency():
                    print(f"CONSISTENCY ERROR at operation {i}")
                    self._save_failure_info(i)
                    return False
            
            # Choose and execute random operation
            operation = random.choice(weighted_ops)
            try:
                if not operation():
                    print(f"OPERATION ERROR at operation {i}")
                    self._save_failure_info(i)
                    return False
            except Exception as e:
                print(f"EXCEPTION at operation {i}: {e}")
                self._save_failure_info(i)
                return False
        
        # Final consistency check
        if not self.verify_consistency():
            print("FINAL CONSISTENCY CHECK FAILED")
            self._save_failure_info(num_operations)
            return False
        
        elapsed = time.time() - start_time
        print(f"\n✅ Fuzz test PASSED!")
        print(f"Completed {num_operations} operations in {elapsed:.1f}s")
        print(f"Average rate: {num_operations/elapsed:.0f} operations/second")
        print(f"Final tree size: {len(self.btree)} keys")
        print(f"Final node count: {self.btree._count_total_nodes()} nodes")
        print("\nOperation statistics:")
        for op_type, count in self.stats.items():
            if count > 0:
                print(f"  {op_type}: {count}")
        
        return True
    
    def _save_failure_info(self, failed_at: int):
        """Save operation history for debugging when a failure occurs"""
        print(f"\n💥 FAILURE DETECTED at operation {failed_at}")
        print(f"Seed: {self.seed}")
        print(f"Capacity: {self.capacity}")
        
        # Save ALL operations to file for complete reproduction
        filename = f"fuzz_failure_{self.seed}_{failed_at}.py"
        
        with open(filename, 'w') as f:
            f.write(f'"""\nFuzz test failure reproduction\n')
            f.write(f'Seed: {self.seed}\n')
            f.write(f'Capacity: {self.capacity}\n')
            f.write(f'Failed at operation: {failed_at}\n')
            f.write(f'"""\n\n')
            f.write('from bplus_tree import BPlusTreeMap\n')
            f.write('from collections import OrderedDict\n\n')
            f.write('def reproduce_failure():\n')
            f.write(f'    tree = BPlusTreeMap(capacity={self.capacity})\n')
            f.write('    reference = OrderedDict()\n\n')
            
            for i, (op_type, key, value, extra) in enumerate(self.operations):
                f.write(f'    # Operation {i + 1}: {op_type}\n')
                
                if op_type in ['insert', 'update']:
                    f.write(f'    tree[{repr(key)}] = {repr(value)}\n')
                    f.write(f'    reference[{repr(key)}] = {repr(value)}\n')
                elif op_type == 'delete':
                    f.write(f'    del tree[{repr(key)}]\n')
                    f.write(f'    del reference[{repr(key)}]\n')
                elif op_type == 'batch_delete':
                    f.write(f'    keys_to_delete = {repr(key)}\n')
                    f.write(f'    tree.delete_batch(keys_to_delete)\n')
                    f.write(f'    for k in keys_to_delete:\n')
                    f.write(f'        if k in reference: del reference[k]\n')
                elif op_type == 'compact':
                    f.write(f'    tree.compact()\n')
                
                f.write(f'    assert tree.invariants(), "Invariants failed at step {i+1}"\n\n')
            
            f.write('    # Verify final consistency\n')
            f.write('    assert len(tree) == len(reference), "Length mismatch"\n')
            f.write('    for key, value in reference.items():\n')
            f.write('        assert tree[key] == value, f"Value mismatch for {key}"\n')
            f.write('    print("Reproduction completed successfully")\n\n')
            f.write('if __name__ == "__main__":\n')
            f.write('    reproduce_failure()\n')
        
        print(f"Failure reproduction saved to: {filename}")
        print("Run the saved file to reproduce the exact failure scenario")


def run_quick_fuzz_test():
    """Run a smaller fuzz test for development/testing"""
    tester = BPlusTreeFuzzTester(capacity=4)  # Use capacity 4 which is more stable
    return tester.run_fuzz_test(1000)  # Much smaller test


def run_full_fuzz_test():
    """Run the full million-operation fuzz test"""
    tester = BPlusTreeFuzzTester(capacity=4)
    return tester.run_fuzz_test(1000000)


def run_varied_capacity_tests():
    """Run fuzz tests with different capacities"""
    capacities = [3, 4, 5, 8, 16]
    all_passed = True
    
    for capacity in capacities:
        print(f"\n{'='*60}")
        print(f"Testing with capacity {capacity}")
        print('='*60)
        
        tester = BPlusTreeFuzzTester(capacity=capacity)
        if not tester.run_fuzz_test(100000):  # 100k ops per capacity
            all_passed = False
            print(f"❌ FAILED with capacity {capacity}")
        else:
            print(f"✅ PASSED with capacity {capacity}")
    
    return all_passed


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            print("Running quick fuzz test...")
            success = run_quick_fuzz_test()
        elif sys.argv[1] == "varied":
            print("Running varied capacity tests...")
            success = run_varied_capacity_tests()
        else:
            print("Running full fuzz test...")
            success = run_full_fuzz_test()
    else:
        print("Running full fuzz test...")
        success = run_full_fuzz_test()
    
    sys.exit(0 if success else 1)