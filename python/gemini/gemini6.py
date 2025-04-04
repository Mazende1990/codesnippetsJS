class HashTable(object):
    """
    HashMap Data Type.

    HashMap() Create a new, empty map. It returns an empty map collection.
    put(key, val) Add a new key-value pair to the map. If the key is already in the map,
                  replace the old value with the new value.
    get(key) Given a key, return the value stored in the map or None otherwise.
    del_(key) or del map[key] Delete the key-value pair from the map using del map[key].
    len() Return the number of key-value pairs stored in the map.
    in Return True for key in map, if the key is in the map, False otherwise.
    """

    _empty = object()
    _deleted = object()

    def __init__(self, size=11):
        """Initializes the HashTable with a given size."""
        self.size = size
        self._len = 0
        self._keys = [self._empty] * size  # keys
        self._values = [self._empty] * size  # values

    def put(self, key, value):
        """Adds or updates a key-value pair in the HashTable."""
        initial_hash = hash_ = self._hash(key)

        while True:
            if self._keys[hash_] is self._empty or self._keys[hash_] is self._deleted:
                # Can assign to hash_ index
                self._keys[hash_] = key
                self._values[hash_] = value
                self._len += 1
                return
            elif self._keys[hash_] == key:
                # Key already exists here, overwrite
                self._keys[hash_] = key
                self._values[hash_] = value
                return

            hash_ = self._rehash(hash_)

            if initial_hash == hash_:
                # Table is full
                raise ValueError("Table is full")

    def get(self, key):
        """Retrieves the value associated with a given key."""
        initial_hash = hash_ = self._hash(key)
        while True:
            if self._keys[hash_] is self._empty:
                # Key was never assigned
                return None
            elif self._keys[hash_] == key:
                # Key found
                return self._values[hash_]

            hash_ = self._rehash(hash_)
            if initial_hash == hash_:
                # Table is full and wrapped around
                return None

    def del_(self, key):
        """Deletes a key-value pair from the HashTable."""
        initial_hash = hash_ = self._hash(key)
        while True:
            if self._keys[hash_] is self._empty:
                # Key was never assigned
                return None
            elif self._keys[hash_] == key:
                # Key found, mark as deleted
                self._keys[hash_] = self._deleted
                self._values[hash_] = self._deleted
                self._len -= 1
                return

            hash_ = self._rehash(hash_)
            if initial_hash == hash_:
                # Table is full and wrapped around
                return None

    def _hash(self, key):
        """Calculates the hash value for a given key."""
        return key % self.size

    def _rehash(self, old_hash):
        """Calculates the next hash value for linear probing."""
        return (old_hash + 1) % self.size

    def __getitem__(self, key):
        """Enables dictionary-like access: map[key]."""
        return self.get(key)

    def __delitem__(self, key):
        """Enables dictionary-like deletion: del map[key]."""
        return self.del_(key)

    def __setitem__(self, key, value):
        """Enables dictionary-like assignment: map[key] = value."""
        self.put(key, value)

    def __len__(self):
        """Returns the number of key-value pairs in the HashTable."""
        return self._len


class ResizableHashTable(HashTable):
    """
    HashTable that automatically resizes when it reaches a certain load factor.
    """
    MIN_SIZE = 8

    def __init__(self):
        """Initializes ResizableHashTable with a minimum size."""
        super().__init__(self.MIN_SIZE)

    def put(self, key, value):
        """Adds or updates a key-value pair and resizes if necessary."""
        super().put(key, value)
        # Resize if filled >= 2/3 size (like python dict)
        if len(self) >= (self.size * 2) / 3:
            self._resize()

    def _resize(self):
        """Resizes the HashTable by doubling its size."""
        keys, values = self._keys, self._values
        self.size *= 2  # New size
        self._len = 0
        self._keys = [self._empty] * self.size
        self._values = [self._empty] * self.size
        for key, value in zip(keys, values):
            if key is not self._empty and key is not self._deleted:
                self.put(key, value)