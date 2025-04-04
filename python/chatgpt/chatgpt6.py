class HashTable:
    """
    Basic HashMap implementation using open addressing and linear probing.

    Methods:
        - put(key, val): Add or update a key-value pair.
        - get(key): Retrieve the value for a given key, or None if not found.
        - del_(key): Delete a key-value pair by key.
        - __len__(): Return number of key-value pairs.
        - __contains__(key): Check if a key exists in the table.
    """

    _empty = object()
    _deleted = object()

    def __init__(self, size=11):
        self.size = size
        self._len = 0
        self._keys = [self._empty] * size
        self._values = [self._empty] * size

    def put(self, key, value):
        """
        Insert or update the key-value pair in the hash table.
        """
        initial_hash = hash_ = self.hash(key)

        while True:
            slot = self._keys[hash_]
            if slot is self._empty or slot is self._deleted:
                self._keys[hash_] = key
                self._values[hash_] = value
                self._len += 1
                return
            elif slot == key:
                self._values[hash_] = value
                return

            hash_ = self._rehash(hash_)
            if hash_ == initial_hash:
                raise ValueError("Hash table is full")

    def get(self, key):
        """
        Retrieve the value for the given key, or None if not found.
        """
        initial_hash = hash_ = self.hash(key)

        while True:
            slot = self._keys[hash_]
            if slot is self._empty:
                return None
            elif slot == key:
                return self._values[hash_]

            hash_ = self._rehash(hash_)
            if hash_ == initial_hash:
                return None

    def del_(self, key):
        """
        Remove the key-value pair associated with the key.
        """
        initial_hash = hash_ = self.hash(key)

        while True:
            slot = self._keys[hash_]
            if slot is self._empty:
                return None
            elif slot == key:
                self._keys[hash_] = self._deleted
                self._values[hash_] = self._deleted
                self._len -= 1
                return

            hash_ = self._rehash(hash_)
            if hash_ == initial_hash:
                return None

    def hash(self, key):
        """
        Hash function based on modulo size of the table.
        """
        return key % self.size

    def _rehash(self, old_hash):
        """
        Linear probing rehashing strategy.
        """
        return (old_hash + 1) % self.size

    # Python standard method support
    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.put(key, value)

    def __delitem__(self, key):
        self.del_(key)

    def __len__(self):
        return self._len

    def __contains__(self, key):
        return self.get(key) is not None


class ResizableHashTable(HashTable):
    """
    HashTable that automatically resizes when it reaches 2/3 capacity.
    Mimics Python's built-in dictionary behavior.
    """

    MIN_SIZE = 8

    def __init__(self):
        super().__init__(self.MIN_SIZE)

    def put(self, key, value):
        super().put(key, value)
        if len(self) >= (self.size * 2) // 3:
            self._resize()

    def _resize(self):
        """
        Double the table size and rehash all existing keys.
        """
        old_keys = self._keys
        old_values = self._values

        self.size *= 2
        self._len = 0
        self._keys = [self._empty] * self.size
        self._values = [self._empty] * self.size

        for key, value in zip(old_keys, old_values):
            if key not in (self._empty, self._deleted):
                self.put(key, value)
