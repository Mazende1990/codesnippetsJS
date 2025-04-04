class HashTable:
    """
    HashMap Data Type
    
    Operations:
    - HashTable(): Create a new, empty map
    - put(key, val): Add a new key-value pair to the map. If the key already exists, replace the old value
    - get(key): Return the value for the given key, or None if key doesn't exist
    - del_(key) or del map[key]: Delete the key-value pair from the map
    - len(): Return the number of key-value pairs stored in the map
    - key in map: Return True if the given key is in the map, False otherwise
    """

    # Sentinel objects to mark empty and deleted slots
    _EMPTY = object()
    _DELETED = object()

    def __init__(self, size=11):
        """Initialize a new hash table with the given size."""
        self.size = size
        self._len = 0
        self._keys = [self._EMPTY] * size
        self._values = [self._EMPTY] * size

    def put(self, key, value):
        """Add a key-value pair to the hash table."""
        initial_hash = current_hash = self._hash(key)

        while True:
            # Case 1: Empty or deleted slot available
            if self._keys[current_hash] is self._EMPTY or self._keys[current_hash] is self._DELETED:
                self._keys[current_hash] = key
                self._values[current_hash] = value
                self._len += 1
                return
            
            # Case 2: Key already exists, update value
            elif self._keys[current_hash] == key:
                self._values[current_hash] = value
                return

            # Collision: try next slot
            current_hash = self._rehash(current_hash)

            # Table is full if we've wrapped around to the initial hash
            if initial_hash == current_hash:
                raise ValueError("Hash table is full")

    def get(self, key):
        """Retrieve value for given key, or None if key doesn't exist."""
        initial_hash = current_hash = self._hash(key)
        
        while True:
            # Empty slot means key was never in the table
            if self._keys[current_hash] is self._EMPTY:
                return None
                
            # Key found, return corresponding value
            elif self._keys[current_hash] == key:
                return self._values[current_hash]

            # Check next slot
            current_hash = self._rehash(current_hash)
            
            # We've searched the entire table
            if initial_hash == current_hash:
                return None

    def del_(self, key):
        """Remove key-value pair from the hash table."""
        initial_hash = current_hash = self._hash(key)
        
        while True:
            # Empty slot means key was never in the table
            if self._keys[current_hash] is self._EMPTY:
                return None
                
            # Key found, mark as deleted
            elif self._keys[current_hash] == key:
                self._keys[current_hash] = self._DELETED
                self._values[current_hash] = self._DELETED
                self._len -= 1
                return

            # Check next slot
            current_hash = self._rehash(current_hash)
            
            # We've searched the entire table
            if initial_hash == current_hash:
                return None

    def _hash(self, key):
        """Primary hash function."""
        return key % self.size

    def _rehash(self, previous_hash):
        """Linear probing rehash function."""
        return (previous_hash + 1) % self.size

    # Dictionary-style interface
    def __getitem__(self, key):
        return self.get(key)

    def __delitem__(self, key):
        return self.del_(key)

    def __setitem__(self, key, value):
        self.put(key, value)

    def __len__(self):
        return self._len


class ResizableHashTable(HashTable):
    """
    A hash table that automatically resizes when it becomes too full.
    Doubles in size when the table is more than 2/3 full.
    """
    
    MIN_SIZE = 8

    def __init__(self):
        """Initialize with minimum size."""
        super().__init__(self.MIN_SIZE)

    def put(self, key, value):
        """
        Add a key-value pair, resizing the table if it becomes too full.
        """
        # Call parent class put method
        super().put(key, value)
        
        # Resize if load factor exceeds 2/3
        if len(self) >= (self.size * 2) / 3:
            self._resize()

    def _resize(self):
        """
        Double the size of the hash table and rehash all existing entries.
        """
        # Save current keys and values
        old_keys, old_values = self._keys, self._values
        
        # Double the size and reset the table
        self.size *= 2
        self._len = 0
        self._keys = [self._EMPTY] * self.size
        self._values = [self._EMPTY] * self.size
        
        # Reinsert all non-empty, non-deleted entries
        for key, value in zip(old_keys, old_values):
            if key is not self._EMPTY and key is not self._DELETED:
                self.put(key, value)