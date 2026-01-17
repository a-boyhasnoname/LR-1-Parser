"""
items.py - LR(1) Item and ItemSet classes for LR(1) Parser
"""
class LR1Item:
    """
    Represents an LR(1) item: [A → α·β, a]
    
    An LR(1) item consists of:
    - A production (A → αβ)
    - A dot position indicating how much has been recognized
    - A lookahead symbol
    """
    
    def __init__(self, production, dot_pos, lookahead):
        """
        Initialize an LR(1) item.
        
        Args:
            production: Production object
            dot_pos: Position of the dot (0 to len(rhs))
            lookahead: Lookahead terminal symbol
        """
        self.lhs = production.lhs
        self.rhs = production.rhs
        self.dot_pos = dot_pos
        self.lookahead = lookahead
        self.production = production
    
    def next_symbol(self):
        """
        Return the symbol immediately after the dot.
        
        Returns:
            The symbol after the dot, or None if dot is at end
        """
        if self.dot_pos < len(self.rhs):
            return self.rhs[self.dot_pos]
        return None
    
    def advance(self):
        """
        Create a new item with the dot advanced by one position.
        
        Returns:
            New LR1Item with dot moved one position to the right
        """
        return LR1Item(self.production, self.dot_pos + 1, self.lookahead)
    
    def is_complete(self):
        """
        Check if this is a complete item (dot at the end).
        
        Returns:
            True if dot is at the end (reduce item), False otherwise
        """
        return self.dot_pos >= len(self.rhs)
    
    def __str__(self):
        """String representation of the item."""
        rhs_before = ' '.join(self.rhs[:self.dot_pos])
        rhs_after = ' '.join(self.rhs[self.dot_pos:])
        
        if not self.rhs:
            # Empty production
            return f"[{self.lhs} → ·, {self.lookahead}]"
        
        if rhs_before and rhs_after:
            return f"[{self.lhs} → {rhs_before} · {rhs_after}, {self.lookahead}]"
        elif rhs_before:
            # Dot at end
            return f"[{self.lhs} → {rhs_before} ·, {self.lookahead}]"
        else:
            # Dot at beginning
            return f"[{self.lhs} → · {rhs_after}, {self.lookahead}]"
    
    def __repr__(self):
        """Official string representation."""
        return self.__str__()
    
    def __eq__(self, other):
        """Check equality of two items."""
        return isinstance(other, LR1Item) and \
               self.lhs == other.lhs and \
               self.rhs == other.rhs and \
               self.dot_pos == other.dot_pos and \
               self.lookahead == other.lookahead
    
    def __hash__(self):
        """Hash function for using items in sets and dicts."""
        return hash((self.lhs, tuple(self.rhs), self.dot_pos, self.lookahead))


class ItemSet:
    """
    Represents a set of LR(1) items (a state in the LR(1) automaton).
    """
    
    def __init__(self, items=None):
        """
        Initialize an item set.
        
        Args:
            items: Initial collection of items (optional)
        """
        self.items = set(items) if items else set()
    
    def add(self, item):
        """
        Add an item to the set.
        
        Args:
            item: LR1Item to add
        """
        self.items.add(item)
    
    def __iter__(self):
        """Make the set iterable."""
        return iter(self.items)
    
    def __len__(self):
        """Return the number of items in the set."""
        return len(self.items)
    
    def __eq__(self, other):
        """Check equality of two item sets."""
        return isinstance(other, ItemSet) and self.items == other.items
    
    def __hash__(self):
        """Hash function for using item sets in sets and dicts."""
        return hash(frozenset(self.items))
    
    def __str__(self):
        """String representation showing all items."""
        return '\n'.join(str(item) for item in sorted(self.items, key=str))
    
    def __repr__(self):
        """Official string representation."""
        return self.__str__()