"""
Memory pool allocation for B+ Tree nodes.

This module provides object pooling to reduce allocation/deallocation overhead
and improve cache locality by reusing node objects.
"""

from typing import List, Optional, Any
from threading import Lock


class NodePool:
    """Memory pool for B+ Tree node objects to reduce allocation overhead"""
    
    def __init__(self, capacity: int, max_pool_size: int = 100):
        """
        Initialize node pool with given capacity.
        
        Args:
            capacity: Node capacity for pooled nodes
            max_pool_size: Maximum number of nodes to keep in pool
        """
        self.capacity = capacity
        self.max_pool_size = max_pool_size
        
        # Separate pools for leaf and branch nodes
        self.leaf_pool: List['LeafNode'] = []
        self.branch_pool: List['BranchNode'] = []
        
        # Thread safety for concurrent access
        self._lock = Lock()
        
        # Statistics for monitoring pool effectiveness
        self.stats = {
            'leaf_requests': 0,
            'leaf_hits': 0,
            'leaf_returns': 0,
            'branch_requests': 0,
            'branch_hits': 0,
            'branch_returns': 0,
            'peak_leaf_pool_size': 0,
            'peak_branch_pool_size': 0
        }
    
    def get_leaf_node(self) -> 'LeafNode':
        """Get a leaf node from pool or create new one"""
        with self._lock:
            self.stats['leaf_requests'] += 1
            
            if self.leaf_pool:
                node = self.leaf_pool.pop()
                node._reset_for_reuse()
                self.stats['leaf_hits'] += 1
                return node
            
            # Create new node if pool is empty
            from bplus_tree import LeafNode  # Import here to avoid circular dependency
            return LeafNode(self.capacity)
    
    def get_branch_node(self) -> 'BranchNode':
        """Get a branch node from pool or create new one"""
        with self._lock:
            self.stats['branch_requests'] += 1
            
            if self.branch_pool:
                node = self.branch_pool.pop()
                node._reset_for_reuse()
                self.stats['branch_hits'] += 1
                return node
            
            # Create new node if pool is empty
            from bplus_tree import BranchNode  # Import here to avoid circular dependency
            return BranchNode(self.capacity)
    
    def return_leaf_node(self, node: 'LeafNode') -> None:
        """Return a leaf node to the pool for reuse"""
        if node.capacity != self.capacity:
            return  # Don't pool nodes with different capacity
        
        with self._lock:
            if len(self.leaf_pool) < self.max_pool_size:
                self.leaf_pool.append(node)
                self.stats['leaf_returns'] += 1
                
                # Update peak size tracking
                if len(self.leaf_pool) > self.stats['peak_leaf_pool_size']:
                    self.stats['peak_leaf_pool_size'] = len(self.leaf_pool)
    
    def return_branch_node(self, node: 'BranchNode') -> None:
        """Return a branch node to the pool for reuse"""
        if node.capacity != self.capacity:
            return  # Don't pool nodes with different capacity
        
        with self._lock:
            if len(self.branch_pool) < self.max_pool_size:
                self.branch_pool.append(node)
                self.stats['branch_returns'] += 1
                
                # Update peak size tracking
                if len(self.branch_pool) > self.stats['peak_branch_pool_size']:
                    self.stats['peak_branch_pool_size'] = len(self.branch_pool)
    
    def get_hit_rate(self) -> dict:
        """Calculate pool hit rates for performance monitoring"""
        with self._lock:
            leaf_hit_rate = (self.stats['leaf_hits'] / self.stats['leaf_requests'] 
                           if self.stats['leaf_requests'] > 0 else 0.0)
            branch_hit_rate = (self.stats['branch_hits'] / self.stats['branch_requests'] 
                             if self.stats['branch_requests'] > 0 else 0.0)
            
            return {
                'leaf_hit_rate': leaf_hit_rate,
                'branch_hit_rate': branch_hit_rate,
                'leaf_pool_size': len(self.leaf_pool),
                'branch_pool_size': len(self.branch_pool),
                'stats': self.stats.copy()
            }
    
    def clear(self) -> None:
        """Clear all pooled nodes and reset statistics"""
        with self._lock:
            self.leaf_pool.clear()
            self.branch_pool.clear()
            self.stats = {key: 0 for key in self.stats}
    
    def pre_allocate(self, leaf_count: int = 10, branch_count: int = 5) -> None:
        """Pre-allocate nodes in the pool for better performance"""
        from bplus_tree import LeafNode, BranchNode
        
        with self._lock:
            # Pre-allocate leaf nodes
            for _ in range(min(leaf_count, self.max_pool_size - len(self.leaf_pool))):
                node = LeafNode(self.capacity)
                node._reset_for_reuse()
                self.leaf_pool.append(node)
            
            # Pre-allocate branch nodes
            for _ in range(min(branch_count, self.max_pool_size - len(self.branch_pool))):
                node = BranchNode(self.capacity)
                node._reset_for_reuse()
                self.branch_pool.append(node)


# Global pool instance for default use
_default_pool: Optional[NodePool] = None


def get_default_pool(capacity: int = 128) -> NodePool:
    """Get or create the default global node pool"""
    global _default_pool
    if _default_pool is None or _default_pool.capacity != capacity:
        _default_pool = NodePool(capacity)
    return _default_pool


def set_default_pool(pool: NodePool) -> None:
    """Set the default global node pool"""
    global _default_pool
    _default_pool = pool


def clear_default_pool() -> None:
    """Clear the default global node pool"""
    global _default_pool
    if _default_pool:
        _default_pool.clear()


def get_pool_stats() -> dict:
    """Get statistics for the default pool"""
    if _default_pool:
        return _default_pool.get_hit_rate()
    return {}