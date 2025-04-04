#!/usr/bin/env python3
from .hash_table import HashTable
from .number_theory.prime_numbers import check_prime, next_prime


class DoubleHash(HashTable):
    """
    Hash Table with open addressing and Double Hashing collision resolution.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _secondary_hash(self, value, data):
        """
        Calculates the secondary hash value used for double hashing.
        """
        primary_hash_remainder = value % self.size_table
        if not check_prime(primary_hash_remainder):
            secondary_prime = next_prime(primary_hash_remainder)
        else:
            secondary_prime = primary_hash_remainder

        return secondary_prime - (data % secondary_prime)

    def _double_hash(self, key, data, increment):
        """
        Calculates the double hash value based on the secondary hash and increment.
        """
        return (increment * self._secondary_hash(key, data)) % self.size_table

    def _collision_resolution(self, key, data=None):
        """
        Resolves hash collisions using double hashing.
        """
        increment = 1
        initial_hash = self.hash_function(data)
        current_hash = initial_hash

        while self.values[current_hash] is not None and self.values[current_hash] != key:
            if self.balanced_factor() >= self.lim_charge:
                current_hash = self._double_hash(key, data, increment)
                increment += 1
            else:
                return None #Indicate failure to resolve collision if load factor is low.

        return current_hash