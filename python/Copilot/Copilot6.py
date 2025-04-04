class HashTable:
    """
    HashMap Data Type
    HashMap() Create a new, empty map. It returns an empty map collection.
    put(key, val) Add a new key-value pair to the map. If the key is already in the map then replace
                    the old value with the new value.
    get(key) Given a key, return the value stored in the map or None otherwise.
    del_(key) or del map[key] Delete the key-value pair from the map using a statement of the form del map[key].
    len() Return the number of key-value pairs stored in the map.
    in Return True for a statement of the form key in map, if the given key is in the map, False otherwise.
    """

    _empty = object()
    _deleted = object()

    def __init__(self, size=11):
        self.size = size
        self._len = 0
        self._keys = [self._empty] * size  # keys
        self._values = [self._empty] * size  # values

    def put(self, key, value):
        initial_hash = hash_ = self.hash(key)

        while True:
            if self._keys[hash_] in {self._empty, self._deleted}:
                self._keys[hash_] = key
                self._values[hash_] = value
                self._len += 1
                return
            elif self._keys[hash_] == key:
                self._values[hash_] = value
                return

            hash_ = self._rehash(hash_)
            if initial_hash == hash_:
                raise ValueError("Table is full")

    def get(self, key):
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
        return key % self.size

    def _rehash(self, old_hash):
        """
        Linear probing
        """
        return (old_hash + 1) % self.size

    def __getitem__(self, key):
        return self.get(key)

    def __delitem__(self, key):
        return self.del_(key)

    def __setitem__(self, key, value):
        self.put(key, value)

    def __len__(self):
        return self._len


class ResizableHashTable(HashTable):
    MIN_SIZE = 8

    def __init__(self):
        super().__init__(self.MIN_SIZE)

    def put(self, key, value):
        super().put(key, value)
        if len(self) >= (self.size * 2) / 3:
            self.__resize()

    def __resize(self):
        keys, values = self._keys, self._values
        self.size *= 2
        self._len = 0
        self._keys = [self._empty] * self.size
        self._values = [self._empty] * self.size
        for key, value in zip(keys, values):
            if key not in {self._empty, self._deleted}:
                self.put(key, value)