class HashTable:
    """
    A hash table implementation with open addressing and linear probing for collision resolution.

    Attributes:
        _empty: Sentinel value for empty slots
        _deleted: Sentinel value for deleted slots
        size: Current capacity of the hash table
        _len: Number of key-value pairs stored
        _keys: List storing keys
        _values: List storing corresponding values

    Methods:
        put(key, value): Insert or update a key-value pair
        get(key): Retrieve a value by key
        del_(key): Remove a key-value pair
        hash(key): Compute hash value for a key
        _rehash(old_hash): Compute new hash for probing
    """

    _empty = object()
    _deleted = object()

    def __init__(self, size=11):
        """Initialize hash table with given size (default 11)."""
        if not isinstance(size, int) or size <= 0:
            raise ValueError("Size must be a positive integer")
        
        self.size = size
        self._len = 0
        self._keys = [self._empty] * size
        self._values = [self._empty] * size

    def put(self, key, value):
        """
        Insert or update a key-value pair in the hash table.
        
        Args:
            key: The key to insert/update
            value: The value to associate with the key
            
        Raises:
            ValueError: If table is full
        """
        if self._len >= self.size:
            raise ValueError("Table is full")

        initial_hash = hash_ = self.hash(key)

        while True:
            if self._keys[hash_] in (self._empty, self._deleted):
                # Found empty or deleted slot
                self._keys[hash_] = key
                self._values[hash_] = value
                self._len += 1
                return
            elif self._keys[hash_] == key:
                # Key exists - update value
                self._values[hash_] = value
                return

            hash_ = self._rehash(hash_)
            if initial_hash == hash_:
                raise ValueError("Table is full")

    def get(self, key):
        """
        Retrieve the value associated with a key.
        
        Args:
            key: The key to look up
            
        Returns:
            The associated value or None if key not found
        """
        initial_hash = hash_ = self.hash(key)
        
        while True:
            if self._keys[hash_] is self._empty:
                return None
            elif self._keys[hash_] == key:
                return self._values[hash_]

            hash_ = self._rehash(hash_)
            if initial_hash == hash_:
                return None

    def del_(self, key):
        """
        Remove a key-value pair from the hash table.
        
        Args:
            key: The key to remove
            
        Returns:
            None (always returns None, even if key not found)
        """
        initial_hash = hash_ = self.hash(key)
        
        while True:
            if self._keys[hash_] is self._empty:
                return None
            elif self._keys[hash_] == key:
                self._keys[hash_] = self._deleted
                self._values[hash_] = self._deleted
                self._len -= 1
                return

            hash_ = self._rehash(hash_)
            if initial_hash == hash_:
                return None

    def hash(self, key):
        """Compute hash value for a key using modulo operation."""
        if not isinstance(key, int):
            raise TypeError("Keys must be integers")
        return key % self.size

    def _rehash(self, old_hash):
        """Compute new hash using linear probing."""
        return (old_hash + 1) % self.size

    # Magic methods for Pythonic interface
    def __getitem__(self, key):
        return self.get(key)

    def __delitem__(self, key):
        return self.del_(key)

    def __setitem__(self, key, value):
        self.put(key, value)

    def __len__(self):
        return self._len

    def __contains__(self, key):
        return self.get(key) is not None

    def __repr__(self):
        items = []
        for k, v in zip(self._keys, self._values):
            if k not in (self._empty, self._deleted):
                items.append(f"{k}: {v}")
        return "{" + ", ".join(items) + "}"


class ResizableHashTable(HashTable):
    """
    A hash table that automatically resizes when load factor exceeds 2/3.
    
    Inherits from HashTable and overrides put() to implement resizing.
    """
    
    MIN_SIZE = 8
    LOAD_FACTOR = 2/3

    def __init__(self):
        """Initialize with minimum size."""
        super().__init__(self.MIN_SIZE)

    def put(self, key, value):
        """
        Insert key-value pair and resize if needed.
        
        Args:
            key: The key to insert
            value: The value to associate with key
        """
        super().put(key, value)
        if len(self) >= self.size * self.LOAD_FACTOR:
            self._resize()

    def _resize(self):
        """
        Double the size of the hash table and rehash all items.
        """
        old_keys = self._keys
        old_values = self._values
        
        self.size *= 2
        self._len = 0
        self._keys = [self._empty] * self.size
        self._values = [self._empty] * self.size
        
        for key, value in zip(old_keys, old_values):
            if key not in (self._empty, self._deleted):
                super().put(key, value)